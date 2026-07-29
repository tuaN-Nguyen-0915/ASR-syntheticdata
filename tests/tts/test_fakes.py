import numpy as np
import pytest

from tests.tts.fakes import FakeEngine


async def test_synthesize_returns_float32_audio():
    wave = await FakeEngine().synthesize("xin chào bác sĩ", b"ref", 1)
    assert wave.dtype == np.float32
    assert wave.size > 0


async def test_duration_scales_with_text_length():
    engine = FakeEngine(sample_rate=16000, chars_per_sec=10.0)
    short = await engine.synthesize("x" * 50, b"ref", 1)
    long = await engine.synthesize("x" * 200, b"ref", 1)
    assert len(long) == pytest.approx(4 * len(short), rel=0.05)


async def test_duration_matches_chars_per_sec():
    engine = FakeEngine(sample_rate=16000, chars_per_sec=10.0)
    wave = await engine.synthesize("x" * 100, b"ref", 1)
    assert len(wave) / 16000 == pytest.approx(10.0, rel=0.02)


async def test_same_seed_gives_identical_audio():
    engine = FakeEngine()
    a = await engine.synthesize("xin chào", b"ref", 42)
    b = await engine.synthesize("xin chào", b"ref", 42)
    assert np.array_equal(a, b)


async def test_different_seed_gives_different_audio():
    engine = FakeEngine()
    a = await engine.synthesize("xin chào", b"ref", 1)
    b = await engine.synthesize("xin chào", b"ref", 2)
    assert not np.array_equal(a, b)


async def test_encode_reference_returns_bytes():
    assert isinstance(await FakeEngine().encode_reference(b"RIFF"), bytes)


async def test_records_calls_for_assertions():
    engine = FakeEngine()
    await engine.synthesize("một", b"ref1", 1)
    await engine.synthesize("hai", b"ref2", 2)
    assert [call.text for call in engine.calls] == ["một", "hai"]
    assert [call.ref_latents for call in engine.calls] == [b"ref1", b"ref2"]
    assert [call.seed for call in engine.calls] == [1, 2]


async def test_fail_texts_raise_until_retries_are_exhausted():
    engine = FakeEngine(fail_texts=("boom",), fail_times=2)
    with pytest.raises(RuntimeError):
        await engine.synthesize("boom", b"ref", 1)
    with pytest.raises(RuntimeError):
        await engine.synthesize("boom", b"ref", 2)
    wave = await engine.synthesize("boom", b"ref", 3)
    assert wave.size > 0


async def test_tracks_peak_concurrency():
    import asyncio

    engine = FakeEngine()
    await asyncio.gather(*(engine.synthesize(f"t{i}", b"ref", i) for i in range(8)))
    assert engine.peak_concurrency >= 2


async def test_thousands_of_distinct_seeds_produce_distinct_audio():
    """Verify that seed affects waveform across a wide range; regression test for 90% seed collision."""
    engine = FakeEngine()
    text = "x" * 100  # Fixed text length ensures duration is constant.
    num_seeds = 2000
    waveforms = {}
    for seed in range(num_seeds):
        wave = await engine.synthesize(text, b"ref", seed)
        # Use bytes representation as key to detect byte-identical outputs.
        key = wave.tobytes()
        if key not in waveforms:
            waveforms[key] = []
        waveforms[key].append(seed)
    # Expect roughly one waveform per seed (allowing for tiny floating-point variations).
    # With good RNG-based waveform, distinct_count should be close to num_seeds.
    distinct_count = len(waveforms)
    assert distinct_count > num_seeds * 0.95, f"Only {distinct_count}/{num_seeds} seeds produced distinct audio"
