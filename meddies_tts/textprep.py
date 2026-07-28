# meddies_tts/textprep.py
from __future__ import annotations

import re
from typing import Protocol

from num2words import num2words

from meddies_tts.vietnamese_numbers import (
    NORTHERN,
    Dialect,
    decimal_to_words,
    digits_to_words,
    number_to_words,
)

_WHITESPACE = re.compile(r"\s+")

# --- leaked reasoning blocks -------------------------------------------------
# Upstream bug: meddies/think_strip.py only knows the literal <think>/</think>
# pair, so other reasoning tags (and unclosed <think>) survive into output_full.
# Measured: 2.77% of Vietnamese utterances carry one, and in 100% of those a real
# utterance is underneath -- so strip, never reject.
_RNAME = r"think|thinking|internal[_ ]?reasoning|phase[_ ]?check|reasoning|tool_call"
_RTAG = rf"<\s*/?\s*(?:{_RNAME})\s*[>\"\]]?"
_REASON_BLOCK = re.compile(rf"{_RTAG}.*?<\s*/\s*(?:{_RNAME})\s*[>\"\]]?", re.DOTALL | re.I)
_REASON_TAG = re.compile(_RTAG, re.I)
_TAG_FRAGMENT = re.compile(r"^[A-Za-z_]{0,12}[>\"\]]\s*")

# --- markdown ---------------------------------------------------------------
_BOLD = re.compile(r"\*{1,3}")
_BULLET = re.compile(r"(?:(?<=\n)|^)\s*[-*•]\s+", re.MULTILINE)
_ORDERED = re.compile(r"(?:(?<=\n)|^)\s*\d+[.)]\s+", re.MULTILINE)
_HEADING = re.compile(r"(?:(?<=\n)|^)\s*#{1,6}\s*", re.MULTILINE)
_NUMBER = re.compile(r"\d+(?:\.\d+)?")

# --- numeric vocabulary (unit list measured from the corpus) ----------------
_HOTLINES = {"113", "114", "115", "911"}
_UNITS = {
    "mg": "mi-li-gam", "mcg": "mi-crô-gam", "µg": "mi-crô-gam", "g": "gam",
    "kg": "ki-lô-gam", "ml": "mi-li-lít", "l": "lít", "lít": "lít", "cc": "xê-xê",
    "cm": "xen-ti-mét", "mm": "mi-li-mét", "m": "mét", "km": "ki-lô-mét",
    "mmhg": "mi-li-mét thuỷ ngân", "iu": "đơn vị quốc tế", "kcal": "ki-lô-ca-lo",
    "°c": "độ C", "%": "phần trăm", "h": "giờ",
    "viên": "viên", "lần": "lần", "gói": "gói", "ống": "ống", "giọt": "giọt",
    "ly": "ly", "bữa": "bữa",
}
_UNIT_ALT = (
    "°C|%|mmHg|kcal|mcg|µg|mg|ml|kg|km|cm|mm|IU|cc|lít|viên|gói|ống|giọt|ly|bữa|lần"
    "|[gmlh]"
)
_PERIODS = {
    "ngày": "mỗi ngày", "tuần": "mỗi tuần", "tháng": "mỗi tháng", "giờ": "mỗi giờ",
    "phút": "mỗi phút", "lần": "mỗi lần", "buổi": "mỗi buổi", "năm": "mỗi năm",
}
_MEASURES = "lần|lít|phút|tiếng|giờ|ngày|tháng|tuần|nước|viên|gói|ống|ly|bữa|ml|mg|g|kg"
# Letters glued (optionally via hyphen) to digits are identifiers -- B12, T4,
# HbA1c, N95, SpO2, COVID-19 -- and must never be verbalized.
_IDENT = re.compile(r"\b[A-Za-zÀ-ỹ]+-?\d+[A-Za-z0-9]*\b")


def _strip_reasoning_tags(text: str) -> str:
    # Shared by strip_reasoning and strip_markup, without collapsing whitespace
    # yet -- strip_markup's bullet/ordered/heading regexes are newline-anchored
    # and need the original line breaks to still be there when they run.
    out = _REASON_BLOCK.sub(" ", text)
    out = _REASON_TAG.sub(" ", out)
    return _TAG_FRAGMENT.sub("", out.lstrip())


def strip_reasoning(text: str) -> str:
    """Remove leaked reasoning blocks. Never deletes text after an unmatched open tag."""
    return _WHITESPACE.sub(" ", _strip_reasoning_tags(text)).strip()


def strip_markup(text: str) -> str:
    """Remove reasoning leakage and markdown, then collapse whitespace."""
    without = _strip_reasoning_tags(text)
    without = _HEADING.sub("", without)
    without = _ORDERED.sub("", without)
    without = _BULLET.sub("", without)
    without = _BOLD.sub("", without)
    return _WHITESPACE.sub(" ", without).strip()


class Normalizer(Protocol):
    def normalize(self, text: str) -> str:
        """Convert raw corpus text into exactly what the TTS model should speak."""
        ...


def _unit(token: str) -> str:
    return _UNITS.get(token.lower().strip(), token)


def _int_or_decimal(token: str, dialect: Dialect) -> str:
    return (decimal_to_words(token, dialect) if re.search(r"[.,]", token)
            else number_to_words(int(token), dialect))


