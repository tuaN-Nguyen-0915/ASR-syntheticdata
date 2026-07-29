from __future__ import annotations

import asyncio
from collections import Counter
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Call:
    text: str
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
        self.encoded.append(wav_bytes)
        return b"latents:" + wav_bytes[:8]

    async def synthesize(self, text: str, ref_latents: bytes, seed: int) -> np.ndarray:
        self._in_flight += 1
        self.peak_concurrency = max(self.peak_concurrency, self._in_flight)
        try:
            await asyncio.sleep(0)
            self.calls.append(Call(text, seed))
            if text in self._fail_texts and self._failures[text] < self._fail_times:
                self._failures[text] += 1
                raise RuntimeError(f"fake engine failure #{self._failures[text]} for {text!r}")
            seconds = max(len(text), 1) / self._chars_per_sec
            samples = max(int(seconds * self.sample_rate), 1)
            t = np.linspace(0, seconds, samples, endpoint=False)
            freq = 180.0 + (seed % 200)
            return (0.3 * np.sin(2 * np.pi * freq * t)).astype(np.float32)
        finally:
            self._in_flight -= 1
