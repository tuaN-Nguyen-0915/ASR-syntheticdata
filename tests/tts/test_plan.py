import pyarrow as pa
import pytest

from meddies_tts.config import Config, HFConfig, RunConfig, TextConfig
from meddies_tts.manifest import MANIFEST_SCHEMA
from meddies_tts.plan import (
    PLAN_SCHEMA,
    audio_path,
    build_plan,
    compute_plan_hash,
    read_plan,
    shard_id,
    shard_repo_path,
    shard_totals,
    write_plan,
)
from meddies_tts.speakers import Speaker


def _cfg(**run_kwargs):
    return Config(hf=HFConfig(repo_id="Meddies/SynthAudio"), run=RunConfig(**run_kwargs))


def _pool(n=6):
    return [
        Speaker(str(i), f"/refs/speaker_{i:03d}.wav", "neutral", 100.0 + i, 12.0)
        for i in range(n)
    ]


def _manifest(n_convs=5, n_turns=2, text="Xin chào bác sĩ."):
    rows = []
    for c in range(n_convs):
        for t in range(1, n_turns + 1):
            for role in ("assistant", "user"):
                rows.append(
                    {
                        "config": "vietnamese",
                        "disease_slug": "suy_gan",
                        "disease_name": "Suy gan",
                        "conv_id": f"conv_{c:04d}",
                        "turn": t,
                        "role": role,
                        "text_raw": text,
                    }
                )
    columns = {name: [r[name] for r in rows] for name in MANIFEST_SCHEMA.names}
    return pa.Table.from_pydict(columns, schema=MANIFEST_SCHEMA)


_IDENTITY = type("N", (), {"normalize": staticmethod(lambda t: t)})()
# keyed by (config, speaker_id) - the dialect follows the speaker
_NORMALIZERS = {("vietnamese", sid): _IDENTITY for sid in map(str, range(6))}


def test_shard_id_is_prefixed_and_zero_padded():
    assert shard_id("vietnamese", 0) == "vi-00000"
    assert shard_id("english", 42) == "en-00042"


def test_shard_id_rejects_unknown_config():
    with pytest.raises(ValueError, match="klingon"):
        shard_id("klingon", 0)


def test_shard_repo_path_follows_hf_convention():
    assert shard_repo_path("vietnamese", 0, 473) == (
        "data/vietnamese/train-00000-of-00473.parquet"
    )


def test_audio_path_mirrors_the_output_full_tree():
    assert audio_path("vietnamese", "suy_gan", "conv_0001", 3, "user") == (
        "vietnamese/suy_gan/conv_0001/Turn3/user.flac"
    )


def test_plan_schema_matches(tmp_path):
    plan, _ = build_plan(_manifest(), _cfg(), _pool(), _NORMALIZERS)
    assert plan.schema.equals(PLAN_SCHEMA)


def test_plan_keeps_every_accepted_utterance():
    plan, rejects = build_plan(_manifest(n_convs=3, n_turns=2), _cfg(), _pool(), _NORMALIZERS)
    assert plan.num_rows == 3 * 2 * 2
    assert rejects == []


def test_degenerate_rows_are_rejected_not_planned():
    manifest = _manifest(n_convs=2, n_turns=1, text="x" * 5000)
    plan, rejects = build_plan(manifest, _cfg(), _pool(), _NORMALIZERS)
    assert plan.num_rows == 0
    assert len(rejects) == 4
    assert rejects[0]["reason"] == "too_long"
    assert rejects[0]["audio_path"].endswith(".flac")


def test_conversation_is_never_split_across_shards():
    plan, _ = build_plan(_manifest(n_convs=10), _cfg(convs_per_shard=3), _pool(), _NORMALIZERS)
    rows = plan.to_pylist()
    by_conv = {}
    for row in rows:
        by_conv.setdefault(row["conv_id"], set()).add(row["shard_id"])
    assert all(len(shards) == 1 for shards in by_conv.values())


def test_shards_respect_convs_per_shard():
    plan, _ = build_plan(_manifest(n_convs=10), _cfg(convs_per_shard=3), _pool(), _NORMALIZERS)
    rows = plan.to_pylist()
    per_shard = {}
    for row in rows:
        per_shard.setdefault(row["shard_id"], set()).add(row["conv_id"])
    assert sorted(len(v) for v in per_shard.values()) == [1, 3, 3, 3]


def test_shard_totals_counts_distinct_shards_per_config():
    plan, _ = build_plan(_manifest(n_convs=10), _cfg(convs_per_shard=3), _pool(), _NORMALIZERS)
    assert shard_totals(plan) == {"vietnamese": 4}


