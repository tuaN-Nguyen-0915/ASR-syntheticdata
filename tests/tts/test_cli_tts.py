# tests/tts/test_cli_tts.py
import json

import pytest

import cli
from meddies_tts.manifest import read_manifest
from meddies_tts.plan import read_plan

_CONFIG = """
hf:
  repo_id: "Meddies/SynthAudio"
run:
  convs_per_shard: 2
  configs: ["vietnamese"]
"""

_VISEC = """speaker_id,output_path,duration_seconds,clip_count,emotions,unique_source_duration_seconds
0,processed_audio_by_id/speaker_000.wav,12.9,8,neutral,100.0
1,processed_audio_by_id/speaker_001.wav,12.8,9,neutral,120.0
2,processed_audio_by_id/speaker_002.wav,12.5,7,neutral,140.0
"""


@pytest.fixture()
def workspace(tmp_path):
    (tmp_path / "config.yaml").write_text(_CONFIG, encoding="utf-8")
    tree = tmp_path / "output_full" / "vietnamese" / "suy_gan"
    for conv in ("conv_0001", "conv_0002", "conv_0003"):
        for turn in (1, 2):
            d = tree / conv / f"Turn{turn}"
            d.mkdir(parents=True)
            (d / "user.txt").write_text("Xin chào bác sĩ.", encoding="utf-8")
            (d / "assistant.txt").write_text("Chào bạn.", encoding="utf-8")
    (tree / "_disease_name.txt").write_text("Suy gan", encoding="utf-8")
    visec = tmp_path / "ViSEC" / "processed_audio_by_id"
    visec.mkdir(parents=True)
    (visec / "metadata.csv").write_text(_VISEC, encoding="utf-8")
    for sid in range(3):
        (visec / f"speaker_{sid:03d}.wav").write_bytes(b"RIFF")
    return tmp_path


def _run(workspace, *args):
    return cli.main([
        "--config", str(workspace / "config.yaml"), *args
    ])


def test_build_manifest_writes_parquet(workspace):
    out = workspace / "manifest.parquet"
    assert _run(workspace, "build-manifest",
                "--output-root", str(workspace / "output_full"),
                "--out", str(out)) == 0
    assert read_manifest(out).num_rows == 12


def _make_plan(workspace):
    manifest = workspace / "manifest.parquet"
    _run(workspace, "build-manifest", "--output-root", str(workspace / "output_full"),
         "--out", str(manifest))
    plan_out = workspace / "shard_plan.parquet"
    _run(workspace, "plan", "--manifest", str(manifest),
         "--visec", str(workspace / "ViSEC" / "processed_audio_by_id" / "metadata.csv"),
         "--out", str(plan_out), "--rejects", str(workspace / "rejects.jsonl"))
    return plan_out


def test_plan_writes_plan_and_rejects(workspace):
    plan_out = _make_plan(workspace)
    assert read_plan(plan_out).num_rows == 12
    assert (workspace / "rejects.jsonl").exists()


def test_plan_packs_conversations_into_shards(workspace):
    shards = set(read_plan(_make_plan(workspace)).column("shard_id").to_pylist())
    assert shards == {"vi-00000", "vi-00001"}


def test_plan_writes_a_hash_file(workspace):
    plan_out = _make_plan(workspace)
    assert plan_out.with_suffix(".hash").read_text(encoding="utf-8").strip()


def test_plan_normalizes_numbers_into_text_spoken(workspace):
    (workspace / "output_full" / "vietnamese" / "suy_gan" / "conv_0001" / "Turn1"
     / "user.txt").write_text("Sốt cao 38.5°C, gọi 115.", encoding="utf-8")
    rows = read_plan(_make_plan(workspace)).to_pylist()
    row = next(r for r in rows if r["conv_id"] == "conv_0001" and r["turn"] == 1
               and r["role"] == "user")
    assert row["text_raw"] == "Sốt cao 38.5°C, gọi 115."
    assert row["text_spoken"] == "Sốt cao ba mươi tám phẩy năm độ C, gọi một một năm."


def test_estimate_reports_cost_and_storage(workspace, capsys):
    plan_out = _make_plan(workspace)
    assert _run(workspace, "estimate", "--plan", str(plan_out)) == 0
    out = capsys.readouterr().out
    assert "GPU-hours" in out and "USD" in out and "GB" in out


def test_missing_repo_id_exits_nonzero(workspace, capsys):
    (workspace / "bad.yaml").write_text("hf: {}\n", encoding="utf-8")
    code = cli.main(["--config", str(workspace / "bad.yaml"), "estimate",
                     "--plan", str(workspace / "nope.parquet")])
    assert code == 2
    assert "hf.repo_id" in capsys.readouterr().err


def test_hf_repo_override_is_applied(workspace, capsys):
    _run(workspace, "build-manifest", "--output-root", str(workspace / "output_full"),
         "--out", str(workspace / "m.parquet"))
    cli.main(["--config", str(workspace / "config.yaml"), "--hf-repo", "someone/scratch",
              "show-config"])
    assert "someone/scratch" in capsys.readouterr().out


def test_materialize_tree_rebuilds_the_output_full_shape(workspace, tmp_path):
    from meddies_tts.audio import to_flac_bytes
    from meddies_tts.writer import build_row, write_shard
    import numpy as np

    row = {
        "config": "vietnamese", "disease_slug": "suy_gan", "disease_name": "Suy gan",
        "conv_id": "conv_0001", "turn": 1, "role": "user",
        "text_raw": "x", "text_spoken": "x", "speaker_id": 0,
        "speaker_emotions": "neutral", "speaker_unique_source_s": 100.0,
        "shard_id": "vi-00000",
        "audio_path": "vietnamese/suy_gan/conv_0001/Turn1/user.flac",
    }
    shard = workspace / "shard.parquet"
    write_shard([build_row(row, to_flac_bytes(np.zeros(1600, dtype=np.float32), 16000),
                           0.1, 1, 1, "v")], shard, "h", "{}")
    dest = tmp_path / "tree"
    assert _run(workspace, "materialize-tree", "--shard", str(shard),
                "--dest", str(dest)) == 0
    assert (dest / "vietnamese/suy_gan/conv_0001/Turn1/user.flac").exists()
