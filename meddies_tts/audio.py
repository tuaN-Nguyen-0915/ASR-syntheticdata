from __future__ import annotations

import io

import numpy as np
import soundfile as sf
import soxr

TARGET_SAMPLE_RATE = 16000


def _rms(wave: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.square(wave, dtype=np.float64))))


def match_loudness(waves: list[np.ndarray], ceiling: float = 0.99) -> list[np.ndarray]:
    """Scale each chunk to the median chunk RMS.

    Chunks are generated independently, so their levels drift. Untreated, that is an
    audible step at every join -- the one artefact that makes concatenated speech
    obviously synthetic. Gains are clamped so a near-silent chunk is not amplified into
    noise, and the result is peak-limited to avoid clipping.
    """
    levels = [_rms(wave) for wave in waves]
    usable = [level for level in levels if level > 1e-5]
    if len(waves) < 2 or not usable:
        return waves
    target = float(np.median(usable))
    matched: list[np.ndarray] = []
    for wave, level in zip(waves, levels):
        if level <= 1e-5:
            matched.append(wave)
            continue
        # Gain is clamped between 0.5 and 2.0 to avoid amplifying near-silent chunks into noise.
        gain = min(max(target / level, 0.5), 2.0)
        scaled = wave * gain
        peak = float(np.max(np.abs(scaled))) if scaled.size else 0.0
        # Peak limit to avoid clipping.
        if peak > ceiling:
            scaled = scaled * (ceiling / peak)
        matched.append(scaled.astype(np.float32, copy=False))
    return matched


def join_chunks(waves: list[np.ndarray], sample_rate: int, silence_ms: int) -> np.ndarray:
    """Loudness-match chunks, then concatenate with silence and no trailing pad."""
    if not waves:
        raise ValueError("join_chunks requires at least one wave")
    if len(waves) == 1:
        return waves[0].astype(np.float32, copy=False)
    leveled = match_loudness(waves)
    gap = np.zeros(int(sample_rate * silence_ms / 1000), dtype=np.float32)
    pieces: list[np.ndarray] = []
    for index, wave in enumerate(leveled):
        if index:
            pieces.append(gap)
        pieces.append(wave.astype(np.float32, copy=False))
    # No silence is appended after the final chunk; pauses belong at sentence boundaries.
    return np.concatenate(pieces).astype(np.float32, copy=False)


def resample(wave: np.ndarray, src_sr: int, dst_sr: int) -> np.ndarray:
    """Resample wave from src_sr to dst_sr using high-quality resampling."""
    if src_sr == dst_sr:
        return wave.astype(np.float32, copy=False)
    return soxr.resample(wave, src_sr, dst_sr).astype(np.float32, copy=False)


def to_flac_bytes(wave: np.ndarray, sample_rate: int) -> bytes:
    """Encode wave as mono FLAC at 16-bit precision."""
    buffer = io.BytesIO()
    sf.write(buffer, wave, sample_rate, format="FLAC", subtype="PCM_16")
    return buffer.getvalue()


def duration_seconds(wave: np.ndarray, sample_rate: int) -> float:
    """Return duration of wave in seconds."""
    return len(wave) / sample_rate