def _slot(index: int) -> str:
    """Digit-free sentinel -- a numeric placeholder would itself get verbalized."""
    letters = ""
    index += 1
    while index:
        index, rem = divmod(index - 1, 26)
        letters = chr(ord("A") + rem) + letters
    return f"\x00{letters}\x00"


def _normalize_numbers(text: str, dialect: Dialect = NORTHERN) -> str:
    """The measured rules, applied most-specific first."""
    saved: list[str] = []

    def stash(match: re.Match) -> str:
        saved.append(match.group(0))
        return _slot(len(saved) - 1)

    out = _IDENT.sub(stash, text)                       # protect B12, COVID-19, HbA1c
    out = re.sub(r">\s*(?=\d)", "trên ", out)
    out = re.sub(r"<\s*(?=\d)", "dưới ", out)
    # range-fraction ("6-7/10") must run before the bare fraction rule, or the
    # trailing "/10" would be consumed as a plain a/b fraction of just "7/10".
    out = re.sub(
        r"(\d+)\s*-\s*(\d+)\s*/\s*(\d+)",
        lambda m: f"{number_to_words(int(m[1]), dialect)} đến {number_to_words(int(m[2]), dialect)} "
                  f"trên {number_to_words(int(m[3]), dialect)}", out)
    # number+unit-per-period ("1000mg/ngày") before the bare fraction rule, or
    # the "/ngày" would never match (ngày isn't a number) and 1000mg/ would be
    # split incorrectly by the unit rule below.
    out = re.sub(
        rf"(\d+(?:[.,]\d+)?)\s*({_UNIT_ALT})\s*/\s*({'|'.join(_PERIODS)})",
        lambda m: f"{_int_or_decimal(m[1], dialect)} {_unit(m[2])} {_PERIODS[m[3]]}", out)
    # bare fraction ("140/90") before the bare-integer rule, or D/D becomes two
    # separate numbers with a literal slash left between them.
    out = re.sub(
        rf"(\d+)\s*/\s*(\d+)\s*({_UNIT_ALT})?",
        lambda m: f"{number_to_words(int(m[1]), dialect)} trên {number_to_words(int(m[2]), dialect)}"
                  + (f" {_unit(m[3])}" if m[3] else ""), out)
    out = re.sub(
        r"(?<![\d/])(\d+)\s*-\s*(\d+)(?![\d/])",
        lambda m: f"{number_to_words(int(m[1]), dialect)} đến {number_to_words(int(m[2]), dialect)}", out)
    out = re.sub(
        rf"(\d+[.,]\d+)\s*({_UNIT_ALT})?",
        lambda m: decimal_to_words(m[1], dialect) + (f" {_unit(m[2])}" if m[2] else ""), out)
    out = re.sub(
        rf"(\d+)\s*({_UNIT_ALT})(?![A-Za-zÀ-ỹ])",
        lambda m: f"{number_to_words(int(m[1]), dialect)} {_unit(m[2])}", out)
    out = re.sub(
        r"\b\d+\b",
        lambda m: digits_to_words(m[0]) if m[0] in _HOTLINES else number_to_words(int(m[0]), dialect),
        out)
    # "phút/ngày" -> "phút mỗi ngày". The right side MUST be a period word, or
    # "anh/chị" (9,760 occurrences) would become "anh mỗi chị".
    out = re.sub(
        rf"\b({_MEASURES})\s*/\s*({'|'.join(_PERIODS)})\b",
        lambda m: f"{m[1]} {_PERIODS[m[2]]}", out)
    # any other word/word slash reads naturally as a space: "anh/chị" -> "anh chị"
    out = re.sub(r"(?<=[A-Za-zÀ-ỹ])\s*/\s*(?=[A-Za-zÀ-ỹ])", " ", out)

    for index, original in enumerate(saved):
        out = out.replace(_slot(index), original)
    return _WHITESPACE.sub(" ", out).strip()


class VietnameseNormalizer:
    """Strip reasoning leakage and markup, then verbalize numbers and units.

    The dialect comes from the speaker (Task 7), so one instance is built per
    speaker_id rather than one per config.
    """

    def __init__(self, dialect: Dialect = NORTHERN) -> None:
        self._dialect = dialect

    def normalize(self, text: str) -> str:
        """Turn raw Vietnamese corpus text into what the TTS model should speak."""
        stripped = strip_markup(text)
        return _normalize_numbers(stripped, self._dialect) if stripped else ""


class EnglishNormalizer:
    """Strip markup, then verbalize numbers with num2words."""

    def normalize(self, text: str) -> str:
        """Turn raw English corpus text into what the TTS model should speak."""
        stripped = strip_markup(text)
        if not stripped:
            return ""
        spoken = _NUMBER.sub(lambda m: _say_english(m.group(0)), stripped)
        return _WHITESPACE.sub(" ", spoken).strip()


def _say_english(token: str) -> str:
    if "." in token:
        whole, _, frac = token.partition(".")
        return f"{num2words(int(whole))} point {' '.join(num2words(int(d)) for d in frac)}"
    return num2words(int(token))


def get_normalizer(config: str, dialect: Dialect | None = None) -> Normalizer:
    """Return the language-appropriate normalizer for a config name ('vietnamese'/'english')."""
    if config == "vietnamese":
        return VietnameseNormalizer(dialect or NORTHERN)
    if config == "english":
        return EnglishNormalizer()
    raise ValueError(f"no normalizer for config {config!r}")
