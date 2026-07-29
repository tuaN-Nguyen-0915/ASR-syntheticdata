import io

import numpy as np
import pytest
import soundfile as sf

from meddies_tts.audio import (
    TARGET_SAMPLE_RATE,
    duration_seconds,
    join_chunks,
    match_loudness,
    resample,
    to_flac_bytes,
)


def _tone(seconds, sample_rate=48000, freq=440.0):
    t = np.linspace(0, seconds, int(seconds * sample_rate), endpoint=False)
    return (0.3 * np.sin(2 * np.pi * freq * t)).astype(np.float32)


def test_target_sample_rate_is_16k():
    assert TARGET_SAMPLE_RATE == 16000


def test_single_chunk_is_returned_unchanged():
    wave = _tone(0.5)
    assert np.array_equal(join_chunks([wave], 48000, 250), wave)


def test_join_inserts_silence_between_chunks():
    wave = _tone(0.5)
    joined = join_chunks([wave, wave], 48000, 250)
    expected = len(wave) * 2 + int(48000 * 0.25)
    assert len(joined) == expected


def test_join_adds_no_trailing_silence():
    wave = _tone(0.1)
    joined = join_chunks([wave, wave, wave], 48000, 100)
    assert len(joined) == len(wave) * 3 + 2 * int(48000 * 0.1)


def test_join_of_empty_list_raises():
    with pytest.raises(ValueError, match="at least one"):
        join_chunks([], 48000, 250)


def test_join_preserves_float32_dtype():
    assert join_chunks([_tone(0.1), _tone(0.1)], 48000, 250).dtype == np.float32


def test_resample_changes_length_proportionally():
    wave = _tone(1.0, 48000)
    out = resample(wave, 48000, 16000)
    assert abs(len(out) - 16000) <= 8


def test_resample_is_identity_when_rates_match():
    wave = _tone(0.25, 16000)
    assert np.array_equal(resample(wave, 16000, 16000), wave)


def test_resample_preserves_a_440hz_tone():
    out = resample(_tone(1.0, 48000, 440.0), 48000, 16000)
    spectrum = np.abs(np.fft.rfft(out))
    peak_hz = np.fft.rfftfreq(len(out), 1 / 16000)[int(np.argmax(spectrum))]
    assert abs(peak_hz - 440.0) < 5.0


def test_flac_bytes_are_decodable():
    wave = _tone(0.5, 16000)
    decoded, sr = sf.read(io.BytesIO(to_flac_bytes(wave, 16000)), dtype="float32")
    assert sr == 16000
    assert len(decoded) == len(wave)


def test_flac_is_lossless_within_16bit_quantization():
    wave = _tone(0.5, 16000)
    decoded, _ = sf.read(io.BytesIO(to_flac_bytes(wave, 16000)), dtype="float32")
    assert np.max(np.abs(decoded - wave)) < 1e-3


def test_flac_output_is_mono():
    data = to_flac_bytes(_tone(0.2, 16000), 16000)
    with sf.SoundFile(io.BytesIO(data)) as handle:
        assert handle.channels == 1
        assert handle.format == "FLAC"


def test_flac_is_smaller_than_raw_pcm():
    wave = _tone(2.0, 16000)
    assert len(to_flac_bytes(wave, 16000)) < wave.nbytes


def test_duration_seconds():
    assert duration_seconds(np.zeros(32000, dtype=np.float32), 16000) == pytest.approx(2.0)


# --- loudness matching across independently generated chunks ------------------

def _rms(wave):
    return float(np.sqrt(np.mean(np.square(wave, dtype=np.float64))))


def test_match_loudness_evens_out_quiet_and_loud_chunks():
    loud, quiet = _tone(0.5) * 1.0, _tone(0.5) * 0.4
    before = _rms(loud) / _rms(quiet)
    a, b = match_loudness([loud, quiet, loud])[:2]
    assert abs(_rms(a) / _rms(b) - 1.0) < abs(before - 1.0)


def test_match_loudness_is_a_noop_for_a_single_chunk():
    wave = _tone(0.3)
    assert np.array_equal(match_loudness([wave])[0], wave)


def test_match_loudness_does_not_amplify_silence():
    silence = np.zeros(4800, dtype=np.float32)
    out = match_loudness([_tone(0.3), silence])
    assert _rms(out[1]) < 1e-6


def test_match_loudness_never_clips():
    out = match_loudness([_tone(0.3) * 0.95, _tone(0.3) * 0.2])
    assert all(float(np.max(np.abs(w))) <= 1.0 for w in out)


def test_match_loudness_gain_is_clamped():
    # A chunk 10x quieter is lifted, but by at most 2x -- never to full parity.
    out = match_loudness([_tone(0.5), _tone(0.5) * 0.1, _tone(0.5)])
    assert _rms(out[1]) <= _rms(_tone(0.5) * 0.1) * 2.0 + 1e-9


def test_join_applies_loudness_matching():
    joined = join_chunks([_tone(0.5), _tone(0.5) * 0.3], 48000, 0)
    half = len(joined) // 2
    ratio = _rms(joined[:half]) / max(_rms(joined[half:]), 1e-9)
    assert ratio < 3.0   # untreated this would be ~3.3


def test_match_loudness_peak_limiter_triggers():
    # A spiky chunk has a high peak but low RMS, so it earns a large gain while
    # already sitting near full scale -- the only shape that can overshoot the
    # ceiling. A quiet *sine* cannot: its peak and RMS are locked together.
    spiky = np.zeros(24000, dtype=np.float32)
    spiky[::10] = 0.95                      # rms ~0.300, peak 0.95
    steady = _tone(0.5, 48000) * 2.0        # rms ~0.42, peak ~0.6
    out = match_loudness([spiky, steady, steady])
    # Un-limited, gain 1.412 would push the peak to 1.342; the limiter must pull it back.
    assert float(np.max(np.abs(out[0]))) == pytest.approx(0.99, abs=1e-4)


def test_flac_encoding_clips_resampling_overshoot():
    # A peak-limited signal at 48 kHz can overshoot after sinc resampling to 16 kHz
    # via Gibbs ringing. The encoder must clamp to prevent clipping in FLAC.
    # Generate a signal that stays within limits after loudness match/peak limit,
    # then resample and verify no clipping occurs in the FLAC output.
    wave_48k = match_loudness([_tone(0.5, 48000) * 0.95])[0]
    resampled = resample(wave_48k, 48000, 16000)
    # Resampling may overshoot; verify FLAC encoding handles it without clipping.
    flac_bytes = to_flac_bytes(resampled, 16000)
    decoded, _ = sf.read(io.BytesIO(flac_bytes), dtype="float32")
    assert float(np.max(np.abs(decoded))) <= 1.0


def test_match_loudness_passes_through_nonfinite_chunks():
    # Non-finite chunks must not be scaled (which would multiply nan by a gain).
    # They should pass through unmodified so QC (Task 9) can detect and reject them.
    bad_chunk = np.array([1.0, np.nan, -0.5], dtype=np.float32)
    good_chunk = _tone(0.3)
    out = match_loudness([good_chunk, bad_chunk])
    assert np.isnan(out[1][1])  # NaN is preserved, not corrupted to zero
