"""Materialize a reference-speaker pool into the layout load_pool expects.

Every source lands in the same shape:

    <dest>/processed_audio_by_id/<speaker_id>.wav
    <dest>/processed_audio_by_id/metadata.csv

ViSEC already ships this way, so it needs no conversion -- point config at it.
VIVOS ships as a single Parquet with embedded audio, so build_vivos_refs unpacks
it. Because both end up identical on disk, nothing downstream of load_pool knows
which corpus it is reading, and switching between them is a config edit.
"""

from __future__ import annotations

import csv
import io
from pathlib import Path

VIVOS_REPO = "christian-hoang-04/vivos-processed"
VIVOS_PARQUET = "data/references/train-00000-of-00001.parquet"

# Superset of what load_pool reads. ViSEC's own CSV is a subset of these columns;
# the reader treats everything beyond speaker_id/output_path/duration_seconds as
# optional, so neither file needs to carry the other's fields.
_COLUMNS = (
    "speaker_id",
    "output_path",
    "duration_seconds",
    "clip_count",
    "emotions",
    "unique_source_duration_seconds",
    "gender",
    "transcript",
)


def build_vivos_refs(dest: Path, target_seconds: int = 10) -> int:
    """Download the VIVOS reference Parquet and write one WAV per speaker.

    VIVOS carries nested 5/10/15/20/30 s variants per speaker; target_seconds picks
    one, giving exactly one reference per speaker as ViSEC has. Returns the count.
    """
    import pyarrow.parquet as pq
    from huggingface_hub import hf_hub_download

    table = pq.read_table(
        hf_hub_download(VIVOS_REPO, VIVOS_PARQUET, repo_type="dataset")
    )
    rows = [r for r in table.to_pylist() if r["target_seconds"] == target_seconds]
    if not rows:
        available = sorted({r["target_seconds"] for r in table.to_pylist()})
        raise ValueError(
            f"no VIVOS references with target_seconds={target_seconds}; "
            f"available: {available}"
        )

    audio_dir = Path(dest) / "processed_audio_by_id"
    audio_dir.mkdir(parents=True, exist_ok=True)

    written = []
    for row in sorted(rows, key=lambda r: r["speaker_id"]):
        speaker_id = row["speaker_id"]
        name = f"{speaker_id}.wav"
        # The Parquet stores encoded WAV bytes; write them through untouched so the
        # reference audio the engine sees is bit-identical to what was published.
        (audio_dir / name).write_bytes(row["audio"]["bytes"])
        written.append(
            {
                "speaker_id": speaker_id,
                "output_path": f"processed_audio_by_id/{name}",
                "duration_seconds": f"{row['actual_seconds']:.3f}",
                "clip_count": len(row["source_clip_ids"].split()),
                "emotions": "",  # VIVOS is read speech and carries no emotion labels
                # Whole source utterances are retained, so the file's own duration
                # is genuinely unique material -- unlike ViSEC, where some
                # references are short clips looped to length.
                "unique_source_duration_seconds": f"{row['actual_seconds']:.3f}",
                "gender": row["gender"],
                "transcript": row["transcript"],
            }
        )

    with (audio_dir / "metadata.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=_COLUMNS)
        writer.writeheader()
        writer.writerows(written)
    return len(written)
