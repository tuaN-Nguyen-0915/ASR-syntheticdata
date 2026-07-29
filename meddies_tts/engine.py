from __future__ import annotations

from typing import Protocol

import numpy as np


class TTSEngine(Protocol):
    """Minimal surface the pipeline needs from a TTS backend.

    Implemented for real by VoxCPMEngine (GPU only, see meddies_tts/engine.py
    bottom half) and for tests by tests/tts/fakes.FakeEngine.
    """

    sample_rate: int
    version: str

    async def encode_reference(self, wav_bytes: bytes) -> bytes:
        """Encode a reference WAV into conditioning latents."""
        ...

    async def synthesize(self, text: str, ref_latents: bytes, seed: int) -> np.ndarray:
        """Generate one chunk of speech as a float32 mono array."""
        ...
