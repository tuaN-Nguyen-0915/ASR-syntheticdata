# meddies_tts/plan.py
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq

from meddies_tts.config import Config
from meddies_tts.reject import check
from meddies_tts.speakers import Speaker, derive_seed, get_assigner
from meddies_tts.textprep import get_normalizer
from meddies_tts.vietnamese_numbers import dialect_from_seed

# Namespaces shard ids per config so planning one language never renumbers another.
CONFIG_PREFIX = {"vietnamese": "vi", "english": "en"}

PLAN_SCHEMA = pa.schema(
    [
        pa.field("config", pa.string()),
        pa.field("disease_slug", pa.string()),
        pa.field("disease_name", pa.string()),
        pa.field("conv_id", pa.string()),
        pa.field("turn", pa.int32()),
        pa.field("role", pa.string()),
        pa.field("text_raw", pa.string()),
        pa.field("text_spoken", pa.string()),
        pa.field("speaker_id", pa.string()),
        pa.field("speaker_source", pa.string()),
        pa.field("speaker_emotions", pa.string()),
        pa.field("speaker_gender", pa.string()),
        pa.field("speaker_unique_source_s", pa.float32()),
        pa.field("shard_id", pa.string()),
        pa.field("audio_path", pa.string()),
    ]
)


def shard_id(config: str, index: int) -> str:
    """Build the namespaced, zero-padded shard id for a config and shard index."""
    if config not in CONFIG_PREFIX:
        raise ValueError(f"no shard prefix registered for config {config!r}")
    return f"{CONFIG_PREFIX[config]}-{index:05d}"


def shard_repo_path(config: str, index: int, total: int) -> str:
    """Build the HF-convention Parquet path for one shard within a config's dataset."""
    return f"data/{config}/train-{index:05d}-of-{total:05d}.parquet"


def audio_path(config: str, disease_slug: str, conv_id: str, turn: int, role: str) -> str:
    """Build the output-tree-relative path where a synthesized utterance's audio lives."""
    return f"{config}/{disease_slug}/{conv_id}/Turn{turn}/{role}.flac"


def build_plan(
    manifest: pa.Table,
    cfg: Config,
    pool: list[Speaker],
    normalizers: dict[tuple[str, str], object] | None = None,
) -> tuple[pa.Table, list[dict]]:
    """Normalize, reject, assign speakers and pack conversations into shards."""
    by_id = {speaker.speaker_id: speaker for speaker in pool}
    assigner = get_assigner(cfg.speaker, pool)
    # Normalizers are cached per (config, speaker_id), not per config, because
    # dialect is a property of the speaker (see the ordering note below).
    # A caller-supplied dict (test injection point) seeds/overrides this cache.
    cache: dict[tuple[str, str], object] = dict(normalizers or {})

    kept: list[dict] = []
    rejects: list[dict] = []
    for row in manifest.to_pylist():
        config = row["config"]
        if config not in cfg.run.configs:
            continue
        path = audio_path(config, row["disease_slug"], row["conv_id"], row["turn"], row["role"])
        rejection = check(row["text_raw"], cfg.text)
        if rejection is not None:
            rejects.append(
                {
                    "audio_path": path,
                    "reason": rejection.reason,
                    "detail": rejection.detail,
                    "text_raw": row["text_raw"],
                }
            )
            continue
        # Speaker assignment MUST happen before normalization. Vietnamese number
        # words vary by dialect (linh/nghìn vs lẻ/ngàn, tư vs bốn), and each
        # speaker is pinned to one dialect derived from their speaker_id. If we
        # normalized first we'd have to pick a single dialect for the whole
        # corpus, discarding the per-speaker variation the corpus wants.
        speaker_id = assigner.assign(
            config, row["disease_slug"], row["conv_id"], row["turn"], row["role"]
        )
        speaker = by_id[speaker_id]

        key = (config, speaker_id)
        if key not in cache:
            # Dialect is derived deterministically from the speaker id (plus the
            # run's salt), so the same speaker always gets the same dialect.
            dialect = dialect_from_seed(
                derive_seed(cfg.speaker.seed_salt, "dialect", speaker_id)
            )
            cache[key] = get_normalizer(config, dialect)
        spoken = cache[key].normalize(row["text_raw"])
        if not spoken:
            # Normalization can legitimately reduce text to nothing (e.g. an
            # utterance that was pure markup/reasoning leakage); that utterance
            # is dropped like any other rejection, not synthesized as silence.
            rejects.append(
                {
                    "audio_path": path,
                    "reason": "empty_after_normalization",
                    "detail": f"{len(row['text_raw'])} raw chars normalized to nothing",
                    "text_raw": row["text_raw"],
                }
            )
            continue
        kept.append(
            {
                **row,
                "text_spoken": spoken,
                "speaker_id": speaker_id,
                "speaker_source": cfg.refs.source,
                "speaker_emotions": speaker.emotions,
                "speaker_gender": speaker.gender,
                "speaker_unique_source_s": speaker.unique_source_s,
                "audio_path": path,
                "shard_id": "",  # filled in by _assign_shards below
            }
        )

    _assign_shards(kept, cfg.run.convs_per_shard)
    columns = {name: [row[name] for row in kept] for name in PLAN_SCHEMA.names}
    return pa.Table.from_pydict(columns, schema=PLAN_SCHEMA), rejects


