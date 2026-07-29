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


# The engine's seed parameter is passed through to torch; mask to a safe positive
# 32-bit value. Masking is deterministic, so reproducibility is preserved and the
# `seed` column stored in the dataset maps 1:1 onto the value actually used.
_SEED_MASK = (1 << 31) - 1


class VoxCPMEngine:
    """TTSEngine backed by nano-vllm-voxcpm. GPU only; never imported on the Mac."""

    def __init__(self, server, sample_rate: int, version: str, cfg) -> None:
        self._server = server
        self.sample_rate = sample_rate
        self.version = version
        self._cfg = cfg

    @classmethod
    async def create(cls, model_path: str, cfg, devices: list[int] | None = None):
        """Boot a nano-vllm-voxcpm server and wrap it as a TTSEngine."""
        from nanovllm_voxcpm import VoxCPM  # imported lazily: requires CUDA + flash-attn

        server = VoxCPM.from_pretrained(
            model=model_path,
            inference_timesteps=cfg.inference_timesteps,
            max_num_batched_tokens=cfg.max_num_batched_tokens,
            max_num_seqs=cfg.max_num_seqs,
            gpu_memory_utilization=cfg.gpu_memory_utilization,
            devices=devices or [0],
        )
        await server.wait_for_ready()
        info = await server.get_model_info()
        version = f"nanovllm-voxcpm/{_package_version()}"
        return cls(server, int(info["sample_rate"]), version, cfg)

    async def encode_reference(self, wav_bytes: bytes) -> bytes:
        """Encode a reference WAV into conditioning latents."""
        # encode_latents resamples and mono-mixes internally, so the 16 kHz
        # ViSEC WAVs need no preprocessing.
        return await self._server.encode_latents(wav_bytes, "wav")

    async def synthesize(self, text: str, ref_latents: bytes, seed: int) -> np.ndarray:
        """Generate speech by collecting the engine's async generator chunks."""
        chunks = []
        async for piece in self._server.generate(
            target_text=text,
            ref_audio_latents=ref_latents,
            cfg_value=self._cfg.cfg_value,
            temperature=self._cfg.temperature,
            seed=seed & _SEED_MASK,
        ):
            chunks.append(piece)
        if not chunks:
            raise RuntimeError(f"engine produced no audio for {text[:60]!r}")
        return np.concatenate(chunks, axis=0).astype(np.float32, copy=False)

    async def close(self) -> None:
        """Shut down the underlying server."""
        await self._server.stop()


def _package_version() -> str:
    """Return the installed nano-vllm-voxcpm version, or 'unknown' if unavailable."""
    try:
        import importlib.metadata

        return importlib.metadata.version("nano-vllm-voxcpm")
    except Exception:  # noqa: BLE001
        return "unknown"
