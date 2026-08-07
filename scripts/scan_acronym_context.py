"""Capture real usage sentences for every acronym the corpus contains.

The earlier scan stored the first 160 chars of each file, so many "examples" did
not contain their own token. This captures the sentence AROUND each match, which
is what you need to decide how an acronym should be spoken.

    python3 scripts/scan_acronym_context.py > /tmp/acronym_context.json
"""

from __future__ import annotations

import json
import pathlib
import re
import sys
import time

sys.set_int_max_str_digits(100_000)
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

WANT_CONTEXTS = 3  # a few per acronym, so ambiguous ones can be judged


def build(scan_path: str) -> list[str]:
    scan = json.load(open(scan_path))
    return [token for token, _ in scan["acronyms"]]


def scan(root: pathlib.Path, tokens: list[str]) -> dict:
    # One alternation, longest-first so CCCD is not matched as CC.
    pattern = re.compile(r"(?<![A-Za-z0-9])(" +
                         "|".join(sorted(map(re.escape, tokens), key=len, reverse=True)) +
                         r")(?![A-Za-z0-9])")
    contexts: dict[str, list[str]] = {t: [] for t in tokens}
    outstanding = set(tokens)
    files = 0
    started = time.time()

    for path in root.rglob("*.txt"):
        files += 1
        text = path.read_text(errors="replace")
        for match in pattern.finditer(text):
            token = match.group(1)
            bucket = contexts[token]
            if len(bucket) >= WANT_CONTEXTS:
                continue
            left = max(0, match.start() - 90)
            # Prefer the sentence the token sits in.
            head = re.split(r"(?<=[.!?])\s", text[left:match.start()])[-1]
            tail = re.split(r"(?<=[.!?])\s", text[match.end():match.end() + 110])[0]
            snippet = re.sub(r"\s+", " ", f"{head}{match.group(1)}{tail}").strip()
            if snippet not in bucket:
                bucket.append(snippet)
                if len(bucket) >= WANT_CONTEXTS:
                    outstanding.discard(token)
        if not outstanding:
            break
        if files % 100_000 == 0:
            print(f"  {files:,} files, {len(outstanding)} acronyms still short",
                  file=sys.stderr, flush=True)

    return {
        "files_scanned": files,
        "seconds": round(time.time() - started, 1),
        "still_short": sorted(outstanding),
        "contexts": contexts,
    }


if __name__ == "__main__":
    tokens = build("docs/edge-case-scan.json")
    json.dump(scan(pathlib.Path("output_full/vietnamese"), tokens),
              sys.stdout, ensure_ascii=False)