def _assign_shards(rows: list[dict], convs_per_shard: int) -> None:
    """Stamp shard_id in place; conversations are packed whole, in sorted order."""
    # Collect the distinct (config, disease_slug, conv_id) conversations per
    # config -- packing operates on whole conversations, never individual rows,
    # so a conversation is never split across two shards.
    by_config: dict[str, set[tuple[str, str, str]]] = {}
    for row in rows:
        key = (row["config"], row["disease_slug"], row["conv_id"])
        by_config.setdefault(row["config"], set()).add(key)

    index_of: dict[tuple[str, str, str], str] = {}
    for config, keys in by_config.items():
        # Sorting before packing makes the assignment deterministic regardless
        # of row order in the input manifest.
        for position, key in enumerate(sorted(keys)):
            index_of[key] = shard_id(config, position // convs_per_shard)

    for row in rows:
        row["shard_id"] = index_of[(row["config"], row["disease_slug"], row["conv_id"])]


def shard_totals(plan: pa.Table) -> dict[str, int]:
    """Count distinct shard ids per config in a plan."""
    totals: dict[str, set[str]] = {}
    for config, sid in zip(
        plan.column("config").to_pylist(), plan.column("shard_id").to_pylist()
    ):
        totals.setdefault(config, set()).add(sid)
    return {config: len(ids) for config, ids in totals.items()}


def compute_plan_hash(plan: pa.Table, cfg: Config, config: str) -> str:
    """Hash one config's slice of the plan: everything that determines its audio.

    Per-config, not per-plan-file: drift is checked per config (see
    hub.check_plan_drift), so a single hash spanning every config in the plan
    would trip PlanDriftError for an untouched Vietnamese config the moment an
    unrelated config (e.g. English) is added to the run. Planning ["vietnamese"]
    alone and ["vietnamese", "english"] together over the same conversations
    must yield the identical vietnamese hash -- so nothing here may depend on
    which OTHER configs are in the plan, only on this config's own rows and cfg.

    Includes a digest of the full text_spoken column (hashed, not embedded raw,
    to keep the payload cheap) plus every text.*/engine.* field the Task 17 pilot
    sweeps and that changes what the audio sounds like: chunk_target_seconds,
    chars_per_sec, silence_ms, cfg_value, temperature, inference_timesteps.
    Hashing text_spoken directly makes a hand-maintained NORMALIZER_VERSION
    constant redundant -- any normalizer change that alters output text already
    changes text_spoken, and therefore this hash, with no extra bookkeeping. (A
    prior version of this function relied on such a constant; it has been removed.)

    Deliberately EXCLUDES hf.repo_id (retargeting where the dataset gets
    published must not invalidate a plan or orphan already-finished shards) and
    engine.concurrency/max_num_seqs (throughput knobs with no effect on the
    generated audio).
    """
    subset = plan.filter(pc.equal(plan.column("config"), config))
    # Joined with a NUL separator (never appears in corpus text) so concatenation
    # can't collide across a row boundary, e.g. ("ab","c") vs ("a","bc").
    text_blob = "\x00".join(subset.column("text_spoken").to_pylist()).encode("utf-8")
    text_spoken_digest = hashlib.blake2b(text_blob, digest_size=16).hexdigest()
    payload = {
        "config": config,
        "text_spoken_digest": text_spoken_digest,
        "speaker_policy": cfg.speaker.policy,
        "speaker_pool": cfg.speaker.pool,
        "seed_salt": cfg.speaker.seed_salt,
        "convs_per_shard": cfg.run.convs_per_shard,
        "text_chunk_target_seconds": cfg.text.chunk_target_seconds,
        "text_chars_per_sec": cfg.text.chars_per_sec,
        "text_silence_ms": cfg.text.silence_ms,
        "engine_cfg_value": cfg.engine.cfg_value,
        "engine_temperature": cfg.engine.temperature,
        "engine_inference_timesteps": cfg.engine.inference_timesteps,
        "rows": [
            [row["audio_path"], row["speaker_id"], row["shard_id"]]
            for row in subset.select(["audio_path", "speaker_id", "shard_id"]).to_pylist()
        ],
    }
    # sort_keys makes the JSON serialization (and thus the hash) independent of
    # dict insertion order, so the same logical plan always hashes identically.
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.blake2b(blob, digest_size=16).hexdigest()


def write_plan(plan: pa.Table, path: Path) -> None:
    """Write a plan table to Parquet with zstd compression."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(plan, path, compression="zstd")


def read_plan(path: Path) -> pa.Table:
    """Read a plan table from Parquet."""
    return pq.read_table(path)