def test_speaker_is_constant_within_a_conversation_for_a_role():
    plan, _ = build_plan(_manifest(n_convs=2, n_turns=4), _cfg(), _pool(), _NORMALIZERS)
    rows = [r for r in plan.to_pylist() if r["conv_id"] == "conv_0000" and r["role"] == "user"]
    assert len({r["speaker_id"] for r in rows}) == 1


def test_speaker_metadata_columns_are_populated():
    plan, _ = build_plan(_manifest(n_convs=1), _cfg(), _pool(), _NORMALIZERS)
    row = plan.to_pylist()[0]
    assert row["speaker_emotions"] == "neutral"
    assert row["speaker_unique_source_s"] >= 100.0


def test_text_spoken_comes_from_the_normalizer():
    upper = type("N", (), {"normalize": staticmethod(str.upper)})()
    shouty = {("vietnamese", sid): upper for sid in map(str, range(6))}
    plan, _ = build_plan(_manifest(n_convs=1, n_turns=1), _cfg(), _pool(), shouty)
    row = plan.to_pylist()[0]
    assert row["text_raw"] == "Xin chào bác sĩ."
    assert row["text_spoken"] == "XIN CHÀO BÁC SĨ."


def test_dialect_follows_the_speaker():
    # Two speakers with different dialects must produce different text for the
    # same input, and the same speaker must always produce the same text.
    manifest = _manifest(n_convs=30, n_turns=1, text="Uống 1005 ml mỗi ngày.")
    plan, _ = build_plan(manifest, _cfg(), _pool(), None)
    rows = plan.to_pylist()
    by_speaker = {}
    for row in rows:
        by_speaker.setdefault(row["speaker_id"], set()).add(row["text_spoken"])
    assert all(len(v) == 1 for v in by_speaker.values())      # stable per speaker
    assert len({next(iter(v)) for v in by_speaker.values()}) > 1  # differs across speakers


def test_build_plan_is_deterministic():
    first, _ = build_plan(_manifest(n_convs=6), _cfg(), _pool(), _NORMALIZERS)
    second, _ = build_plan(_manifest(n_convs=6), _cfg(), _pool(), _NORMALIZERS)
    assert first.to_pylist() == second.to_pylist()


def test_plan_hash_is_stable_for_identical_inputs():
    cfg = _cfg()
    plan, _ = build_plan(_manifest(n_convs=4), cfg, _pool(), _NORMALIZERS)
    assert compute_plan_hash(plan, cfg, "vietnamese") == compute_plan_hash(plan, cfg, "vietnamese")


def test_plan_hash_changes_when_salt_changes():
    from dataclasses import replace

    from meddies_tts.config import SpeakerConfig

    cfg_a = _cfg()
    cfg_b = replace(cfg_a, speaker=SpeakerConfig(seed_salt="v2"))
    plan_a, _ = build_plan(_manifest(n_convs=4), cfg_a, _pool(), _NORMALIZERS)
    plan_b, _ = build_plan(_manifest(n_convs=4), cfg_b, _pool(), _NORMALIZERS)
    assert compute_plan_hash(plan_a, cfg_a, "vietnamese") != compute_plan_hash(plan_b, cfg_b, "vietnamese")


def test_plan_hash_is_unaffected_by_repo_id():
    from dataclasses import replace

    cfg_a = _cfg()
    cfg_b = replace(cfg_a, hf=HFConfig(repo_id="someone/scratch"))
    plan, _ = build_plan(_manifest(n_convs=4), cfg_a, _pool(), _NORMALIZERS)
    assert compute_plan_hash(plan, cfg_a, "vietnamese") == compute_plan_hash(plan, cfg_b, "vietnamese")


def test_plan_hash_changes_when_shard_packing_changes():
    cfg_a = _cfg(convs_per_shard=3)
    cfg_b = _cfg(convs_per_shard=5)
    plan_a, _ = build_plan(_manifest(n_convs=10), cfg_a, _pool(), _NORMALIZERS)
    plan_b, _ = build_plan(_manifest(n_convs=10), cfg_b, _pool(), _NORMALIZERS)
    assert compute_plan_hash(plan_a, cfg_a, "vietnamese") != compute_plan_hash(plan_b, cfg_b, "vietnamese")


