# meddies_tts/vietnamese_numbers.py
"""Vietnamese number verbalization with per-speaker dialect. Pure Python."""
from __future__ import annotations

import random
from dataclasses import dataclass

_DIGITS = ("không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín")


@dataclass(frozen=True)
class Dialect:
    zero_filler: str   # "linh" (Northern) | "lẻ" (Southern)
    thousand: str      # "nghìn" (Northern) | "ngàn" (Southern)
    four: str           # "tư" | "bốn"


NORTHERN = Dialect("linh", "nghìn", "tư")
SOUTHERN = Dialect("lẻ", "ngàn", "tư")

# Coupled on purpose: no real speaker says "linh" alongside "ngàn".
_REGIONS = (("linh", "nghìn"), ("lẻ", "ngàn"))


def dialect_from_seed(seed: int) -> Dialect:
    """Pick a dialect deterministically. Caller seeds from speaker_id (Task 7)."""
    rng = random.Random(seed)
    zero_filler, thousand = rng.choice(_REGIONS)
    return Dialect(zero_filler, thousand, rng.choice(("tư", "bốn")))


def digits_to_words(text: str) -> str:
    """Read each digit separately: '115' -> 'một một năm'. Used for hotlines."""
    return " ".join(_DIGITS[int(ch)] for ch in text if ch.isdigit())


def _tens(n: int, dialect: Dialect) -> str:
    if n < 10:
        return _DIGITS[n]
    if n < 20:
        unit = n % 10
        if unit == 0:
            return "mười"
        return "mười " + ("lăm" if unit == 5 else _DIGITS[unit])
    ten, unit = divmod(n, 10)
    out = f"{_DIGITS[ten]} mươi"
    if unit == 1:
        return out + " mốt"
    if unit == 4:
        return out + f" {dialect.four}"
    if unit == 5:
        return out + " lăm"
    return out + (f" {_DIGITS[unit]}" if unit else "")


def _hundreds(n: int, dialect: Dialect, force_hundred: bool) -> str:
    hundred, rest = divmod(n, 100)
    if hundred == 0 and not force_hundred:
        return _tens(rest, dialect)
    if rest == 0:
        return f"{_DIGITS[hundred]} trăm"
    tail = (
        f"{dialect.zero_filler} {_DIGITS[rest]}" if rest < 10 else _tens(rest, dialect)
    )
    return f"{_DIGITS[hundred]} trăm {tail}"


def number_to_words(n: int, dialect: Dialect = NORTHERN) -> str:
    """Convert an integer to Vietnamese words in the given regional dialect."""
    if n < 0:
        return "âm " + number_to_words(-n, dialect)
    if n < 100:
        return _tens(n, dialect)
    if n < 1000:
        return _hundreds(n, dialect, force_hundred=True)
    parts: list[str] = []
    # Walk billions -> millions -> thousands, only emitting "không trăm" filler
    # for a lower group once a higher group has already been emitted.
    for name, size in (("tỷ", 10**9), ("triệu", 10**6), (dialect.thousand, 10**3)):
        if n >= size:
            group, n = divmod(n, size)
            # A group can itself exceed 999 once the whole number is >= 10**12
            # (e.g. 10**12 // 10**9 == 1000): recurse instead of handing it to
            # _hundreds, which assumes a single 0-999 chunk and would otherwise
            # index _DIGITS out of range. Only the leading (tỷ) group can ever
            # be this large, since every later group is n mod 10**9 or smaller.
            words = (number_to_words(group, dialect) if group >= 1000
                     else _hundreds(group, dialect, force_hundred=bool(parts)))
            parts.append(f"{words} {name}")
    if n:
        parts.append(_hundreds(n, dialect, force_hundred=True))
    return " ".join(parts)


def decimal_to_words(text: str, dialect: Dialect = NORTHERN) -> str:
    """'38.5' / '38,5' -> 'ba mươi tám phẩy năm' (fraction read digit by digit)."""
    whole, _, frac = text.replace(",", ".").partition(".")
    words = number_to_words(int(whole), dialect)
    return f"{words} phẩy {digits_to_words(frac)}" if frac else words
