import pytest

from meddies_tts.config import SpeakerConfig
from meddies_tts.speakers import (
    PerConversationAssigner,
    PerTurnAssigner,
    derive_seed,
    get_assigner,
    load_pool,
)

_CSV = """speaker_id,output_path,duration_seconds,clip_count,emotions,unique_source_duration_seconds
0,processed_audio_by_id/speaker_000.wav,12.968,8,angry|happy|neutral|sad,3951.683
1,processed_audio_by_id/speaker_001.wav,12.8,9,angry|neutral,67.904
79,processed_audio_by_id/speaker_079.wav,12.1,10,angry,1.3
136,processed_audio_by_id/speaker_136.wav,11.9,6,neutral,2.0
"""


def _pool_csv(tmp_path):
    root = tmp_path / "ViSEC-processed"
    (root / "processed_audio_by_id").mkdir(parents=True)
    csv = root / "processed_audio_by_id" / "metadata.csv"
    csv.write_text(_CSV, encoding="utf-8")
    for sid in (0, 1, 79, 136):
        (root / "processed_audio_by_id" / f"speaker_{sid:03d}.wav").write_bytes(b"RIFF")
    return csv


def test_derive_seed_is_stable_across_calls():
    assert derive_seed("v1", "vietnamese", "conv_0001") == derive_seed(
        "v1", "vietnamese", "conv_0001"
    )


def test_derive_seed_differs_by_salt():
    assert derive_seed("v1", "a") != derive_seed("v2", "a")


def test_derive_seed_differs_by_parts():
    assert derive_seed("v1", "a") != derive_seed("v1", "b")


def test_derive_seed_fits_in_int64():
    assert 0 <= derive_seed("v1", "x") <= 2**63 - 1


def test_load_pool_reads_every_speaker(tmp_path):
    assert len(load_pool(_pool_csv(tmp_path))) == 4


def test_load_pool_parses_fields(tmp_path):
    speaker = next(s for s in load_pool(_pool_csv(tmp_path)) if s.speaker_id == 79)
    assert speaker.emotions == "angry"
    assert speaker.unique_source_s == pytest.approx(1.3)
    assert speaker.duration_s == pytest.approx(12.1)
    assert speaker.wav_path.name == "speaker_079.wav"
    assert speaker.wav_path.exists()


def test_load_pool_applies_allow_filter(tmp_path):
    pool = load_pool(_pool_csv(tmp_path), allow={0, 1})
    assert [s.speaker_id for s in pool] == [0, 1]


def test_per_conversation_gives_same_speaker_for_every_turn(tmp_path):
    pool = load_pool(_pool_csv(tmp_path))
    assigner = PerConversationAssigner(pool, "v1")
    ids = [assigner.assign("vietnamese", "suy_gan", "conv_0001", t, "user") for t in range(1, 9)]
    assert len(set(ids)) == 1


def test_per_conversation_user_and_assistant_differ(tmp_path):
    pool = load_pool(_pool_csv(tmp_path))
    assigner = PerConversationAssigner(pool, "v1")
    user = assigner.assign("vietnamese", "suy_gan", "conv_0001", 1, "user")
    assistant = assigner.assign("vietnamese", "suy_gan", "conv_0001", 1, "assistant")
    assert user != assistant


def test_per_conversation_is_reproducible(tmp_path):
    pool = load_pool(_pool_csv(tmp_path))
    a = PerConversationAssigner(pool, "v1").assign("vietnamese", "suy_gan", "conv_0007", 3, "user")
    b = PerConversationAssigner(pool, "v1").assign("vietnamese", "suy_gan", "conv_0007", 3, "user")
    assert a == b


def test_changing_salt_reshuffles(tmp_path):
    pool = load_pool(_pool_csv(tmp_path))
    a = [PerConversationAssigner(pool, "v1").assign("vietnamese", "d", f"conv_{i:04d}", 1, "user")
         for i in range(40)]
    b = [PerConversationAssigner(pool, "v2").assign("vietnamese", "d", f"conv_{i:04d}", 1, "user")
         for i in range(40)]
    assert a != b


def test_different_conversations_get_different_pairs(tmp_path):
    pool = load_pool(_pool_csv(tmp_path))
    assigner = PerConversationAssigner(pool, "v1")
    ids = {assigner.assign("vietnamese", "d", f"conv_{i:04d}", 1, "user") for i in range(40)}
    assert len(ids) > 1


def test_per_turn_varies_across_turns(tmp_path):
    pool = load_pool(_pool_csv(tmp_path))
    assigner = PerTurnAssigner(pool, "v1")
    ids = {assigner.assign("vietnamese", "d", "conv_0001", t, "user") for t in range(1, 30)}
    assert len(ids) > 1


def test_per_turn_still_differs_by_role(tmp_path):
    pool = load_pool(_pool_csv(tmp_path))
    assigner = PerTurnAssigner(pool, "v1")
    user = assigner.assign("vietnamese", "d", "conv_0001", 4, "user")
    assistant = assigner.assign("vietnamese", "d", "conv_0001", 4, "assistant")
    assert user != assistant


def test_get_assigner_selects_policy(tmp_path):
    pool = load_pool(_pool_csv(tmp_path))
    assert isinstance(get_assigner(SpeakerConfig(), pool), PerConversationAssigner)
    assert isinstance(
        get_assigner(SpeakerConfig(policy="per_turn"), pool), PerTurnAssigner
    )


def test_pool_smaller_than_two_raises(tmp_path):
    pool = load_pool(_pool_csv(tmp_path), allow={0})
    with pytest.raises(ValueError, match="at least 2"):
        PerConversationAssigner(pool, "v1")
