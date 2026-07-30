import pytest

from meddies_tts.config import ConfigError, load_config

_MINIMAL = """
hf:
  repo_id: "Meddies/SynthAudio"
"""


def _write(tmp_path, text):
    path = tmp_path / "config.yaml"
    path.write_text(text, encoding="utf-8")
    return path


def test_loads_repo_id_and_applies_defaults(tmp_path):
    cfg = load_config(_write(tmp_path, _MINIMAL))
    assert cfg.hf.repo_id == "Meddies/SynthAudio"
    assert cfg.hf.private is False
    assert cfg.speaker.policy == "per_conversation"
    assert cfg.speaker.seed_salt == "v1"
    assert cfg.engine.concurrency == 48
    assert cfg.text.max_chars == 3000
    assert cfg.text.chunk_chars == 130       # fixed budget, not seconds x rate
    assert cfg.text.chunk_hard_cap == 144   # + chunk_overflow_chars
    assert cfg.run.convs_per_shard == 122
    assert cfg.run.configs == ("vietnamese",)


def test_missing_repo_id_raises(tmp_path):
    with pytest.raises(ConfigError, match="hf.repo_id"):
        load_config(_write(tmp_path, "hf: {}\n"))


def test_null_repo_id_raises(tmp_path):
    with pytest.raises(ConfigError, match="hf.repo_id"):
        load_config(_write(tmp_path, "hf:\n  repo_id: null\n"))


def test_override_replaces_repo_id(tmp_path):
    cfg = load_config(_write(tmp_path, _MINIMAL), {"hf.repo_id": "someone/scratch"})
    assert cfg.hf.repo_id == "someone/scratch"


def test_concurrency_above_max_num_seqs_raises(tmp_path):
    text = _MINIMAL + "engine:\n  concurrency: 128\n  max_num_seqs: 64\n"
    with pytest.raises(ConfigError, match="concurrency"):
        load_config(_write(tmp_path, text))


def test_unknown_speaker_policy_raises(tmp_path):
    text = _MINIMAL + "speaker:\n  policy: per_galaxy\n"
    with pytest.raises(ConfigError, match="policy"):
        load_config(_write(tmp_path, text))


def test_config_is_frozen(tmp_path):
    cfg = load_config(_write(tmp_path, _MINIMAL))
    with pytest.raises(Exception):
        cfg.hf.repo_id = "other/repo"


def test_negative_chars_per_sec_raises(tmp_path):
    text = _MINIMAL + "text:\n  chars_per_sec: 0\n"
    with pytest.raises(ConfigError, match="chars_per_sec"):
        load_config(_write(tmp_path, text))


def test_non_positive_chunk_max_chars_raises(tmp_path):
    text = _MINIMAL + "text:\n  chunk_max_chars: 0\n"
    with pytest.raises(ConfigError, match="chunk_max_chars"):
        load_config(_write(tmp_path, text))


def test_negative_convs_per_shard_raises(tmp_path):
    text = _MINIMAL + "run:\n  convs_per_shard: 0\n"
    with pytest.raises(ConfigError, match="convs_per_shard"):
        load_config(_write(tmp_path, text))
