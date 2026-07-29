import numpy as np

from meddies_tts.qc import DEFAULT_CHARS_PER_SEC, check_audio


def _tone(seconds, sample_rate=16000, amplitude=0.3):
    t = np.linspace(0, seconds, int(seconds * sample_rate), endpoint=False)
    return (amplitude * np.sin(2 * np.pi * 220 * t)).astype(np.float32)


def test_default_chars_per_sec_is_the_spec_assumption():
    assert DEFAULT_CHARS_PER_SEC == 14.0


def test_accepts_audio_of_the_expected_duration():
    # 140 chars at 14 chars/sec -> 10 s expected
    assert check_audio(_tone(10.0), 16000, 140).ok


def test_accepts_within_the_tolerance_band():
    assert check_audio(_tone(5.0), 16000, 140).ok   # 0.5x
    assert check_audio(_tone(25.0), 16000, 140).ok  # 2.5x


def test_rejects_empty_audio():
    result = check_audio(np.zeros(0, dtype=np.float32), 16000, 140)
    assert not result.ok
    assert result.reason == "empty"


def test_rejects_silent_audio():
    result = check_audio(np.zeros(160000, dtype=np.float32), 16000, 140)
    assert not result.ok
    assert result.reason == "silent"


def test_rejects_nan():
    wave = _tone(10.0)
    wave[100] = np.nan
    result = check_audio(wave, 16000, 140)
    assert not result.ok
    assert result.reason == "not_finite"


def test_rejects_inf():
    wave = _tone(10.0)
    wave[100] = np.inf
    assert check_audio(wave, 16000, 140).reason == "not_finite"


def test_rejects_truncated_audio():
    result = check_audio(_tone(1.0), 16000, 140)  # 0.1x expected
    assert not result.ok
    assert result.reason == "too_short"


def test_rejects_runaway_audio():
    result = check_audio(_tone(60.0), 16000, 140)  # ~6x expected
    assert not result.ok
    assert result.reason == "too_long"


def test_zero_length_text_is_rejected_before_duration_maths():
    assert check_audio(_tone(1.0), 16000, 0).reason == "no_text"


def test_calibrated_chars_per_sec_shifts_the_band():
    # 280 chars at 28 chars/sec -> 10 s expected, so 10 s of audio is fine
    assert check_audio(_tone(10.0), 16000, 280, chars_per_sec=28.0).ok


def test_detail_is_populated_on_failure():
    assert check_audio(_tone(1.0), 16000, 140).detail


def test_rejects_silence_below_threshold():
    # RMS of sine wave with amplitude A is A/sqrt(2).
    # silence_rms default is 1e-4. Generate audio with RMS just below it.
    # amplitude = 0.9e-4 * sqrt(2) ≈ 1.273e-4
    amplitude_below = 0.9e-4 * np.sqrt(2)
    wave = _tone(10.0, amplitude=amplitude_below)
    result = check_audio(wave, 16000, 140)
    assert not result.ok
    assert result.reason == "silent"


def test_accepts_silence_above_threshold():
    # Generate audio with RMS just above the 1e-4 threshold.
    # amplitude = 1.1e-4 * sqrt(2) ≈ 1.556e-4
    amplitude_above = 1.1e-4 * np.sqrt(2)
    wave = _tone(10.0, amplitude=amplitude_above)
    result = check_audio(wave, 16000, 140)
    assert result.ok
