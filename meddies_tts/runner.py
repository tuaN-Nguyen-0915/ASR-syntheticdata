from __future__ import annotations

import asyncio
from dataclasses import dataclass, field

import numpy as np

from meddies_tts.audio import (
    TARGET_SAMPLE_RATE,
    duration_seconds,
    join_chunks,
    resample,
    to_flac_bytes,
)
from meddies_tts.chunking import chunk_text
from meddies_tts.config import Config
from meddies_tts.engine import TTSEngine
from meddies_tts.qc import DEFAULT_CHARS_PER_SEC, check_audio
from meddies_tts.speakers import derive_seed
from meddies_tts.writer import build_row

_QC_RETRY_TAG = "retry"


@dataclass(frozen=True)
class ShardResult:
    shard_id: str
    n_utterances: int
    n_failed: int
    audio_seconds: float
    failures: list[dict] = field(default_factory=list)


async def _synthesize_chunk(
    engine: TTSEngine,
    semaphore: asyncio.Semaphore,
    text: str,
    ref_latents: bytes,
    seed: int,
    max_retries: int,
) -> np.ndarray:
    """Generate one chunk, retrying transient engine errors under the shared semaphore."""
    last: Exception | None = None
    for attempt in range(max_retries + 1):
        # Every attempt re-acquires the semaphore rather than holding it across retries,
        # so a chunk that's mid-backoff doesn't block other utterances from using that slot.
        async with semaphore:
            try:
                return await engine.synthesize(text, ref_latents, seed + attempt)
            except Exception as error:  # noqa: BLE001 - retried, then surfaced
                last = error
    raise RuntimeError(f"chunk generation failed after {max_retries + 1} attempts: {last}")


async def _synthesize_once(
    row: dict,
    engine: TTSEngine,
    semaphore: asyncio.Semaphore,
    ref_latents: bytes,
    cfg: Config,
    salt_suffix: str,
    max_chunk_retries: int,
) -> tuple[np.ndarray, int, int]:
    """Chunk, synthesize, join, and resample one utterance attempt."""
    chunks = chunk_text(row["text_spoken"], cfg.text.chunk_chars)
    seeds = [
        derive_seed(cfg.speaker.seed_salt, row["audio_path"], f"{salt_suffix}#{index}")
        for index in range(len(chunks))
    ]
    # All chunks of this utterance are submitted together; asyncio.gather plus the shared
    # semaphore (passed down from run_shard) is what lets chunks from OTHER utterances in
    # the shard interleave with these instead of waiting for this utterance to finish first.
    waves = await asyncio.gather(
        *(
            _synthesize_chunk(engine, semaphore, text, ref_latents, seed, max_chunk_retries)
            for text, seed in zip(chunks, seeds)
        )
    )
    joined = join_chunks(list(waves), engine.sample_rate, cfg.text.silence_ms)
    wave = resample(joined, engine.sample_rate, TARGET_SAMPLE_RATE)
    return wave, len(chunks), seeds[0]


async def _synthesize_utterance(
    row: dict,
    engine: TTSEngine,
    semaphore: asyncio.Semaphore,
    refs: dict[int, bytes],
    cfg: Config,
    chars_per_sec: float,
    max_chunk_retries: int,
) -> tuple[dict | None, dict | None]:
    """Synthesize one utterance, QC it, and regenerate once (reseeded) on QC failure."""
    ref_latents = refs[row["speaker_id"]]
    last_reason = ""
    # Utterance-level retry: a QC failure regenerates the WHOLE utterance once, with a
    # different salt suffix so the retry gets a different seed than the first attempt.
    # This is separate from the chunk-level retry in _synthesize_chunk, which handles
    # transient engine exceptions rather than bad-sounding-but-successful output.
    for salt_suffix in ("", _QC_RETRY_TAG):
        try:
            wave, n_chunks, seed = await _synthesize_once(
                row, engine, semaphore, ref_latents, cfg, salt_suffix, max_chunk_retries
            )
        except Exception as error:  # noqa: BLE001 - recorded as a shard failure
            # A chunk that exhausted its retries drops only this utterance; the caller's
            # gather() keeps running the rest of the shard.
            return None, {
                "audio_path": row["audio_path"],
                "reason": "engine_error",
                "detail": str(error),
            }
        verdict = check_audio(
            wave, TARGET_SAMPLE_RATE, len(row["text_spoken"]), chars_per_sec
        )
        if verdict.ok:
            built = build_row(
                row,
                to_flac_bytes(wave, TARGET_SAMPLE_RATE),
                duration_seconds(wave, TARGET_SAMPLE_RATE),
                n_chunks,
                seed,
                engine.version,
            )
            return built, None
        last_reason = f"qc:{verdict.reason}"
    return None, {
        "audio_path": row["audio_path"],
        "reason": last_reason,
        "detail": "failed QC on both the initial attempt and the reseeded retry",
    }


async def run_shard(
    shard_id: str,
    plan_rows: list[dict],
    engine: TTSEngine,
    refs: dict[int, bytes],
    cfg: Config,
    chars_per_sec: float = DEFAULT_CHARS_PER_SEC,
    max_chunk_retries: int = 2,
) -> tuple[list[dict], ShardResult]:
    """Synthesize every utterance in a shard, keeping the engine's batcher fed."""
    for row in plan_rows:
        if row["speaker_id"] not in refs:
            raise KeyError(f"no reference latents for speaker_id {row['speaker_id']}")

    # One semaphore shared across every utterance's chunks in the shard. All coroutines
    # below are built up front and handed to a single gather() -- nothing here awaits one
    # utterance before starting the next. The engine's batcher only sees concurrent work
    # if concurrent work is actually submitted; a per-utterance loop would starve it.
    semaphore = asyncio.Semaphore(cfg.engine.concurrency)
    outcomes = await asyncio.gather(
        *(
            _synthesize_utterance(
                row, engine, semaphore, refs, cfg, chars_per_sec, max_chunk_retries
            )
            for row in plan_rows
        )
    )

    rows = [built for built, _ in outcomes if built is not None]
    failures = [failure for _, failure in outcomes if failure is not None]
    return rows, ShardResult(
        shard_id=shard_id,
        n_utterances=len(plan_rows),
        n_failed=len(failures),
        audio_seconds=float(sum(row["duration_s"] for row in rows)),
        failures=failures,
    )