def test_plan_hash_changes_when_text_spoken_changes():
    # A digest of text_spoken must be in the payload -- normalization output
    # changing (e.g. a textprep.py rule edit) must change the hash even though
    # nothing else about the plan (rows, salt, packing) is different.
    cfg = _cfg()
    upper = type("N", (), {"normalize": staticmethod(str.upper)})()
    lower = type("N", (), {"normalize": staticmethod(str.lower)})()
    plan_a, _ = build_plan(
        _manifest(n_convs=4), cfg, _pool(), {("vietnamese", sid): upper for sid in map(str, range(6))}
    )
    plan_b, _ = build_plan(
        _manifest(n_convs=4), cfg, _pool(), {("vietnamese", sid): lower for sid in map(str, range(6))}
    )
    assert compute_plan_hash(plan_a, cfg, "vietnamese") != compute_plan_hash(plan_b, cfg, "vietnamese")


@pytest.mark.parametrize(
    "field,value",
    [
        ("chunk_max_chars", 200),
        ("chunk_overflow_chars", 30),
        ("chars_per_sec", 7.0),
        ("silence_ms", 500),
    ],
)
def test_plan_hash_changes_when_a_pilot_calibrated_text_field_changes(field, value):
    # These are exactly the fields the Task 17 pilot sweeps -- if the hash doesn't
    # cover them, a re-calibrated dataset is indistinguishable from the old one.
    from dataclasses import replace

    cfg_a = _cfg()
    cfg_b = replace(cfg_a, text=replace(cfg_a.text, **{field: value}))
    plan, _ = build_plan(_manifest(n_convs=4), cfg_a, _pool(), _NORMALIZERS)
    assert compute_plan_hash(plan, cfg_a, "vietnamese") != compute_plan_hash(plan, cfg_b, "vietnamese")


@pytest.mark.parametrize(
    "field,value",
    [
        ("cfg_value", 4.0),
        ("temperature", 0.5),
        ("inference_timesteps", 20),
    ],
)
def test_plan_hash_changes_when_an_engine_output_field_changes(field, value):
    from dataclasses import replace

    cfg_a = _cfg()
    cfg_b = replace(cfg_a, engine=replace(cfg_a.engine, **{field: value}))
    plan, _ = build_plan(_manifest(n_convs=4), cfg_a, _pool(), _NORMALIZERS)
    assert compute_plan_hash(plan, cfg_a, "vietnamese") != compute_plan_hash(plan, cfg_b, "vietnamese")


def test_plan_hash_is_unaffected_by_throughput_only_engine_fields():
    # concurrency/max_num_seqs change how FAST a shard is produced, not what the
    # audio sounds like -- they must not invalidate an otherwise-identical plan.
    from dataclasses import replace

    cfg_a = _cfg()
    cfg_b = replace(cfg_a, engine=replace(cfg_a.engine, concurrency=4, max_num_seqs=4))
    plan, _ = build_plan(_manifest(n_convs=4), cfg_a, _pool(), _NORMALIZERS)
    assert compute_plan_hash(plan, cfg_a, "vietnamese") == compute_plan_hash(plan, cfg_b, "vietnamese")


def test_plan_hash_for_one_config_is_unaffected_by_other_configs_in_the_plan():
    # Fix I2: drift is checked per config, so the vietnamese hash must be identical
    # whether the plan was built with configs=("vietnamese",) alone or together
    # with ("vietnamese", "english") over the SAME conversations -- otherwise
    # adding english later would trip PlanDriftError on unchanged vietnamese.
    manifest_vi = _manifest(n_convs=4)
    # Build an English-language manifest for the SAME conversations by relabeling config.
    en_columns = {n: manifest_vi.column(n).to_pylist() for n in manifest_vi.schema.names}
    en_columns["config"] = ["english"] * manifest_vi.num_rows
    manifest_en = pa.Table.from_pydict(en_columns, schema=manifest_vi.schema)
    combined = pa.concat_tables([manifest_vi, manifest_en])

    normalizers = dict(_NORMALIZERS)
    normalizers.update({("english", sid): _IDENTITY for sid in map(str, range(6))})

    cfg_vi_only = _cfg(configs=("vietnamese",))
    cfg_both = _cfg(configs=("vietnamese", "english"))
    plan_vi_only, _ = build_plan(manifest_vi, cfg_vi_only, _pool(), normalizers)
    plan_both, _ = build_plan(combined, cfg_both, _pool(), normalizers)

    assert compute_plan_hash(plan_vi_only, cfg_vi_only, "vietnamese") == compute_plan_hash(
        plan_both, cfg_both, "vietnamese"
    )


def test_write_then_read_round_trips(tmp_path):
    plan, _ = build_plan(_manifest(n_convs=3), _cfg(), _pool(), _NORMALIZERS)
    path = tmp_path / "shard_plan.parquet"
    write_plan(plan, path)
    assert read_plan(path).to_pylist() == plan.to_pylist()
