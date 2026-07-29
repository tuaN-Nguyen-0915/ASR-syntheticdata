# tests/tts/test_cli_tts.py
import json

import huggingface_hub
import pytest

import cli
from meddies_tts.hub import plan_hash_path
from meddies_tts.manifest import read_manifest
from meddies_tts.plan import read_plan
from tests.tts.test_hub import FakeApi

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
    # One hash per config (Fix I2), stored as a {config: hash} JSON mapping, not
    # a single hash for the whole plan file.
    plan_out = _make_plan(workspace)
    hashes = json.loads(plan_out.with_suffix(".hash").read_text(encoding="utf-8"))
    assert hashes.keys() == {"vietnamese"}
    assert hashes["vietnamese"]


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


def test_estimate_falls_back_to_the_configs_calibrated_chars_per_sec(workspace, capsys):
    # Fix 1: without --chars-per-sec, `estimate` must use the pilot-calibrated
    # config.yaml value, not the pre-pilot argparse default of 14.0.
    (workspace / "config.yaml").write_text(
        _CONFIG + "text:\n  chars_per_sec: 7.0\n", encoding="utf-8"
    )
    plan_out = _make_plan(workspace)
    assert _run(workspace, "estimate", "--plan", str(plan_out)) == 0
    out = capsys.readouterr().out
    assert "at 7.0 chars/sec" in out


def test_estimate_flag_overrides_the_configs_chars_per_sec(workspace, capsys):
    (workspace / "config.yaml").write_text(
        _CONFIG + "text:\n  chars_per_sec: 7.0\n", encoding="utf-8"
    )
    plan_out = _make_plan(workspace)
    assert _run(workspace, "estimate", "--plan", str(plan_out), "--chars-per-sec", "20.0") == 0
    out = capsys.readouterr().out
    assert "at 20.0 chars/sec" in out


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
        "text_raw": "x", "text_spoken": "x", "speaker_id": "0",
        "speaker_source": "visec", "speaker_gender": "",
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


def _shard_with_audio_path(workspace, name, audio_path):
    """Write a one-row shard whose audio.path is exactly the given (possibly malicious) value."""
    from meddies_tts.audio import to_flac_bytes
    from meddies_tts.writer import build_row, write_shard
    import numpy as np

    row = {
        "config": "vietnamese", "disease_slug": "suy_gan", "disease_name": "Suy gan",
        "conv_id": "conv_0001", "turn": 1, "role": "user",
        "text_raw": "x", "text_spoken": "x", "speaker_id": "0",
        "speaker_source": "visec", "speaker_gender": "",
        "speaker_emotions": "neutral", "speaker_unique_source_s": 100.0,
        "shard_id": "vi-00000",
        "audio_path": audio_path,
    }
    shard = workspace / name
    write_shard([build_row(row, to_flac_bytes(np.zeros(1600, dtype=np.float32), 16000),
                           0.1, 1, 1, "v")], shard, "h", "{}")
    return shard


def test_materialize_tree_rejects_relative_traversal(workspace, tmp_path):
    # A shard is untrusted input by construction (it may come straight from the
    # Hub), so "../ESCAPED.flac" must not be allowed to land outside --dest.
    shard = _shard_with_audio_path(workspace, "shard_traversal.parquet",
                                    "../OUTSIDE/ESCAPED.flac")
    dest = tmp_path / "tree"
    code = _run(workspace, "materialize-tree", "--shard", str(shard), "--dest", str(dest))
    assert code != 0
    assert not (tmp_path / "OUTSIDE" / "ESCAPED.flac").exists()
    assert not dest.exists() or not any(dest.rglob("*"))


def test_materialize_tree_rejects_absolute_path(workspace, tmp_path):
    # pathlib silently discards the left operand when joined with an absolute
    # path: Path("/a/dest") / "/etc/x" == Path("/etc/x"). An absolute audio.path
    # must be rejected outright, not silently honored.
    escape_target = tmp_path / "ABSOLUTE_OUTSIDE" / "ABSOLUTE.flac"
    shard = _shard_with_audio_path(workspace, "shard_absolute.parquet", str(escape_target))
    dest = tmp_path / "tree2"
    code = _run(workspace, "materialize-tree", "--shard", str(shard), "--dest", str(dest))
    assert code != 0
    assert not escape_target.exists()


def _patch_hf_api(monkeypatch, fake_api):
    """Make `from huggingface_hub import HfApi; HfApi()` inside cli.py hand back fake_api."""
    monkeypatch.setattr(huggingface_hub, "HfApi", lambda *a, **kw: fake_api)


def test_status_reports_all_remaining_on_a_fresh_repo(workspace, capsys, monkeypatch):
    plan_out = _make_plan(workspace)
    _patch_hf_api(monkeypatch, FakeApi(files=[]))  # nothing published yet, no hash file either
    assert _run(workspace, "status", "--plan", str(plan_out)) == 0
    out = capsys.readouterr().out
    assert "done      : 0" in out
    assert "remaining : 2" in out


def test_status_exits_nonzero_on_plan_drift(workspace, capsys, monkeypatch):
    plan_out = _make_plan(workspace)
    # A hash published under a different value than the local plan simulates a
    # repo whose shards were produced by a plan that has since changed underneath it.
    fake_api = FakeApi(files=[], remote_files={plan_hash_path("vietnamese"): "not-the-local-hash"})
    _patch_hf_api(monkeypatch, fake_api)
    code = _run(workspace, "status", "--plan", str(plan_out))
    assert code == cli._EXIT_PLAN_DRIFT
    err = capsys.readouterr().err
    assert err.startswith("error:")
    assert "plan hash mismatch" in err


def test_preflight_reports_a_clean_error_on_invalid_token(workspace, capsys, monkeypatch):
    _patch_hf_api(monkeypatch, FakeApi(whoami=None))  # invalid/missing HF token
    code = _run(workspace, "preflight")
    assert code == cli._EXIT_ERROR
    err = capsys.readouterr().err
    assert err.startswith("error:")
    assert "token" in err
