import pytest

from meddies_tts.audio import TARGET_SAMPLE_RATE
from meddies_tts.config import Config, EngineConfig, HFConfig, TextConfig
from meddies_tts.runner import run_shard
from tests.tts.fakes import FakeEngine


def _cfg(concurrency=8, chunk_seconds=12.0):
    # chunk_chars is a derived property (Task 1), so size it via the duration target:
    # chunk_chars == int(chunk_seconds * chars_per_sec).
    return Config(
        hf=HFConfig(repo_id="Meddies/SynthAudio"),
        engine=EngineConfig(concurrency=concurrency, max_num_seqs=concurrency),
        text=TextConfig(chunk_target_seconds=chunk_seconds, chars_per_sec=10.0),
    )


def _row(index=0, text="Xin chào bác sĩ. Tôi bị đau bụng."):
    return {
        "config": "vietnamese",
        "disease_slug": "suy_gan",
        "disease_name": "Suy gan",
        "conv_id": f"conv_{index // 4:04d}",
        "turn": (index % 4) + 1,
        "role": "user" if index % 2 == 0 else "assistant",
        "text_raw": text,
        "text_spoken": text,
        "speaker_id": 0,
        "speaker_emotions": "neutral",
        "speaker_unique_source_s": 100.0,
        "shard_id": "vi-00000",
        "audio_path": f"vietnamese/suy_gan/conv_{index:04d}/Turn1/user.flac",
    }


_REFS = {0: b"latents-0"}


async def test_produces_one_row_per_utterance():
    rows, result = await run_shard("vi-00000", [_row(i) for i in range(5)],
                                   FakeEngine(), _REFS, _cfg())
    assert len(rows) == 5
    assert result.n_utterances == 5
    assert result.n_failed == 0


async def test_result_reports_shard_id_and_audio_seconds():
    rows, result = await run_shard("vi-00000", [_row(0)], FakeEngine(), _REFS, _cfg())
    assert result.shard_id == "vi-00000"
    assert result.audio_seconds == pytest.approx(rows[0]["duration_s"], rel=1e-3)


async def test_audio_is_resampled_to_16k():
    rows, _ = await run_shard("vi-00000", [_row(0)], FakeEngine(sample_rate=48000),
                              _REFS, _cfg())
    import io

    import soundfile as sf

    with sf.SoundFile(io.BytesIO(rows[0]["audio"]["bytes"])) as handle:
        assert handle.samplerate == TARGET_SAMPLE_RATE


async def test_keeps_the_engine_busy_with_many_concurrent_requests():
    # Floor: with 40 utterances (far more than enough to saturate 8 slots), peak
    # concurrency must actually REACH the configured limit, not merely exceed 1 --
    # a fan-out regression to e.g. peak=2 would still pass a `> 1` assertion.
    engine = FakeEngine()
    cfg = _cfg(concurrency=8)
    await run_shard("vi-00000", [_row(i) for i in range(40)], engine, _REFS, cfg)
    assert engine.peak_concurrency >= cfg.engine.concurrency


async def test_never_exceeds_the_configured_concurrency():
    engine = FakeEngine()
    await run_shard("vi-00000", [_row(i) for i in range(40)], engine, _REFS, _cfg(concurrency=4))
    assert engine.peak_concurrency <= 4


async def test_long_text_is_chunked_and_n_chunks_recorded():
    text = " ".join(f"Đây là câu số {i}." for i in range(60))
    rows, _ = await run_shard("vi-00000", [_row(0, text)], FakeEngine(), _REFS,
                              _cfg(chunk_seconds=12.0))   # 120-char budget
    assert rows[0]["n_chunks"] > 1


async def test_short_text_is_a_single_chunk():
    rows, _ = await run_shard("vi-00000", [_row(0)], FakeEngine(), _REFS, _cfg())
    assert rows[0]["n_chunks"] == 1


async def test_generation_is_deterministic_for_the_same_row():
    first, _ = await run_shard("vi-00000", [_row(0)], FakeEngine(), _REFS, _cfg())
    second, _ = await run_shard("vi-00000", [_row(0)], FakeEngine(), _REFS, _cfg())
    assert first[0]["seed"] == second[0]["seed"]
    assert first[0]["audio"]["bytes"] == second[0]["audio"]["bytes"]


async def test_different_utterances_get_different_seeds():
    rows, _ = await run_shard("vi-00000", [_row(0), _row(1)], FakeEngine(), _REFS, _cfg())
    assert rows[0]["seed"] != rows[1]["seed"]


