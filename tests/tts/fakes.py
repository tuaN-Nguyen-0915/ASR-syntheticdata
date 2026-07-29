from __future__ import annotations

import asyncio
from collections import Counter
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Call:
    text: str
    ref_latents: bytes
    seed: int


class FakeEngine:
    """In-memory stand-in for the real engine. No GPU, no network."""

    def __init__(
        self,
        sample_rate: int = 48000,
        chars_per_sec: float = 14.0,
        fail_texts: tuple[str, ...] = (),
        fail_times: int = 0,
    ) -> None:
        self.sample_rate = sample_rate
        self.version = "fake-1"
        self._chars_per_sec = chars_per_sec
        self._fail_texts = set(fail_texts)
        self._fail_times = fail_times
        self._failures: Counter[str] = Counter()
        self.calls: list[Call] = []
        self.encoded: list[bytes] = []
        self.peak_concurrency = 0
        self._in_flight = 0

    async def encode_reference(self, wav_bytes: bytes) -> bytes:
        """Convert WAV bytes to mock conditioning latents."""
        self.encoded.append(wav_bytes)
        return b"latents:" + wav_bytes[:8]

    async def synthesize(self, text: str, ref_latents: bytes, seed: int) -> np.ndarray:
        """Generate deterministic speech audio from text and random seed."""
        try:
            self._in_flight += 1
            # Track peak concurrency: Task 12 tests that this respects its semaphore and backoff limits.
            self.peak_concurrency = max(self.peak_concurrency, self._in_flight)
            await asyncio.sleep(0)
            self.calls.append(Call(text, ref_latents, seed))
            # Per-text failure counter: simulate transient errors for retry testing.
            if text in self._fail_texts and self._failures[text] < self._fail_times:
                self._failures[text] += 1
                raise RuntimeError(f"fake engine failure #{self._failures[text]} for {text!r}")
            # Duration scales linearly with text length and chars_per_sec.
            seconds = max(len(text), 1) / self._chars_per_sec
            samples = max(int(seconds * self.sample_rate), 1)
            t = np.linspace(0, seconds, samples, endpoint=False)
            # Seed determines waveform: different seeds produce different frequency, phase, and amplitude.
            rng = np.random.default_rng(seed)
            freq = 100.0 + 400.0 * rng.uniform()
            phase = 2.0 * np.pi * rng.uniform()
            amplitude = 0.2 + 0.1 * rng.uniform()
            noise = 0.02 * rng.standard_normal(samples)
            return (amplitude * np.sin(2 * np.pi * freq * t + phase) + noise).astype(np.float32)
        finally:
            self._in_flight -= 1
