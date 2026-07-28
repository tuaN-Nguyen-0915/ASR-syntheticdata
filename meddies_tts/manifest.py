from __future__ import annotations

import re
from collections.abc import Iterator, Sequence
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

MANIFEST_SCHEMA = pa.schema(
    [
        pa.field("config", pa.string()),
        pa.field("disease_slug", pa.string()),
        pa.field("disease_name", pa.string()),
        pa.field("conv_id", pa.string()),
        pa.field("turn", pa.int32()),
        pa.field("role", pa.string()),
        pa.field("text_raw", pa.string()),
    ]
)

_ROLES = ("assistant", "user")
_TURN_RE = re.compile(r"^Turn(\d+)$")


def _disease_name(disease_dir: Path) -> str:
    name_file = disease_dir / "_disease_name.txt"
    if not name_file.exists():
        return disease_dir.name
    first = name_file.read_text(encoding="utf-8").strip().splitlines()
    return first[0].strip() if first else disease_dir.name


def iter_utterances(output_root: Path, configs: Sequence[str]) -> Iterator[dict]:
    """Yield one dict per utterance file, in stable sorted order."""
    root = Path(output_root)
    for config in configs:
        config_dir = root / config
        if not config_dir.is_dir():
            continue
        for disease_dir in sorted(p for p in config_dir.iterdir() if p.is_dir()):
            disease_name = _disease_name(disease_dir)
            for conv_dir in sorted(p for p in disease_dir.iterdir() if p.is_dir()):
                turn_dirs = []
                for turn_dir in conv_dir.iterdir():
                    match = _TURN_RE.match(turn_dir.name)
                    if turn_dir.is_dir() and match:
                        turn_dirs.append((int(match.group(1)), turn_dir))
                for turn, turn_dir in sorted(turn_dirs):
                    for role in _ROLES:
                        text_file = turn_dir / f"{role}.txt"
                        if not text_file.exists():
                            continue
                        yield {
                            "config": config,
                            "disease_slug": disease_dir.name,
                            "disease_name": disease_name,
                            "conv_id": conv_dir.name,
                            "turn": turn,
                            "role": role,
                            "text_raw": text_file.read_text(encoding="utf-8").strip(),
                        }


def build_manifest(output_root: Path, configs: Sequence[str]) -> pa.Table:
    """Build a Parquet table from utterances in the output tree."""
    rows = list(iter_utterances(output_root, configs))
    columns = {name: [row[name] for row in rows] for name in MANIFEST_SCHEMA.names}
    return pa.Table.from_pydict(columns, schema=MANIFEST_SCHEMA)


def write_manifest(table: pa.Table, path: Path) -> None:
    """Write a manifest table to Parquet with zstd compression."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(table, path, compression="zstd")


def read_manifest(path: Path) -> pa.Table:
    """Read a manifest table from Parquet."""
    return pq.read_table(path)
