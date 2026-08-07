"""Build the editable acronym decision table.

Emits a TSV the user fills in and hands back, plus a readable markdown view with
the usage sentences needed to make each call.

    python3 scripts/build_acronym_table.py
"""

from __future__ import annotations

import csv
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

# Pre-classification is a STARTING POINT, not an answer — the contexts decide.
# Everything here was confirmed by reading real usage during the scan.
_NOT_ACRONYMS = {  # Vietnamese words appearing in shouty headers
    "NGAY", "QUAN", "AN", "KHI", "CHO", "NGUY", "PHUT", "BAN", "CAN", "LAM",
    "GIO", "SAU", "TAM", "LUON", "DUNG", "KHONG", "VIEC", "NHAT", "TOT", "MOI",
    "BAO", "THE", "NAM", "HAN", "TIM", "TAY", "MAT", "DAU", "ANH", "EM", "THEO",
    "MOT", "HAI", "BA", "NEU", "VOI", "DEN", "LEN", "RA", "VAO",
}
_LEAK = {  # reasoning scaffolding — should be stripped, never spoken
    "FIFE", "PHASE", "OPQRST", "PMH", "ROS", "ICE", "SBAR", "HPI", "DDX",
    "GATHERING", "PROVIDING", "STRUCTURE", "CLINICAL", "COMPLETE", "INFORMATION",
    "SAFETY", "OBJECTIVE", "SUMMARY", "TURN", "PATIENT", "AGE",
}
_VN_ADMIN = {  # Vietnamese acronyms normally spoken as their full phrase
    "CCCD": "căn cước công dân",
    "CMND": "chứng minh nhân dân",
    "BHYT": "bảo hiểm y tế",
    "BHXH": "bảo hiểm xã hội",
    "BV": "bệnh viện",
    "TTYT": "trung tâm y tế",
    "UBND": "uỷ ban nhân dân",
    "BYT": "bộ y tế",
}


def suggest(token: str) -> tuple[str, str]:
    """(action, proposed_output) — a suggestion to be overridden, not a decision."""
    if token in _LEAK:
        return "STRIP", ""
    if token in _NOT_ACRONYMS:
        return "LOWERCASE", token.lower()
    if token in _VN_ADMIN:
        return "EXPAND", _VN_ADMIN[token]
    return "SPELL", ""


def main() -> None:
    scan = json.load(open("docs/edge-case-scan.json"))
    ctx = json.load(open("/tmp/acronym_context.json"))["contexts"]

    rows = []
    for token, count in scan["acronyms"]:
        action, proposed = suggest(token)
        rows.append({
            "acronym": token,
            "count": count,
            "suggested_action": action,
            "proposed_spoken": proposed,
            "YOUR_ACTION": "",
            "YOUR_SPOKEN": "",
            "context_1": (ctx.get(token) or [""])[0][:160],
        })

    out_tsv = pathlib.Path("docs/acronyms-table.tsv")
    with out_tsv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)

    # Markdown view: same rows, but with every captured sentence, for judging.
    lines = ["# Acronym decision table", ""]
    lines += [
        f"{len(rows)} acronyms, {sum(r['count'] for r in rows):,} occurrences, from a full",
        f"scan of 712,881 files. Fill in **YOUR_ACTION** and **YOUR_SPOKEN** in",
        "`docs/acronyms-table.tsv` (same rows, tab-separated) and hand it back.", "",
        "`suggested_action` is a starting point only — it was derived from patterns,",
        "not from reading every context. Override freely.", "",
        "| action | meaning |",
        "|---|---|",
        "| `SPELL` | say it letter by letter |",
        "| `EXPAND` | replace with the full Vietnamese phrase (put it in YOUR_SPOKEN) |",
        "| `LOWERCASE` | not an acronym — an ordinary word in a shouty header |",
        "| `STRIP` | reasoning-scaffolding leakage; remove, never speak |",
        "| `KEEP` | leave exactly as-is for the model |",
        "",
        "---", "",
    ]
    for row in rows:
        token = row["acronym"]
        lines.append(f"### {token} — {row['count']:,}× — suggested: `{row['suggested_action']}`"
                     + (f" → `{row['proposed_spoken']}`" if row["proposed_spoken"] else ""))
        for sentence in (ctx.get(token) or ["(no context captured)"])[:3]:
            lines.append(f"- *{sentence[:180]}*")
        lines.append("")
    pathlib.Path("docs/acronyms-table.md").write_text("\n".join(lines), encoding="utf-8")

    missing = sum(1 for r in rows if not r["context_1"])
    print(f"wrote docs/acronyms-table.tsv and docs/acronyms-table.md")
    print(f"  {len(rows)} rows, {missing} without a captured context")
    from collections import Counter
    for action, n in Counter(r["suggested_action"] for r in rows).most_common():
        occ = sum(r["count"] for r in rows if r["suggested_action"] == action)
        print(f"  suggested {action:<10} {n:>4} rows  {occ:>8,} occurrences")


if __name__ == "__main__":
    main()
