from __future__ import annotations

from dataclasses import dataclass

import numpy as np

DEFAULT_CHARS_PER_SEC = 14.0


@dataclass(frozen=True)
class QCResult:
    ok: bool
    reason: str | None = None
    detail: str = ""


_OK = QCResult(True)


def check_audio(
    wave: np.ndarray,
    sample_rate: int,
    n_chars: int,
    chars_per_sec: float = DEFAULT_CHARS_PER_SEC,
    min_ratio: float = 0.3,
    max_ratio: float = 3.0,
    silence_rms: float = 1e-4,
) -> QCResult:
    """Cheap sanity checks catching dead, truncated and runaway generations."""
    if wave.size == 0:
        return QCResult(False, "empty", "generated 0 samples")
    # Check not_finite before silent: a NaN array would otherwise be misreported
    # as "silent" rather than the actual defect. The FLAC encoder silently
    # converts NaN to 0.0, so we must catch it here on the raw float array.
    if not np.all(np.isfinite(wave)):
        return QCResult(False, "not_finite", "wave contains NaN or inf")
    rms = float(np.sqrt(np.mean(np.square(wave, dtype=np.float64))))
    if rms < silence_rms:
        return QCResult(False, "silent", f"rms={rms:.2e} < {silence_rms:.0e}")
    if n_chars <= 0:
        return QCResult(False, "no_text", "utterance has no spoken text")

    duration = wave.size / sample_rate
    expected = n_chars / chars_per_sec
    ratio = duration / expected
    if ratio < min_ratio:
        return QCResult(
            False, "too_short", f"{duration:.1f}s vs expected {expected:.1f}s (x{ratio:.2f})"
        )
    if ratio > max_ratio:
        return QCResult(
            False, "too_long", f"{duration:.1f}s vs expected {expected:.1f}s (x{ratio:.2f})"
        )
    return _OK
