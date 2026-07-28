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
    key = "/".join([salt, *(str(part) for part in parts)]).encode("utf-8")
    digest = hashlib.blake2b(key, digest_size=8).digest()
    return int.from_bytes(digest, "big") & _INT64_MASK


@dataclass(frozen=True)
class Speaker:
    speaker_id: int
    wav_path: Path
    emotions: str
    unique_source_s: float
    duration_s: float


def load_pool(metadata_csv: Path, allow: set[int] | None = None) -> list[Speaker]:
    """Load ViSEC speakers; wav paths resolve relative to the CSV's parent's parent."""
    csv_path = Path(metadata_csv)
    root = csv_path.parent.parent
    speakers: list[Speaker] = []
    with csv_path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            speaker_id = int(row["speaker_id"])
            if allow is not None and speaker_id not in allow:
                continue
            speakers.append(
                Speaker(
                    speaker_id=speaker_id,
                    wav_path=root / row["output_path"],
                    emotions=row["emotions"],
                    unique_source_s=float(row["unique_source_duration_seconds"]),
                    duration_s=float(row["duration_seconds"]),
                )
            )
    return sorted(speakers, key=lambda s: s.speaker_id)


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
        seed = derive_seed(self._salt, *self._scope(config, disease_slug, conv_id, turn))
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
    if cfg.policy == "per_conversation":
        return PerConversationAssigner(pool, cfg.seed_salt)
    if cfg.policy == "per_turn":
        return PerTurnAssigner(pool, cfg.seed_salt)
    raise ValueError(f"unknown speaker policy {cfg.policy!r}")
