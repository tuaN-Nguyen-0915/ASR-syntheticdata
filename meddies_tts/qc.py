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
    # Calibrated against the 54-utterance pilot, not guessed: observed ratios were
    # median 0.99, stdev 0.25, spanning 0.77-1.64 for utterances that sound correct.
    # The one degenerate generation (the model babbling past the end of a 52-char
    # line, 7.8s where 3.1s was due) sat at 2.51 -- and sailed through the original
    # 0.3/3.0 bounds, which were wide enough that nothing could ever trip them.
    # 0.6/2.0 keeps ~1.5x margin around the observed good range on both sides.
    # A rejection costs one reseeded regeneration, not a dropped utterance, so
    # erring tight is cheap; erring loose ships garbage.
    min_ratio: float = 0.6,
    max_ratio: float = 2.0,
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
    # Check silent before no_text: if both conditions hold, silent is the more useful
    # signal — a completely silent utterance cannot be listened to regardless of
    # whether it has text or not.
    if rms < silence_rms:
        return QCResult(False, "silent", f"rms={rms:.2e} < {silence_rms:.0e}")
    if n_chars <= 0:
        return QCResult(False, "no_text", "utterance has no spoken text")

    # Guard against bad parameters before division.
    if sample_rate <= 0:
        return QCResult(False, "bad_params", f"sample_rate={sample_rate} must be positive")
    if chars_per_sec <= 0:
        return QCResult(False, "bad_params", f"chars_per_sec={chars_per_sec} must be positive")

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
