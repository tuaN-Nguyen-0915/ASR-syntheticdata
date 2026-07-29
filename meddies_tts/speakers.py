from __future__ import annotations

import csv
import hashlib
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from meddies_tts.config import SpeakerConfig

_INT64_MASK = (1 << 63) - 1


def derive_seed(salt: str, *parts: object) -> int:
    """Deterministic non-negative int64 seed from a salt and identity parts."""
    # Assumption: parts must not contain '/', and callers pass fixed arity (e.g., Task 12 always uses 2 parts).
    key = "/".join([salt, *(str(part) for part in parts)]).encode("utf-8")
    digest = hashlib.blake2b(key, digest_size=8).digest()
    return int.from_bytes(digest, "big") & _INT64_MASK


@dataclass(frozen=True)
class Speaker:
    """One reference voice, corpus-agnostic.

    speaker_id is a STRING so both pools keep their native identifiers: ViSEC's
    are numeric ("0".."146"), VIVOS's are names ("VIVOSDEV01"). Mapping VIVOS to
    integers would have made the published speaker_id a meaningless index and
    pushed real provenance into a side column.

    Fields a given corpus lacks are empty, never invented: ViSEC has no
    transcripts and no gender labels; VIVOS has no emotion labels.
    """

    speaker_id: str
    wav_path: Path
    emotions: str
    unique_source_s: float
    duration_s: float
    gender: str = ""
    # Exact text of the reference audio. Only VIVOS supplies this; it is what
    # enables VoxCPM2's transcript-assisted cloning, which the spec (line 105)
    # recorded as unavailable with ViSEC.
    transcript: str = ""


def load_pool(metadata_csv: Path, allow: set[str] | None = None) -> list[Speaker]:
    """Load a reference pool from a metadata CSV; WAV paths resolve relative to its parent's parent.

    Reads both the ViSEC CSV as it ships and the CSV build-refs writes for VIVOS.
    The columns they share are required; the rest are optional, so the existing
    ViSEC directory keeps working untouched -- which is what makes switching back
    a config edit rather than a rebuild.
    """
    csv_path = Path(metadata_csv)
    root = csv_path.parent.parent
    speakers: list[Speaker] = []
    with csv_path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            speaker_id = str(row["speaker_id"])
            if allow is not None and speaker_id not in allow:
                continue
            speakers.append(
                Speaker(
                    speaker_id=speaker_id,
                    wav_path=root / row["output_path"],
                    emotions=row.get("emotions", ""),
                    # ViSEC reports how much unique source a reference represents
                    # (some are short loops padded out); VIVOS retains whole
                    # utterances, so its own duration is the honest value.
                    unique_source_s=float(
                        row.get("unique_source_duration_seconds")
                        or row["duration_seconds"]
                    ),
                    duration_s=float(row["duration_seconds"]),
                    gender=row.get("gender", ""),
                    transcript=row.get("transcript", ""),
                )
            )
    # Numeric-aware sort so ViSEC ids order 0,1,2,...,10 rather than 0,1,10,2.
    return sorted(
        speakers,
        key=lambda s: (0, int(s.speaker_id), "") if s.speaker_id.isdigit()
        else (1, 0, s.speaker_id),
    )


class SpeakerAssigner(Protocol):
    def assign(
        self, config: str, disease_slug: str, conv_id: str, turn: int, role: str
    ) -> int: ...


class _PairAssigner:
    """Draws a distinct (user, assistant) speaker pair from a scope key."""

    def __init__(self, pool: list[Speaker], salt: str) -> None:
        if len(pool) < 2:
            raise ValueError("speaker pool must contain at least 2 speakers")
        self._ids = [speaker.speaker_id for speaker in pool]
        self._salt = salt

    def _scope(self, config: str, disease_slug: str, conv_id: str, turn: int) -> tuple:
        raise NotImplementedError

    def assign(
        self, config: str, disease_slug: str, conv_id: str, turn: int, role: str
    ) -> int:
        # Role is not part of the seed: both roles in the same scope derive from one draw, ensuring they form a matched pair.
        seed = derive_seed(self._salt, *self._scope(config, disease_slug, conv_id, turn))
        # sample(self._ids, 2) draws without replacement, guaranteeing user_id != assistant_id.
        user_id, assistant_id = random.Random(seed).sample(self._ids, 2)
        return user_id if role == "user" else assistant_id


class PerConversationAssigner(_PairAssigner):
    """One speaker pair per conversation, fixed across all its turns."""

    def _scope(self, config: str, disease_slug: str, conv_id: str, turn: int) -> tuple:
        return (config, disease_slug, conv_id)


class PerTurnAssigner(_PairAssigner):
    """A fresh speaker pair for every turn."""

    def _scope(self, config: str, disease_slug: str, conv_id: str, turn: int) -> tuple:
        return (config, disease_slug, conv_id, turn)


def get_assigner(cfg: SpeakerConfig, pool: list[Speaker]) -> SpeakerAssigner:
    """Select the assignment policy from config."""
    if cfg.policy == "per_conversation":
        return PerConversationAssigner(pool, cfg.seed_salt)
    if cfg.policy == "per_turn":
        return PerTurnAssigner(pool, cfg.seed_salt)
    raise ValueError(f"unknown speaker policy {cfg.policy!r}")
