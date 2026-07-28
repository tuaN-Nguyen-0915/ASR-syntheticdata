from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from meddies_tts.config import TextConfig

_MIN_WORDS_FOR_DEGENERACY = 200


@dataclass(frozen=True)
class Rejection:
    reason: str
    detail: str


def type_token_ratio(text: str) -> float:
    """Return the ratio of unique to total tokens (words) in text."""
    words = text.split()
    if not words:
        return 1.0
    return len(set(words)) / len(words)


def max_ngram_repeat(text: str, n: int = 5) -> int:
    """Return the highest frequency of any contiguous n-gram."""
    words = text.split()
    if len(words) < n * 2:
        return 1
    # Count all contiguous n-grams and return the highest frequency.
    grams = Counter(tuple(words[i : i + n]) for i in range(len(words) - n + 1))
    return grams.most_common(1)[0][1]


def check(text: str, cfg: TextConfig) -> Rejection | None:
    """Return a Rejection if the utterance must not be synthesized, else None."""
    if len(text) > cfg.max_chars:
        return Rejection("too_long", f"{len(text)} chars > max_chars={cfg.max_chars}")

    words = text.split()
    if len(words) <= _MIN_WORDS_FOR_DEGENERACY:
        return None

    ttr = type_token_ratio(text)
    if ttr >= cfg.min_ttr:
        return None

    repeat = max_ngram_repeat(text)
    if repeat < cfg.max_ngram_repeat:
        return None

    return Rejection(
        "degenerate",
        f"words={len(words)} ttr={ttr:.3f}<{cfg.min_ttr} max_5gram_repeat={repeat}",
    )
