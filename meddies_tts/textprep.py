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
#
# Longest/most-specific alternatives first (re alternation is first-match, not
# longest-match): "internal[_ ]?reasoning" must precede "internal[_ ]?reason" or
# the shorter one wins on "<internal_reasoning>", stranding "ing>" -- the same
# class of trap documented for _UNIT_ALT/_ROMAN_ALT above.
_RNAME = (
    r"thinking|think|internal[_ ]?reasoning|internal[_ ]?reason|"
    r"external[_ ]?reasoning|phase[_ ]?check|reasoning|tool_call"
)
# Corpus tags come in mismatched bracket styles -- "(internal_reasoning) ...
# </internal_reasoning>" is a real example -- so both the opening delimiter
# ("<" or "(") and the closing delimiter (">", '"', "]", or ")") are accepted
# independently, not paired.
_OPEN = r"[<(]"
_CLOSE = r"[>\"\)\]]"
_RTAG = rf"{_OPEN}\s*/?\s*(?:{_RNAME})\s*{_CLOSE}?"
_REASON_BLOCK = re.compile(rf"{_RTAG}.*?{_OPEN}\s*/\s*(?:{_RNAME})\s*{_CLOSE}?", re.DOTALL | re.I)
_REASON_TAG = re.compile(_RTAG, re.I)
# Sweeps up a leftover fragment when an alternation above matched a SHORTER name
# than what's actually in the text (see the ordering note), e.g. a bare
# "internal_reasoning>" with no leading "<" at all -- the raw corpus contains
# exactly that shape. "internal_reasoning" is 18 chars; {0,12} was 6 short and
# left it untouched. 24 covers every _RNAME alternative with room to spare.
_TAG_FRAGMENT = re.compile(rf"^[A-Za-z_]{{0,24}}{_CLOSE}\s*")

# --- tagless leading reasoning-header blocks ---------------------------------
# The largest untagged leak shape: no "<", "(", or any bracket at all -- just a
# markdown-bold "**Internal Reasoning:**" header directly at the start of the
# text, e.g. "**Internal Reasoning:** - **Phase:** Phase 4 (Closing). -
# **Status:** ... - **Action:** ...". strip_markup's _BOLD rule would otherwise
# turn this into ordinary-looking prose instead of removing it.
#
# Removed ONLY when a safe right boundary exists in the rest of the text:
# either a real (if mismatched-bracket) closing tag, or an unambiguous
# "**Response:**"/"**Trả lời:**" marker that starts the real reply. If neither
# boundary is found, nothing is removed -- truncating a legitimate medical
# utterance is worse than leaving one leaked header in.
_HEADER_START = re.compile(r"^\s*\**\s*(?:internal|external)[_ ]?reasoning\s*:?\s*\**\s*", re.I)
_HEADER_CLOSE_TAG = re.compile(rf"{_OPEN}\s*/\s*(?:internal|external)[_ ]?reasoning\s*{_CLOSE}?", re.I)
_HEADER_RESPONSE_MARK = re.compile(r"\**\s*(?:response|trả\s+lời|reply)\s*:?\s*\**\s*", re.I)


def _strip_tagless_reasoning_header(text: str) -> str:
    """Remove a leading, tag-free reasoning header, if its right boundary is unambiguous."""
    start = _HEADER_START.match(text)
    if not start:
        return text
    rest = text[start.end():]
    close = _HEADER_CLOSE_TAG.search(rest)
    if close:
        return rest[close.end():]
    response = _HEADER_RESPONSE_MARK.search(rest)
    if response:
        return rest[response.end():]
    return text  # no safe boundary found -- leave untouched, per the module note above


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
    "m2": "mét vuông", "cm2": "xen-ti-mét vuông", "mmol": "mi-li-mol",
    "mol": "mol", "nm": "na-nô-mét",
}
# Longer/more specific alternatives must precede shorter ones they share a
# prefix with (e.g. "cm2" before "cm", "mmol" before "mm"), or the shorter one
# wins and strands the remaining characters -- re.sub alternation is
# first-match, not longest-match.
_UNIT_ALT = (
    "°C|%|mmHg|kcal|mmol|mol|mcg|µg|mg|ml|kg|km|cm2|cm|mm|nm|IU|cc|lít|viên|gói"
    "|ống|giọt|ly|bữa|lần|m2|[gmlh]"
)
_PERIODS = {
    "ngày": "mỗi ngày", "tuần": "mỗi tuần", "tháng": "mỗi tháng", "giờ": "mỗi giờ",
    "phút": "mỗi phút", "lần": "mỗi lần", "buổi": "mỗi buổi", "năm": "mỗi năm",
}
_MEASURES = "lần|lít|phút|tiếng|giờ|ngày|tháng|tuần|nước|viên|gói|ống|ly|bữa|ml|mg|g|kg"
# Letters glued (optionally via hyphen) to digits are identifiers -- B12, T4,
# HbA1c, N95, SpO2, COVID-19 -- and must never be verbalized.
_IDENT = re.compile(r"\b[A-Za-zÀ-ỹ]+-?\d+[A-Za-z0-9]*\b")

# --- Vietnamese thousands-dotted currency ("500.000đ") ----------------------
# Vietnamese groups thousands with "." (500.000 = five hundred thousand), the
# opposite of the decimal rule's "." further down. Each group after the first
# is exactly 3 digits, which is what distinguishes this from a real decimal
# like "38.5" (1 digit) or "1.25" (2 digits).
_DOTTED_THOUSANDS = r"\d{1,3}(?:\.\d{3})+"
_CURRENCY = {"đ": "đồng", "vnđ": "đồng", "vnd": "đồng"}
# Trailing \b keeps this from matching just the "đ" that starts the unrelated
# word "đồng" when the currency is already spelled out in the source text.
_CURRENCY_SYM = r"(?i:VNĐ|VND|đ)\b"

