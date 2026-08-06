"""Scan the whole corpus for tokens that survive normalization unverbalized.

Anything still non-Vietnamese in `text_spoken` is what the TTS model has to guess
at: acronyms, units the unit table misses, drug names, stray symbols. Run:

    python3 scripts/scan_edge_cases.py output_full/vietnamese > /tmp/edge.json
"""

from __future__ import annotations

import collections
import json
import pathlib
import re
import sys
import time

sys.set_int_max_str_digits(100_000)
# Run from anywhere: the package lives at the repo root, not beside this file.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from meddies_tts.textprep import VietnameseNormalizer  # noqa: E402
from meddies_tts.vietnamese_numbers import Dialect  # noqa: E402

# Vietnamese letters, including every diacritic form.
_VI = "a-zà-ỹA-ZÀ-Ỹ"
_TOKEN = re.compile(rf"[{_VI}0-9][{_VI}0-9./%°-]*")
# 2+ consecutive capitals = acronym (AMH, NSTEMI, LVEF, INR, MELD...)
_ACRONYM = re.compile(r"^[A-Z][A-Z0-9]+$")
# Letter+digit mixes that the identifier guard protects (B12, T2, HbA1c)
_ALNUM = re.compile(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z0-9]+$")
_HAS_DIGIT = re.compile(r"\d")
# A token carrying no Vietnamese diacritic and no lowercase-only shape is likely
# foreign (drug names, English terms). Diacritics are the cheapest signal.
_DIACRITIC = re.compile(r"[àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩị"
                        r"òóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ"
                        r"ÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊ"
                        r"ÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴĐ]")
_SYMBOL = re.compile(rf"[^\s{_VI}0-9.,]")

# Common Vietnamese words with no diacritic — excluded so they don't swamp the
# "foreign word" bucket.
_BARE_VI = {
    "anh", "chi", "em", "ban", "cho", "co", "khong", "la", "toi", "va", "cua",
    "cac", "nay", "do", "de", "khi", "hay", "con", "ma", "thi", "hoac", "nen",
    "can", "sau", "truoc", "trong", "ngoai", "tren", "duoi", "ra", "vao", "len",
    "he", "so", "am", "an", "at", "on", "in", "no", "to", "be", "we", "it",
}


def scan(root: pathlib.Path) -> dict:
    norm = VietnameseNormalizer(Dialect("linh", "nghìn", "tư")).normalize
    acronyms: collections.Counter = collections.Counter()
    alnum: collections.Counter = collections.Counter()
    foreign: collections.Counter = collections.Counter()
    symbols: collections.Counter = collections.Counter()
    digits_left: collections.Counter = collections.Counter()
    examples: dict[str, str] = {}
    files = errors = 0
    started = time.time()

    for path in root.rglob("*.txt"):
        files += 1
        try:
            spoken = norm(path.read_text(errors="replace"))
        except Exception:
            errors += 1
            continue
        if not spoken:
            continue
        for symbol in _SYMBOL.findall(spoken):
            symbols[symbol] += 1
        for token in _TOKEN.findall(spoken):
            if _ACRONYM.match(token):
                acronyms[token] += 1
                examples.setdefault(token, spoken[:160])
            elif _ALNUM.match(token):
                alnum[token] += 1
                examples.setdefault(token, spoken[:160])
            elif _HAS_DIGIT.search(token):
                # Digits should be gone after verbalization; anything left is a
                # rule gap, not a stylistic choice.
                digits_left[token] += 1
                examples.setdefault(token, spoken[:160])
            elif (not _DIACRITIC.search(token) and len(token) > 2
                  and token.lower() not in _BARE_VI):
                foreign[token] += 1
                examples.setdefault(token, spoken[:160])
        if files % 50_000 == 0:
            rate = files / (time.time() - started)
            print(f"  {files:,} files ({rate:.0f}/s)", file=sys.stderr, flush=True)

    return {
        "files": files,
        "errors": errors,
        "seconds": round(time.time() - started, 1),
        "acronyms": acronyms.most_common(400),
        "alnum": alnum.most_common(200),
        "foreign": foreign.most_common(400),
        "digits_left": digits_left.most_common(100),
        "symbols": symbols.most_common(60),
        "examples": examples,
    }


if __name__ == "__main__":
    root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "output_full/vietnamese")
    json.dump(scan(root), sys.stdout, ensure_ascii=False)
