from __future__ import annotations

from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
from datasets import Audio, Features, Value

from meddies_tts.audio import TARGET_SAMPLE_RATE

FEATURES = Features(
    {
        "config": Value("string"),
        "disease_slug": Value("string"),
        "disease_name": Value("string"),
        "conv_id": Value("string"),
        "turn": Value("int32"),
        "role": Value("string"),
        "text_raw": Value("string"),
        "text_spoken": Value("string"),
        "speaker_id": Value("int32"),
        "speaker_emotions": Value("string"),
        "speaker_unique_source_s": Value("float32"),
        "audio": Audio(sampling_rate=TARGET_SAMPLE_RATE),
        "duration_s": Value("float32"),
        "n_chunks": Value("int32"),
        "seed": Value("int64"),
        "engine_version": Value("string"),
    }
)

_PLANNING_ONLY = ("shard_id", "audio_path")


def build_row(
    plan_row: dict,
    flac_bytes: bytes,
    duration_s: float,
    n_chunks: int,
    seed: int,
    engine_version: str,
) -> dict:
    """Turn a plan row plus generated audio into a published dataset row."""
    row = {key: value for key, value in plan_row.items() if key not in _PLANNING_ONLY}
    # audio_path is dropped as a top-level column but survives as the audio struct's
    # "path", preserving the original directory layout in the published dataset.
    row["audio"] = {"bytes": flac_bytes, "path": plan_row["audio_path"]}
    row["duration_s"] = duration_s
    row["n_chunks"] = n_chunks
    row["seed"] = seed
    row["engine_version"] = engine_version
    return row


def write_shard(rows: list[dict], path: Path, plan_hash: str, config_json: str) -> None:
    """Write one shard, embedding plan_hash and resolved config as file metadata."""
    if not rows:
        raise ValueError("write_shard received no rows")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Build the Arrow table directly from FEATURES.arrow_schema rather than going
    # through Dataset.from_list(). Our rows already carry the audio column in its
    # raw on-disk shape ({"bytes": ..., "path": ...}), which is exactly what the
    # Audio feature stores -- from_list's per-row encode_example() step exists to
    # transcode arrays/paths into that shape, and (in current `datasets` releases)
    # unconditionally imports torch/torchcodec to do so, even when nothing actually
    # needs transcoding. Building the table ourselves skips that needless encode step.
    # FEATURES.arrow_schema already carries the b"huggingface" metadata that declares
    # the audio column as an Audio feature at TARGET_SAMPLE_RATE -- that's what keeps
    # the published dataset's audio decodable instead of degrading to raw bytes.
    table = pa.Table.from_pylist(rows, schema=FEATURES.arrow_schema)
    # Extend (never replace) that existing metadata with our own provenance keys.
    metadata = dict(table.schema.metadata or {})
    metadata[b"plan_hash"] = plan_hash.encode("utf-8")
    metadata[b"config_json"] = config_json.encode("utf-8")
    pq.write_table(table.replace_schema_metadata(metadata), path, compression="zstd")
