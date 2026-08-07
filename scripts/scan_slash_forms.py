"""Catalogue every `x/y` form in the corpus, with context and current handling.

Slashes carry at least five different meanings in this corpus — fractions, rates,
alternatives, dates, abbreviation pairs — and each needs a different spoken form.
This finds all of them so the rules can be checked against reality.

    python3 scripts/scan_slash_forms.py output_full/vietnamese > /tmp/slash.json
"""

from __future__ import annotations

import collections
import json
import pathlib
import re
import sys
import time

sys.set_int_max_str_digits(100_000)
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

_W = "0-9A-Za-zÀ-ỹ"
# One token, a slash, another token. Interior . , % ° - are allowed so "38.5/2",
# "5-6/10" and "1.500.000/tháng" are captured whole rather than split.
_SLASH = re.compile(rf"[{_W}][{_W}.,%°-]*\s*/\s*[{_W}][{_W}.,%°-]*")
_TRAILING = re.compile(r"[.,;:]+$")
_SENTENCE = re.compile(r"[^.!?]*$")

_DIGIT = re.compile(r"\d")
_ALPHA = re.compile(rf"[A-Za-zÀ-ỹ]")


def classify(form: str) -> str:
    """Group by what the two sides are — the thing that decides how it is read."""
    left, _, right = form.partition("/")
    ln, la = bool(_DIGIT.search(left)), bool(_ALPHA.search(left))
    rn, ra = bool(_DIGIT.search(right)), bool(_ALPHA.search(right))
    if ln and not la and rn and not ra:
        return "number / number"
    if la and not ln and ra and not rn:
        return "word / word"
    if ln and not la and ra and not rn:
        return "number / word"
    if la and not ln and rn and not ra:
        return "word / number"
    return "mixed alphanumeric"


def context(text: str, start: int, end: int, width: int = 90) -> str:
    """A short readable snippet around the match, preferring the sentence it sits in."""
    left = max(0, start - width)
    head = _SENTENCE.search(text[left:start]).group()
    tail = text[end:end + width].split(".")[0]
    return re.sub(r"\s+", " ", f"{head}{text[start:end]}{tail}").strip()


def scan(root: pathlib.Path) -> dict:
    counts: collections.Counter = collections.Counter()
    contexts: dict[str, str] = {}
    files = total = 0
    started = time.time()

    for path in root.rglob("*.txt"):
        files += 1
        text = path.read_text(errors="replace")
        for match in _SLASH.finditer(text):
            form = _TRAILING.sub("", re.sub(r"\s*/\s*", "/", match.group()))
            if "/" not in form or form.endswith("/") or form.startswith("/"):
                continue
            counts[form] += 1
            total += 1
            if form not in contexts:
                contexts[form] = context(text, match.start(), match.end())
        if files % 100_000 == 0:
            print(f"  {files:,} files, {len(counts):,} distinct",
                  file=sys.stderr, flush=True)

    return {
        "files": files,
        "occurrences": total,
        "distinct": len(counts),
        "seconds": round(time.time() - started, 1),
        "forms": [
            {"form": f, "count": c, "kind": classify(f), "context": contexts[f]}
            for f, c in counts.most_common()
        ],
    }


if __name__ == "__main__":
    root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "output_full/vietnamese")
    json.dump(scan(root), sys.stdout, ensure_ascii=False)
