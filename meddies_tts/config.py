from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

import yaml

_POLICIES = ("per_conversation", "per_turn")


class ConfigError(ValueError):
    """Raised when configuration is missing or internally inconsistent."""


@dataclass(frozen=True)
class HFConfig:
    repo_id: str
    private: bool = False
    revision: str = "main"
    token_secret: str = "huggingface"


@dataclass(frozen=True)
class SpeakerConfig:
    policy: str = "per_conversation"
    pool: str = "all"
    seed_salt: str = "v1"


@dataclass(frozen=True)
class EngineConfig:
    concurrency: int = 48
    max_num_seqs: int = 64
    max_num_batched_tokens: int = 16384
    cfg_value: float = 2.0
    temperature: float = 1.0
    inference_timesteps: int = 10
    # Fraction of GPU memory nano-vllm-voxcpm may claim for KV-cache blocks; more
    # blocks means more concurrent sequences resident before the scheduler queues.
    # vLLM's own default is 0.9; the pilot should sweep this alongside concurrency.
    gpu_memory_utilization: float = 0.94


@dataclass(frozen=True)
class TextConfig:
    # VoxCPM quality degrades noticeably past ~13 s of audio per generation, so the
    # chunk budget is expressed in SECONDS and converted using the calibrated speech
    # rate. The pilot (Task 17) measures chars_per_sec and both values are updated.
    chunk_target_seconds: float = 12.0
    chars_per_sec: float = 14.0
    silence_ms: int = 250
    max_chars: int = 3000
    min_ttr: float = 0.35
    max_ngram_repeat: int = 4

    @property
    def chunk_chars(self) -> int:
        """Character budget per chunk, computed from chunk_target_seconds and chars_per_sec."""
        return max(1, int(self.chunk_target_seconds * self.chars_per_sec))


@dataclass(frozen=True)
class RunConfig:
    gpu: str = "A100-40GB"
    convs_per_shard: int = 122
    budget_usd: float | None = None
    configs: tuple[str, ...] = ("vietnamese",)


@dataclass(frozen=True)
class Config:
    hf: HFConfig
    speaker: SpeakerConfig = SpeakerConfig()
    engine: EngineConfig = EngineConfig()
    text: TextConfig = TextConfig()
    run: RunConfig = RunConfig()


def _section(raw: dict[str, Any], key: str) -> dict[str, Any]:
    value = raw.get(key) or {}
    if not isinstance(value, dict):
        raise ConfigError(f"config section '{key}' must be a mapping, got {type(value).__name__}")
    return value


def _apply_overrides(raw: dict[str, Any], overrides: dict[str, Any]) -> dict[str, Any]:
    for dotted, value in overrides.items():
        if value is None:
            continue
        section, _, field = dotted.partition(".")
        if not field:
            raise ConfigError(f"override '{dotted}' must be of the form 'section.field'")
        raw.setdefault(section, {})[field] = value
    return raw


def load_config(path: Path, overrides: dict[str, Any] | None = None) -> Config:
    """Load and validate configuration from a YAML file with optional dot-key overrides."""
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        raise ConfigError("config file must contain a top-level mapping")
    raw = _apply_overrides(raw, overrides or {})

    hf_raw = _section(raw, "hf")
    repo_id = hf_raw.get("repo_id")
    if not repo_id:
        raise ConfigError(
            "hf.repo_id is required and has no default. Set it in config.yaml "
            "(e.g. 'Meddies/SynthAudio') or pass --hf-repo."
        )

    run_raw = dict(_section(raw, "run"))
    if "configs" in run_raw:
        run_raw["configs"] = tuple(run_raw["configs"])

    cfg = Config(
        hf=HFConfig(**hf_raw),
        speaker=SpeakerConfig(**_section(raw, "speaker")),
        engine=EngineConfig(**_section(raw, "engine")),
        text=TextConfig(**_section(raw, "text")),
        run=RunConfig(**run_raw),
    )
    _validate(cfg)
    return cfg


def _validate(cfg: Config) -> None:
    if cfg.speaker.policy not in _POLICIES:
        raise ConfigError(
            f"speaker.policy must be one of {_POLICIES}, got {cfg.speaker.policy!r}"
        )
    if cfg.engine.concurrency > cfg.engine.max_num_seqs:
        raise ConfigError(
            f"engine.concurrency ({cfg.engine.concurrency}) must be <= "
            f"engine.max_num_seqs ({cfg.engine.max_num_seqs}); extra requests would "
            "only queue inside the engine"
        )
    if cfg.text.chars_per_sec <= 0:
        raise ConfigError(
            f"text.chars_per_sec must be positive, got {cfg.text.chars_per_sec}"
        )
    if cfg.text.chunk_target_seconds <= 0:
        raise ConfigError(
            f"text.chunk_target_seconds must be positive, got {cfg.text.chunk_target_seconds}"
        )
    if cfg.run.convs_per_shard <= 0:
        raise ConfigError(
            f"run.convs_per_shard must be positive, got {cfg.run.convs_per_shard}"
        )