async def test_transient_chunk_failure_is_retried_and_succeeds():
    text = "Một câu duy nhất."
    engine = FakeEngine(fail_texts=(text,), fail_times=1)
    rows, result = await run_shard("vi-00000", [_row(0, text)], engine, _REFS, _cfg())
    assert len(rows) == 1
    assert result.n_failed == 0


async def test_permanent_chunk_failure_drops_only_that_utterance():
    bad = "Câu hỏng."
    engine = FakeEngine(fail_texts=(bad,), fail_times=99)
    plan = [_row(0), _row(1, bad), _row(2)]
    rows, result = await run_shard("vi-00000", plan, engine, _REFS, _cfg())
    assert len(rows) == 2
    assert result.n_failed == 1
    assert result.failures[0]["audio_path"] == plan[1]["audio_path"]
    assert result.failures[0]["reason"] == "engine_error"


async def test_qc_failure_is_recorded_as_a_failure():
    # chars_per_sec far from the fake engine's rate makes every duration look wrong
    engine = FakeEngine(chars_per_sec=14.0)
    rows, result = await run_shard("vi-00000", [_row(0)], engine, _REFS, _cfg(),
                                   chars_per_sec=1000.0)
    assert rows == []
    assert result.n_failed == 1
    assert result.failures[0]["reason"].startswith("qc:")


async def test_a_failing_utterance_does_not_abort_the_shard():
    bad = "Câu hỏng."
    engine = FakeEngine(fail_texts=(bad,), fail_times=99)
    plan = [_row(i) for i in range(10)] + [_row(99, bad)]
    rows, result = await run_shard("vi-00000", plan, engine, _REFS, _cfg())
    assert len(rows) == 10
    assert result.n_utterances == 11


async def test_row_order_follows_the_plan():
    plan = [_row(i) for i in range(6)]
    rows, _ = await run_shard("vi-00000", plan, FakeEngine(), _REFS, _cfg())
    assert [r["conv_id"] for r in rows] == [p["conv_id"] for p in plan]


async def test_missing_reference_latents_raises():
    with pytest.raises(KeyError):
        await run_shard("vi-00000", [_row(0)], FakeEngine(), {}, _cfg())


async def test_qc_retry_uses_a_different_seed_than_the_first_attempt():
    # chars_per_sec mismatch makes every attempt fail QC, so both the initial
    # generation and the reseeded retry run. A single-chunk utterance means exactly
    # two engine calls; their seeds must differ, or "regenerate with a different
    # seed" is a no-op that would never actually produce different audio.
    engine = FakeEngine(chars_per_sec=14.0)
    rows, result = await run_shard("vi-00000", [_row(0)], engine, _REFS, _cfg(),
                                   chars_per_sec=1000.0)
    assert rows == []
    assert result.n_failed == 1
    seeds_used = [call.seed for call in engine.calls]
    assert len(seeds_used) == 2
    assert len(set(seeds_used)) == 2


async def test_downstream_error_is_recorded_not_fatal_to_the_shard(monkeypatch):
    # Simulates a bug in post-processing (e.g. build_row's schema check raising) for
    # exactly one row. The other rows must still come back and the bad row must be
    # recorded as a failure -- not propagate out of run_shard and discard everything.
    import meddies_tts.runner as runner_module

    real_build_row = runner_module.build_row
    bad_path = _row(1)["audio_path"]

    def flaky_build_row(row, *args, **kwargs):
        if row["audio_path"] == bad_path:
            raise ValueError("boom")
        return real_build_row(row, *args, **kwargs)

    monkeypatch.setattr(runner_module, "build_row", flaky_build_row)

    plan = [_row(0), _row(1), _row(2)]
    rows, result = await run_shard("vi-00000", plan, FakeEngine(), _REFS, _cfg())

    assert len(rows) == 2
    assert result.n_failed == 1
    assert result.failures[0]["audio_path"] == bad_path
    assert result.failures[0]["reason"] == "unexpected_error"


async def test_missing_audio_path_is_recorded_not_a_crash():
    # A row missing "audio_path" makes the failure-handler's own row["audio_path"]
    # lookup raise a second KeyError that used to escape uncaught. The handler must
    # be defensive (row.get) so this degrades to a recorded failure instead.
    row = _row(0)
    del row["audio_path"]
    rows, result = await run_shard("vi-00000", [row], FakeEngine(), _REFS, _cfg())
    assert rows == []
    assert result.n_failed == 1
    assert result.failures[0]["audio_path"] == "<unknown>"