# --- Roman-numeral severity grading ("độ III", "giai đoạn II", "type I") ----
_ROMAN = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5,
          "VI": 6, "VII": 7, "VIII": 8, "IX": 9, "X": 10}
# Longest numeral first, same reasoning as _UNIT_ALT above: "I" would
# otherwise steal the first letter of "III"/"IV"/etc. before they get a turn.
_ROMAN_ALT = "VIII|III|VII|II|IV|VI|IX|I|V|X"
# Grading words measured in the corpus. A bare Roman numeral with no grading
# word in front is left alone -- far more likely to be an abbreviation, a
# list marker, or English text than a severity grade.
_GRADE_WORDS = r"giai\s+đoạn|độ|type|nhóm|cấp|mức"


def _strip_reasoning_tags(text: str) -> str:
    # Shared by strip_reasoning and strip_markup, without collapsing whitespace
    # yet -- strip_markup's bullet/ordered/heading regexes are newline-anchored
    # and need the original line breaks to still be there when they run.
    out = _strip_tagless_reasoning_header(text)
    out = _REASON_BLOCK.sub(" ", out)
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


def _dedot(token: str) -> int:
    return int(token.replace(".", ""))  # "1.500.000" -> 1500000


def _currency_suffix(symbol: str | None) -> str:
    return f" {_CURRENCY[symbol.lower()]}" if symbol else ""


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

    # Dosing shorthand ("x2/ngày") must run before identifier protection below,
    # or "x2" (letter + digits) gets mistaken for a protected identifier like
    # "B12" and survives untouched. Safe to special-case ahead of protection
    # because, unlike a real identifier, it's always followed by "/<period>".
    out = re.sub(
        rf"\bx\s?(\d+)\s*/\s*({'|'.join(_PERIODS)})\b",
        lambda m: f"{number_to_words(int(m[1]), dialect)} lần {_PERIODS[m[2]]}", text)
    out = _IDENT.sub(stash, out)                        # protect B12, COVID-19, HbA1c
    out = re.sub(r">\s*(?=\d)", "trên ", out)
    out = re.sub(r"<\s*(?=\d)", "dưới ", out)
    # Roman-numeral grading ("độ III", "type I") only right after a grading
    # word -- operates on letters, not digits, so it is independent of every
    # other rule here and can run at any point in this function.
    out = re.sub(
        rf"\b({_GRADE_WORDS})\s+({_ROMAN_ALT})\b",
        lambda m: f"{m[1]} {number_to_words(_ROMAN[m[2]], dialect)}", out)
    # dotted-thousands range ("100.000-300.000đ") before dotted-thousands single,
    # which in turn MUST run before the decimal rule below -- otherwise "." in
    # "500.000" is read as a decimal point instead of a thousands separator, and
    # a dashed pair like "100.000-300.000" gets torn apart at the dots before
    # the generic range/decimal rules even see it (see task-3 Fix 1).
    out = re.sub(
        rf"({_DOTTED_THOUSANDS})\s*-\s*({_DOTTED_THOUSANDS})(?:\s*({_CURRENCY_SYM}))?",
        lambda m: f"{number_to_words(_dedot(m[1]), dialect)} đến {number_to_words(_dedot(m[2]), dialect)}"
                  + _currency_suffix(m[3]), out)
    out = re.sub(
        rf"({_DOTTED_THOUSANDS})(?:\s*({_CURRENCY_SYM}))?",
        lambda m: number_to_words(_dedot(m[1]), dialect) + _currency_suffix(m[2]), out)
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
    # separate numbers with a literal slash left between them. The trailing
    # unit's "\s*" lives INSIDE the optional group -- outside it, re.sub still
    # consumes the space even when no unit follows, gluing the next word on
    # ("140/90 vậy" -> "...mườivậy" instead of "...mười vậy").
    out = re.sub(
        rf"(\d+)\s*/\s*(\d+)(?:\s*({_UNIT_ALT}))?",
        lambda m: f"{number_to_words(int(m[1]), dialect)} trên {number_to_words(int(m[2]), dialect)}"
                  + (f" {_unit(m[3])}" if m[3] else ""), out)
    out = re.sub(
        r"(?<![\d/])(\d+)\s*-\s*(\d+)(?![\d/])",
        lambda m: f"{number_to_words(int(m[1]), dialect)} đến {number_to_words(int(m[2]), dialect)}", out)
    # Same "\s* outside the optional group" trap as the fraction rule above --
    # keep the space inside so an unmatched unit doesn't eat the following space.
    out = re.sub(
        rf"(\d+[.,]\d+)(?:\s*({_UNIT_ALT}))?",
        lambda m: decimal_to_words(m[1], dialect) + (f" {_unit(m[2])}" if m[2] else ""), out)
    # Informal height notation ("1m72" = 1.72 m). Must run before the number+unit
    # rule below, or that rule's bare "m" fallback grabs just the leading digit
    # and strands the rest ("1m72" -> "một mét72"). The suffix digits are read
    # individually (digit-by-digit), not as a number ("72" -> "bảy hai", not
    # "bảy mươi hai"). Excludes a lone trailing "2" ("20m2") so it falls through
    # to the unit rule instead, which reads that as square meters.
    out = re.sub(
        r"\b(\d+)m(?!2\b)(\d+)\b",
        lambda m: f"{number_to_words(int(m[1]), dialect)} mét {digits_to_words(m[2])}", out)
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
