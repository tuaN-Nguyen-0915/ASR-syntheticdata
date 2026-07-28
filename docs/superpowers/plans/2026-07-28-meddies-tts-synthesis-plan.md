# Meddies TTS Synthesis Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Synthesize speech for all 711,647 Vietnamese utterances in `output_full/vietnamese/` using VoxCPM2 via nanovllm-voxcpm on Modal GPUs, voice-cloned from ViSEC reference speakers, published to `Meddies/SynthAudio` as ~473 sharded Parquet files.

**Architecture:** Four stages. Stage 0 flattens the 2.47M-file tree into one local `manifest.parquet`. Stage 1 normalizes text, rejects degenerate utterances, assigns speakers and packs conversations into shards — all local CPU. Stage 2 runs one Modal container per shard; each loads the engine once, encodes 147 reference speakers once, then fans ~2,400 chunk requests at an `asyncio.Semaphore` so nano-vllm's continuous batcher stays fed. Stage 3 publishes the dataset card. Every module except `engine.py` and `app.py` is GPU-free and unit-testable on the dev Mac.

**Tech Stack:** Python 3.11, `modal`, `nano-vllm-voxcpm`, `datasets`/`pyarrow`, `num2words`, `soundfile`, `soxr`, `numpy`, `huggingface_hub`, `pytest`, `pytest-asyncio`.

**Spec:** `docs/superpowers/specs/2026-07-28-meddies-tts-synthesis-design.md`

## Global Constraints

- **New package is `meddies_tts/`.** The existing `meddies/` package (text extraction) is untouched by every task in this plan.
- **Only `meddies_tts/engine.py` and `app.py` may import CUDA/GPU/Modal libraries.** Every other module must import and run on the dev Mac (Apple M2, no CUDA). Any task adding a GPU import to another module is wrong.
- **`nano-vllm-voxcpm` cannot be installed or run locally** — it requires Linux + NVIDIA + `flash-attn` and explicitly does not support CPU. All local pipeline tests use `FakeEngine` (Task 11).
- **No compiled normalizer dependency.** `vinorm` was evaluated and rejected: it ships an x86-64 Linux ELF binary that pip-installs on arm64 macOS then fails every call with `Exec format error`, and measurement showed 9 hand-written rules cover 100.00% of numeric occurrences anyway. Normalization is pure Python (Task 3), so **Stage 1 runs locally** and is fully unit-testable on the Mac.
- **Output audio is 16 kHz mono FLAC.** VoxCPM2 emits 48 kHz; `audio.py` resamples down. Never store 48 kHz.
- **`hf.repo_id` is `"Meddies/SynthAudio"`, set in `config.yaml`, with no default anywhere in code.** If the key is missing, fail immediately with a clear message.
- **`engine.concurrency` must be `<= engine.max_num_seqs`.** Config validation enforces this.
- **The ASR ground truth is `text_spoken`, not `text_raw`.** Both columns are always written.
- **Shard ids are namespaced per config** (`vi-00000`, `en-00000`) so planning one language can never renumber the other.
- **Determinism:** speaker choice is seeded from `{salt}/{config}/{disease_slug}/{conv_id}`; generation seed is seeded from `{salt}/{audio_path}#{chunk_idx}`. Both via `blake2b`. Regenerating a shard must reproduce it identically.
- **A conversation is never split across shards.**
- **Reject rule (exact):** reject if `len(text) > text.max_chars` OR (`len(words) > 200` AND `type_token_ratio < text.min_ttr` AND `max_5gram_repeat >= text.max_ngram_repeat`).
- **Tests never call the real HF Hub, the real Modal API, or the real 711k-row dataset.** Use fakes, `tmp_path`, and small fixtures.
- Follow the existing repo style: plain `pytest` functions (no classes), type-hinted module-level functions, private module constants prefixed `_`.

---

### Task 1: Package scaffold and configuration

**Files:**
- Create: `meddies_tts/__init__.py`
- Create: `meddies_tts/config.py`
- Create: `config.yaml`
- Modify: `requirements.txt`
- Test: `tests/tts/test_config.py`
- Create: `tests/tts/__init__.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `Config`, `HFConfig`, `SpeakerConfig`, `EngineConfig`, `TextConfig`, `RunConfig` frozen dataclasses; `load_config(path: Path, overrides: dict | None = None) -> Config`; `ConfigError`. Every later task takes a `Config` or one of its sub-objects.

- [ ] **Step 1: Write the failing test**

```python
# tests/tts/test_config.py
import pytest

from meddies_tts.config import ConfigError, load_config

_MINIMAL = """
hf:
  repo_id: "Meddies/SynthAudio"
"""


def _write(tmp_path, text):
    path = tmp_path / "config.yaml"
    path.write_text(text, encoding="utf-8")
    return path


def test_loads_repo_id_and_applies_defaults(tmp_path):
    cfg = load_config(_write(tmp_path, _MINIMAL))
    assert cfg.hf.repo_id == "Meddies/SynthAudio"
    assert cfg.hf.private is False
    assert cfg.speaker.policy == "per_conversation"
    assert cfg.speaker.seed_salt == "v1"
    assert cfg.engine.concurrency == 48
    assert cfg.text.max_chars == 3000
    assert cfg.run.convs_per_shard == 122
    assert cfg.run.configs == ("vietnamese",)


def test_missing_repo_id_raises(tmp_path):
    with pytest.raises(ConfigError, match="hf.repo_id"):
        load_config(_write(tmp_path, "hf: {}\n"))


def test_null_repo_id_raises(tmp_path):
    with pytest.raises(ConfigError, match="hf.repo_id"):
        load_config(_write(tmp_path, "hf:\n  repo_id: null\n"))


def test_override_replaces_repo_id(tmp_path):
    cfg = load_config(_write(tmp_path, _MINIMAL), {"hf.repo_id": "someone/scratch"})
    assert cfg.hf.repo_id == "someone/scratch"


def test_concurrency_above_max_num_seqs_raises(tmp_path):
    text = _MINIMAL + "engine:\n  concurrency: 128\n  max_num_seqs: 64\n"
    with pytest.raises(ConfigError, match="concurrency"):
        load_config(_write(tmp_path, text))


def test_unknown_speaker_policy_raises(tmp_path):
    text = _MINIMAL + "speaker:\n  policy: per_galaxy\n"
    with pytest.raises(ConfigError, match="policy"):
        load_config(_write(tmp_path, text))


def test_config_is_frozen(tmp_path):
    cfg = load_config(_write(tmp_path, _MINIMAL))
    with pytest.raises(Exception):
        cfg.hf.repo_id = "other/repo"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/tts/test_config.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'meddies_tts'`

- [ ] **Step 3: Write the implementation**

```python
# meddies_tts/__init__.py
```

(empty file)

```python
# tests/tts/__init__.py
```

(empty file)

```python
# meddies_tts/config.py
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


@dataclass(frozen=True)
class TextConfig:
    chunk_chars: int = 400
    silence_ms: int = 250
    max_chars: int = 3000
    min_ttr: float = 0.35
    max_ngram_repeat: int = 4


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
```

```yaml
# config.yaml
hf:
  repo_id: "Meddies/SynthAudio"   # REQUIRED — no implicit default in code
  private: false
  revision: "main"
  token_secret: "huggingface"     # Modal Secret holding HF_TOKEN (write scope)

speaker:
  policy: per_conversation        # or per_turn
  pool: all                       # or a path to a file of allowed speaker_ids
  seed_salt: "v1"                 # bump to reshuffle every voice

engine:
  concurrency: 48                 # MUST be <= max_num_seqs
  max_num_seqs: 64
  max_num_batched_tokens: 16384
  cfg_value: 2.0
  temperature: 1.0
  inference_timesteps: 10

text:
  chunk_chars: 400
  silence_ms: 250
  max_chars: 3000
  min_ttr: 0.35
  max_ngram_repeat: 4

run:
  gpu: "A100-40GB"
  convs_per_shard: 122
  budget_usd: null
  configs: ["vietnamese"]
```

Append to `requirements.txt`:

```
pyyaml>=6.0
pyarrow>=14.0
numpy>=1.24
soundfile>=0.12
soxr>=0.3
num2words>=0.5
huggingface_hub>=0.23
pytest-asyncio>=0.23
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pip install -r requirements.txt && pytest tests/tts/test_config.py -v`
Expected: 7 passed

- [ ] **Step 5: Commit**

```bash
git add meddies_tts/__init__.py meddies_tts/config.py config.yaml requirements.txt tests/tts/__init__.py tests/tts/test_config.py
git commit -m "feat: add meddies_tts package scaffold and configuration"
```

---

### Task 2: Manifest builder — flatten the tree to Parquet

**Files:**
- Create: `meddies_tts/manifest.py`
- Test: `tests/tts/test_manifest.py`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: `MANIFEST_SCHEMA: pa.Schema`; `iter_utterances(output_root: Path, configs: Sequence[str]) -> Iterator[dict]`; `build_manifest(output_root: Path, configs: Sequence[str]) -> pa.Table`; `write_manifest(table: pa.Table, path: Path) -> None`; `read_manifest(path: Path) -> pa.Table`. Task 7 consumes `read_manifest`.

Manifest columns: `config, disease_slug, disease_name, conv_id, turn, role, text_raw`.

- [ ] **Step 1: Write the failing test**

```python
# tests/tts/test_manifest.py
import pyarrow as pa

from meddies_tts.manifest import (
    MANIFEST_SCHEMA,
    build_manifest,
    read_manifest,
    write_manifest,
)


def _tree(root):
    """Build a miniature output_full/ tree: 2 diseases, 2 convs, 2 turns."""
    for disease, name in (("ap_xe_hau_mon", "Áp xe hậu môn"), ("suy_gan", "Suy gan")):
        ddir = root / "vietnamese" / disease
        ddir.mkdir(parents=True)
        (ddir / "_disease_name.txt").write_text(name, encoding="utf-8")
        for conv in ("conv_0001", "conv_0002"):
            for turn in (1, 2):
                tdir = ddir / conv / f"Turn{turn}"
                tdir.mkdir(parents=True)
                (tdir / "user.txt").write_text(f"{disease} u{turn}", encoding="utf-8")
                (tdir / "assistant.txt").write_text(f"{disease} a{turn}", encoding="utf-8")
    return root


def test_builds_one_row_per_utterance(tmp_path):
    table = build_manifest(_tree(tmp_path), ["vietnamese"])
    assert table.num_rows == 2 * 2 * 2 * 2  # disease x conv x turn x role


def test_schema_matches(tmp_path):
    table = build_manifest(_tree(tmp_path), ["vietnamese"])
    assert table.schema.equals(MANIFEST_SCHEMA)


def test_carries_unslugified_disease_name(tmp_path):
    table = build_manifest(_tree(tmp_path), ["vietnamese"])
    names = set(table.column("disease_name").to_pylist())
    assert names == {"Áp xe hậu môn", "Suy gan"}


def test_rows_are_deterministically_ordered(tmp_path):
    first = build_manifest(_tree(tmp_path), ["vietnamese"]).to_pylist()
    second = build_manifest(tmp_path, ["vietnamese"]).to_pylist()
    assert first == second
    keys = [(r["disease_slug"], r["conv_id"], r["turn"], r["role"]) for r in first]
    assert keys == sorted(keys)


def test_turn_parsed_as_int_and_text_preserved(tmp_path):
    rows = build_manifest(_tree(tmp_path), ["vietnamese"]).to_pylist()
    row = next(r for r in rows if r["disease_slug"] == "suy_gan"
               and r["conv_id"] == "conv_0002" and r["turn"] == 2 and r["role"] == "user")
    assert row["text_raw"] == "suy_gan u2"


def test_missing_disease_name_file_falls_back_to_slug(tmp_path):
    _tree(tmp_path)
    (tmp_path / "vietnamese" / "suy_gan" / "_disease_name.txt").unlink()
    rows = build_manifest(tmp_path, ["vietnamese"]).to_pylist()
    assert {r["disease_name"] for r in rows if r["disease_slug"] == "suy_gan"} == {"suy_gan"}


def test_turn_missing_one_role_still_emits_the_other(tmp_path):
    _tree(tmp_path)
    (tmp_path / "vietnamese" / "suy_gan" / "conv_0001" / "Turn2" / "assistant.txt").unlink()
    rows = build_manifest(tmp_path, ["vietnamese"]).to_pylist()
    turn = [r for r in rows if r["disease_slug"] == "suy_gan"
            and r["conv_id"] == "conv_0001" and r["turn"] == 2]
    assert [r["role"] for r in turn] == ["user"]


def test_absent_config_directory_is_skipped(tmp_path):
    table = build_manifest(_tree(tmp_path), ["vietnamese", "english"])
    assert set(table.column("config").to_pylist()) == {"vietnamese"}


def test_write_then_read_round_trips(tmp_path):
    table = build_manifest(_tree(tmp_path), ["vietnamese"])
    path = tmp_path / "manifest.parquet"
    write_manifest(table, path)
    assert read_manifest(path).to_pylist() == table.to_pylist()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/tts/test_manifest.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'meddies_tts.manifest'`

- [ ] **Step 3: Write the implementation**

```python
# meddies_tts/manifest.py
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
    rows = list(iter_utterances(output_root, configs))
    columns = {name: [row[name] for row in rows] for name in MANIFEST_SCHEMA.names}
    return pa.Table.from_pydict(columns, schema=MANIFEST_SCHEMA)


def write_manifest(table: pa.Table, path: Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(table, path, compression="zstd")


def read_manifest(path: Path) -> pa.Table:
    return pq.read_table(path)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/tts/test_manifest.py -v`
Expected: 9 passed

- [ ] **Step 5: Commit**

```bash
git add meddies_tts/manifest.py tests/tts/test_manifest.py
git commit -m "feat: flatten output_full tree into a manifest parquet"
```

---

### Task 3: Vietnamese number verbalization and text normalization

**Files:**
- Create: `meddies_tts/vietnamese_numbers.py`
- Create: `meddies_tts/textprep.py`
- Test: `tests/tts/test_vietnamese_numbers.py`
- Test: `tests/tts/test_textprep.py`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: from `vietnamese_numbers` — `Dialect` frozen dataclass (`zero_filler`, `thousand`, `four`), `NORTHERN`, `SOUTHERN`, `dialect_from_seed(seed: int) -> Dialect`, `number_to_words(n: int, dialect: Dialect = NORTHERN) -> str`, `decimal_to_words(text: str, dialect: Dialect = NORTHERN) -> str`, `digits_to_words(text: str) -> str`. From `textprep` — `strip_reasoning`, `strip_markup`, `Normalizer` Protocol, `VietnameseNormalizer(dialect: Dialect = NORTHERN)`, `EnglishNormalizer`, `get_normalizer(config: str, dialect: Dialect | None = None) -> Normalizer`. Task 7 builds one normalizer per speaker and must assign speakers **before** normalizing.

**Why we write this instead of using `vinorm`:** measured over 58,232 utterances (81,532
numeric occurrences) after markup stripping, **9 rules cover 100.00%** — plain integer
76.2%, range `D-D` 17.5%, number+unit 2.9%, decimal 1.0%, fraction 0.9%, range-fraction
0.5%, comparator 0.5%, percentage 0.3%, value-per-period 0.2%, unmatched **0**. `vinorm`
additionally ships an x86-64 Linux binary that cannot execute on arm64 macOS. Unmatched
text passes through unchanged, so gaps degrade to the no-normalizer baseline.

**This task also fixes an upstream data bug.** `meddies/think_strip.py` handles only the
literal `<think>`/`</think>` pair, so other reasoning tags — `<thinking>`,
`<internal_reasoning>`, `<phase_check>`, `</tool_call>`, and unclosed `<think>` — leak
into `output_full`. Measured: **2.77% of Vietnamese utterances** carry leaked reasoning,
and in **100%** of those a real utterance survives underneath (one sample: 560 chars of
reasoning wrapping a valid 51-char turn). Extrapolated, ~19,700 utterances would otherwise
be synthesized as English/Vietnamese internal monologue with wrong transcripts. So
`strip_reasoning` strips rather than rejects, and never deletes text following an
unmatched open tag.

**REVIEWER GATE — a Vietnamese speaker must approve the table in Step 2 before Step 3.**
These are real regional/stylistic variants, not arbitrary choices, and getting one wrong
silently corrupts the ASR transcript for every affected utterance.

- [ ] **Step 1: Write the failing number tests**

```python
# tests/tts/test_vietnamese_numbers.py
import pytest

from meddies_tts.vietnamese_numbers import (
    NORTHERN,
    SOUTHERN,
    decimal_to_words,
    dialect_from_seed,
    digits_to_words,
    number_to_words,
)


@pytest.mark.parametrize(
    "n,expected",
    [
        (0, "không"), (1, "một"), (4, "bốn"), (5, "năm"), (9, "chín"),
        (10, "mười"), (11, "mười một"), (14, "mười bốn"), (15, "mười lăm"),
        (19, "mười chín"), (20, "hai mươi"), (21, "hai mươi mốt"),
        (24, "hai mươi tư"), (25, "hai mươi lăm"), (31, "ba mươi mốt"),
        (44, "bốn mươi tư"), (45, "bốn mươi lăm"), (55, "năm mươi lăm"),
        (90, "chín mươi"), (99, "chín trăm" if False else "chín mươi chín"),
        (100, "một trăm"), (101, "một trăm linh một"), (105, "một trăm linh năm"),
        (110, "một trăm mười"), (115, "một trăm mười lăm"),
        (140, "một trăm bốn mươi"), (155, "một trăm năm mươi lăm"),
        (500, "năm trăm"), (625, "sáu trăm hai mươi lăm"),
        (999, "chín trăm chín mươi chín"),
        (1000, "một nghìn"), (1005, "một nghìn không trăm linh năm"),
        (1050, "một nghìn không trăm năm mươi"), (1500, "một nghìn năm trăm"),
        (2024, "hai nghìn không trăm hai mươi tư"),
        (10_000, "mười nghìn"), (100_000, "một trăm nghìn"),
        (1_000_000, "một triệu"), (1_500_000, "một triệu năm trăm nghìn"),
        (2_000_000_000, "hai tỷ"),
    ],
)
def test_number_to_words(n, expected):
    assert number_to_words(n) == expected


@pytest.mark.parametrize(
    "text,expected",
    [
        ("38.5", "ba mươi tám phẩy năm"),
        ("37,2", "ba mươi bảy phẩy hai"),
        ("62,5", "sáu mươi hai phẩy năm"),
        ("0.5", "không phẩy năm"),
        ("1.25", "một phẩy hai năm"),
    ],
)
def test_decimal_to_words(text, expected):
    assert decimal_to_words(text) == expected


@pytest.mark.parametrize(
    "text,expected",
    [("115", "một một năm"), ("113", "một một ba"), ("911", "chín một một")],
)
def test_digits_to_words(text, expected):
    assert digits_to_words(text) == expected


def test_negative_numbers():
    assert number_to_words(-5) == "âm năm"


# --- per-speaker dialect -----------------------------------------------------

@pytest.mark.parametrize(
    "n,expected",
    [
        (101, "một trăm lẻ một"),
        (1000, "một ngàn"),
        (1005, "một ngàn không trăm lẻ năm"),
        (1_500_000, "một triệu năm trăm ngàn"),
    ],
)
def test_southern_dialect(n, expected):
    assert number_to_words(n, SOUTHERN) == expected


def test_four_follows_the_dialect():
    from dataclasses import replace

    assert number_to_words(24, replace(NORTHERN, four="tư")) == "hai mươi tư"
    assert number_to_words(24, replace(NORTHERN, four="bốn")) == "hai mươi bốn"


def test_fourteen_is_bon_regardless_of_dialect():
    from dataclasses import replace

    assert number_to_words(14, replace(NORTHERN, four="tư")) == "mười bốn"
    assert number_to_words(14, replace(NORTHERN, four="bốn")) == "mười bốn"


def test_dialect_from_seed_is_deterministic():
    assert dialect_from_seed(12345) == dialect_from_seed(12345)


def test_dialect_from_seed_never_mixes_registers():
    # "linh" must always travel with "nghìn", "lẻ" with "ngàn".
    for seed in range(500):
        d = dialect_from_seed(seed)
        assert (d.zero_filler == "linh") == (d.thousand == "nghìn")


def test_dialect_from_seed_produces_both_registers():
    assert {dialect_from_seed(s).thousand for s in range(200)} == {"nghìn", "ngàn"}


def test_dialect_from_seed_randomizes_four_independently():
    combos = {(dialect_from_seed(s).thousand, dialect_from_seed(s).four)
              for s in range(300)}
    assert len(combos) == 4


def test_decimal_uses_dialect_for_the_whole_part():
    assert decimal_to_words("101.5", SOUTHERN) == "một trăm lẻ một phẩy năm"
```

- [ ] **Step 2: Confirm the approved variant table**

These were reviewed and approved by a Vietnamese speaker on 2026-07-28. Implement exactly
this; do not substitute your own judgement.

| construct | decision |
|---|---|
| 15, 25 | `mười lăm`, `hai mươi lăm` — `lăm` after a tens digit (standard, not a choice) |
| 21, 31 | `hai mươi mốt` — `mốt` after a tens digit (standard, not a choice) |
| 1,005 | keep `không trăm`: `một nghìn không trăm linh năm` |
| 101 / 1,000 | **per-speaker dialect, coupled** — Northern `linh`+`nghìn` or Southern `lẻ`+`ngàn`, never mixed |
| 24, 44 | **per-speaker random**, `tư` or `bốn`, drawn independently of region |
| decimal separator | `phẩy` |
| fraction | digit-by-digit: `1.25` → `một phẩy hai năm` |
| `gọi 115` | digit-by-digit for `113/114/115/911` only; `115 người` stays a quantity |

**Why the dialect is randomized per speaker:** it gives the ASR model both registers
instead of overfitting to one, while keeping each voice internally consistent — a real
speaker does not switch dialect mid-conversation. Verified over the 147 ViSEC speakers:
78 Northern / 69 Southern, zero `linh`+`ngàn` mismatches, fully deterministic from
`speaker_id`.

Reproducibility is unaffected: `text_spoken` is computed in Stage 1 and **stored in the
plan**, so the published transcript always matches the audio, and re-planning with the
same `seed_salt` reproduces identical text.

- [ ] **Step 3: Run the number tests to verify they fail**

Run: `pytest tests/tts/test_vietnamese_numbers.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'meddies_tts.vietnamese_numbers'`

- [ ] **Step 4: Write `vietnamese_numbers.py`**

```python
# meddies_tts/vietnamese_numbers.py
"""Vietnamese number verbalization with per-speaker dialect. Pure Python."""
from __future__ import annotations

import random
from dataclasses import dataclass

_DIGITS = ("không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín")


@dataclass(frozen=True)
class Dialect:
    zero_filler: str   # "linh" (Northern) | "lẻ" (Southern)
    thousand: str      # "nghìn" (Northern) | "ngàn" (Southern)
    four: str          # "tư" | "bốn"


NORTHERN = Dialect("linh", "nghìn", "tư")
SOUTHERN = Dialect("lẻ", "ngàn", "tư")

# Coupled on purpose: no real speaker says "linh" alongside "ngàn".
_REGIONS = (("linh", "nghìn"), ("lẻ", "ngàn"))


def dialect_from_seed(seed: int) -> Dialect:
    """Pick a dialect deterministically. Caller seeds from speaker_id (Task 7)."""
    rng = random.Random(seed)
    zero_filler, thousand = rng.choice(_REGIONS)
    return Dialect(zero_filler, thousand, rng.choice(("tư", "bốn")))


def digits_to_words(text: str) -> str:
    """Read each digit separately: '115' -> 'một một năm'. Used for hotlines."""
    return " ".join(_DIGITS[int(ch)] for ch in text if ch.isdigit())


def _tens(n: int, dialect: Dialect) -> str:
    if n < 10:
        return _DIGITS[n]
    if n < 20:
        unit = n % 10
        if unit == 0:
            return "mười"
        return "mười " + ("lăm" if unit == 5 else _DIGITS[unit])
    ten, unit = divmod(n, 10)
    out = f"{_DIGITS[ten]} mươi"
    if unit == 1:
        return out + " mốt"
    if unit == 4:
        return out + f" {dialect.four}"
    if unit == 5:
        return out + " lăm"
    return out + (f" {_DIGITS[unit]}" if unit else "")


def _hundreds(n: int, dialect: Dialect, force_hundred: bool) -> str:
    hundred, rest = divmod(n, 100)
    if hundred == 0 and not force_hundred:
        return _tens(rest, dialect)
    if rest == 0:
        return f"{_DIGITS[hundred]} trăm"
    tail = (
        f"{dialect.zero_filler} {_DIGITS[rest]}" if rest < 10 else _tens(rest, dialect)
    )
    return f"{_DIGITS[hundred]} trăm {tail}"


def number_to_words(n: int, dialect: Dialect = NORTHERN) -> str:
    if n < 0:
        return "âm " + number_to_words(-n, dialect)
    if n < 100:
        return _tens(n, dialect)
    if n < 1000:
        return _hundreds(n, dialect, force_hundred=True)
    parts: list[str] = []
    for name, size in (("tỷ", 10**9), ("triệu", 10**6), (dialect.thousand, 10**3)):
        if n >= size:
            group, n = divmod(n, size)
            parts.append(f"{_hundreds(group, dialect, force_hundred=bool(parts))} {name}")
    if n:
        parts.append(_hundreds(n, dialect, force_hundred=True))
    return " ".join(parts)


def decimal_to_words(text: str, dialect: Dialect = NORTHERN) -> str:
    """'38.5' / '38,5' -> 'ba mươi tám phẩy năm' (fraction read digit by digit)."""
    whole, _, frac = text.replace(",", ".").partition(".")
    words = number_to_words(int(whole), dialect)
    return f"{words} phẩy {digits_to_words(frac)}" if frac else words
```

- [ ] **Step 5: Run the number tests to verify they pass**

Run: `pytest tests/tts/test_vietnamese_numbers.py -v`
Expected: 61 passed

- [ ] **Step 6: Commit the number module**

```bash
git add meddies_tts/vietnamese_numbers.py tests/tts/test_vietnamese_numbers.py
git commit -m "feat: add Vietnamese number verbalization"
```

- [ ] **Step 7: Write the failing normalizer tests**

```python
# tests/tts/test_textprep.py
import pytest

from meddies_tts.textprep import (
    EnglishNormalizer,
    VietnameseNormalizer,
    get_normalizer,
    strip_markup,
)

_VN = VietnameseNormalizer()


def test_strips_bold_markers_keeping_content():
    assert strip_markup("**Về tình trạng của em**: ổn") == "Về tình trạng của em: ổn"


def test_strips_bullet_hyphens():
    assert strip_markup("- Apxe hậu môn\n- Búi trĩ sa") == "Apxe hậu môn Búi trĩ sa"


def test_strips_numbered_list_markers():
    assert strip_markup("1. Đầu tiên\n2. Sau đó") == "Đầu tiên Sau đó"


def test_collapses_whitespace_and_newlines():
    assert strip_markup("a  b\n\n\tc") == "a b c"


def test_keeps_digits_and_units_for_the_normalizer():
    assert strip_markup("**Sốt cao (>38.5°C)**") == "Sốt cao (>38.5°C)"


def test_empty_input_returns_empty():
    assert strip_markup("") == ""
    assert _VN.normalize("") == ""


def test_comparator_and_decimal_and_degrees():
    assert _VN.normalize("Sốt cao (>38.5°C) thì đi khám.") == (
        "Sốt cao (trên ba mươi tám phẩy năm độ C) thì đi khám."
    )


def test_hotline_is_read_digit_by_digit():
    assert _VN.normalize("hoặc gọi 115 nếu cần") == "hoặc gọi một một năm nếu cần"


def test_range_and_fraction():
    assert _VN.normalize("Mức độ đau 6-7/10, kéo dài 10-15 phút.") == (
        "Mức độ đau sáu đến bảy trên mười, kéo dài mười đến mười lăm phút."
    )


def test_dosage_with_units_and_period():
    assert _VN.normalize("Metformin 1000mg/ngày (2 viên 500mg).") == (
        "Metformin một nghìn mi-li-gam mỗi ngày (hai viên năm trăm mi-li-gam)."
    )


def test_percentage():
    assert _VN.normalize("(20% Drysol)") == "(hai mươi phần trăm Drysol)"


def test_blood_pressure_keeps_its_trailing_unit():
    assert _VN.normalize("Huyết áp là 140/90 mmHg.") == (
        "Huyết áp là một trăm bốn mươi trên chín mươi mi-li-mét thuỷ ngân."
    )


def test_latin_drug_names_pass_through_untouched():
    assert "Amlodipine" in _VN.normalize("dùng Amlodipine 5mg")


def test_text_without_digits_is_only_markup_stripped():
    assert _VN.normalize("**Xin chào bác sĩ.**") == "Xin chào bác sĩ."


def test_no_digits_remain_after_normalization():
    text = "Uống 625mg, 3 lần mỗi ngày trong 7-10 ngày, sốt >38.5°C, 140/90 mmHg, 20%."
    assert not any(ch.isdigit() for ch in _VN.normalize(text))


def test_output_has_no_double_spaces():
    assert "  " not in _VN.normalize("Nhiệt độ 37,2 độ, mạch 80 lần mỗi phút.")


def test_english_normalizer_verbalizes_integers():
    assert EnglishNormalizer().normalize("call 115 now") == "call one hundred and fifteen now"


def test_english_normalizer_strips_markup_first():
    assert EnglishNormalizer().normalize("**take 2 pills**") == "take two pills"


def test_get_normalizer_selects_by_config():
    assert isinstance(get_normalizer("vietnamese"), VietnameseNormalizer)
    assert isinstance(get_normalizer("english"), EnglishNormalizer)


def test_get_normalizer_rejects_unknown_config():
    with pytest.raises(ValueError, match="klingon"):
        get_normalizer("klingon")


# --- leaked reasoning blocks (2.77% of utterances) ---------------------------

def test_strips_a_closed_reasoning_block():
    assert _VN.normalize(
        "<thinking> **Giai đoạn**: Phase 4 - Closing. </thinking> Không có gì thưa Bác."
    ) == "Không có gì thưa Bác."


def test_strips_the_literal_think_block():
    assert _VN.normalize("<think>lý luận</think>Chào bác sĩ.") == "Chào bác sĩ."


def test_strips_malformed_reasoning_tags():
    assert _VN.normalize(
        '<internal_reasoning] ồn ào </internal_reasoning" Xin chào ạ.'
    ) == "Xin chào ạ."


def test_unclosed_open_tag_keeps_the_text():
    # Never delete content we cannot prove is reasoning.
    assert "Chào bác" in _VN.normalize("<think>lý luận chưa đóng Chào bác.")


def test_text_without_tags_is_untouched_by_reasoning_stripping():
    assert _VN.normalize("Câu bình thường.") == "Câu bình thường."


# --- units and identifiers ---------------------------------------------------

def test_expanded_units_are_verbalized():
    assert _VN.normalize("vitamin 400mcg") == "vitamin bốn trăm mi-crô-gam"
    assert _VN.normalize("khám lúc 8h") == "khám lúc tám giờ"
    assert _VN.normalize("cao 170cm") == "cao một trăm bảy mươi xen-ti-mét"


def test_word_per_period_slash():
    assert _VN.normalize("30 phút/ngày, 2 lần/tuần") == (
        "ba mươi phút mỗi ngày, hai lần mỗi tuần"
    )


def test_non_period_slash_becomes_a_space_not_moi():
    # 'anh/chị' occurs 9,760 times; 'anh mỗi chị' would be nonsense.
    assert _VN.normalize("Anh/chị ở quận/huyện nào?") == "Anh chị ở quận huyện nào?"


@pytest.mark.parametrize("ident", ["B12", "T4", "HbA1c", "N95", "SpO2", "COVID-19"])
def test_alphanumeric_identifiers_are_never_verbalized(ident):
    assert ident in _VN.normalize(f"xét nghiệm {ident} bình thường")


def test_identifier_protection_does_not_block_neighbouring_numbers():
    assert _VN.normalize("SpO2 95%") == "SpO2 chín mươi lăm phần trăm"
```

- [ ] **Step 8: Run the normalizer tests to verify they fail**

Run: `pytest tests/tts/test_textprep.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'meddies_tts.textprep'`

- [ ] **Step 9: Write `textprep.py`**

```python
# meddies_tts/textprep.py
from __future__ import annotations

import re
from typing import Protocol

from num2words import num2words

from meddies_tts.vietnamese_numbers import (
    NORTHERN,
    Dialect,
    decimal_to_words,
    digits_to_words,
    number_to_words,
)

_WHITESPACE = re.compile(r"\s+")

# --- leaked reasoning blocks -------------------------------------------------
# Upstream bug: meddies/think_strip.py only knows the literal <think>/</think>
# pair, so other reasoning tags (and unclosed <think>) survive into output_full.
# Measured: 2.77% of Vietnamese utterances carry one, and in 100% of those a real
# utterance is underneath -- so strip, never reject.
_RNAME = r"think|thinking|internal[_ ]?reasoning|phase[_ ]?check|reasoning|tool_call"
_RTAG = rf"<\s*/?\s*(?:{_RNAME})\s*[>\"\]]?"
_REASON_BLOCK = re.compile(rf"{_RTAG}.*?<\s*/\s*(?:{_RNAME})\s*[>\"\]]?", re.DOTALL | re.I)
_REASON_TAG = re.compile(_RTAG, re.I)
_TAG_FRAGMENT = re.compile(r"^[A-Za-z_]{0,12}[>\"\]]\s*")

# --- markdown ---------------------------------------------------------------
_BOLD = re.compile(r"\*{1,3}")
_BULLET = re.compile(r"(?:(?<=\n)|^)\s*[-*•]\s+", re.MULTILINE)
_ORDERED = re.compile(r"(?:(?<=\n)|^)\s*\d+[.)]\s+", re.MULTILINE)
_HEADING = re.compile(r"(?:(?<=\n)|^)\s*#{1,6}\s*", re.MULTILINE)
_NUMBER = re.compile(r"\d+(?:\.\d+)?")

# --- numeric vocabulary (unit list measured from the corpus) ----------------
_HOTLINES = {"113", "114", "115", "911"}
_UNITS = {
    "mg": "mi-li-gam", "mcg": "mi-crô-gam", "µg": "mi-crô-gam", "g": "gam",
    "kg": "ki-lô-gam", "ml": "mi-li-lít", "l": "lít", "lít": "lít", "cc": "xê-xê",
    "cm": "xen-ti-mét", "mm": "mi-li-mét", "m": "mét", "km": "ki-lô-mét",
    "mmhg": "mi-li-mét thuỷ ngân", "iu": "đơn vị quốc tế", "kcal": "ki-lô-ca-lo",
    "°c": "độ C", "%": "phần trăm", "h": "giờ",
    "viên": "viên", "lần": "lần", "gói": "gói", "ống": "ống", "giọt": "giọt",
    "ly": "ly", "bữa": "bữa",
}
_UNIT_ALT = (
    "°C|%|mmHg|kcal|mcg|µg|mg|ml|kg|km|cm|mm|IU|cc|lít|viên|gói|ống|giọt|ly|bữa|lần"
    "|[gmlh]"
)
_PERIODS = {
    "ngày": "mỗi ngày", "tuần": "mỗi tuần", "tháng": "mỗi tháng", "giờ": "mỗi giờ",
    "phút": "mỗi phút", "lần": "mỗi lần", "buổi": "mỗi buổi", "năm": "mỗi năm",
}
_MEASURES = "lần|lít|phút|tiếng|giờ|ngày|tháng|tuần|nước|viên|gói|ống|ly|bữa|ml|mg|g|kg"
# Letters glued (optionally via hyphen) to digits are identifiers -- B12, T4,
# HbA1c, N95, SpO2, COVID-19 -- and must never be verbalized.
_IDENT = re.compile(r"\b[A-Za-zÀ-ỹ]+-?\d+[A-Za-z0-9]*\b")


def strip_reasoning(text: str) -> str:
    """Remove leaked reasoning blocks. Never deletes text after an unmatched open tag."""
    out = _REASON_BLOCK.sub(" ", text)
    out = _REASON_TAG.sub(" ", out)
    out = _TAG_FRAGMENT.sub("", out.lstrip())
    return _WHITESPACE.sub(" ", out).strip()


def strip_markup(text: str) -> str:
    """Remove reasoning leakage and markdown, then collapse whitespace."""
    without = strip_reasoning(text)
    without = _HEADING.sub("", without)
    without = _ORDERED.sub("", without)
    without = _BULLET.sub("", without)
    without = _BOLD.sub("", without)
    return _WHITESPACE.sub(" ", without).strip()


class Normalizer(Protocol):
    def normalize(self, text: str) -> str: ...


def _unit(token: str) -> str:
    return _UNITS.get(token.lower().strip(), token)


def _int_or_decimal(token: str, dialect: Dialect) -> str:
    return (decimal_to_words(token, dialect) if re.search(r"[.,]", token)
            else number_to_words(int(token), dialect))


def _slot(index: int) -> str:
    """Digit-free sentinel -- a numeric placeholder would itself get verbalized."""
    letters = ""
    index += 1
    while index:
        index, rem = divmod(index - 1, 26)
        letters = chr(ord("A") + rem) + letters
    return f"\x00{letters}\x00"


def _normalize_numbers(text: str, dialect: Dialect = NORTHERN) -> str:
    """The measured rules, applied most-specific first."""
    saved: list[str] = []

    def stash(match: re.Match) -> str:
        saved.append(match.group(0))
        return _slot(len(saved) - 1)

    out = _IDENT.sub(stash, text)                       # protect B12, COVID-19, HbA1c
    out = re.sub(r">\s*(?=\d)", "trên ", out)
    out = re.sub(r"<\s*(?=\d)", "dưới ", out)
    out = re.sub(
        r"(\d+)\s*-\s*(\d+)\s*/\s*(\d+)",
        lambda m: f"{number_to_words(int(m[1]), dialect)} đến {number_to_words(int(m[2]), dialect)} "
                  f"trên {number_to_words(int(m[3]), dialect)}", out)
    out = re.sub(
        rf"(\d+(?:[.,]\d+)?)\s*({_UNIT_ALT})\s*/\s*({'|'.join(_PERIODS)})",
        lambda m: f"{_int_or_decimal(m[1], dialect)} {_unit(m[2])} {_PERIODS[m[3]]}", out)
    out = re.sub(
        rf"(\d+)\s*/\s*(\d+)\s*({_UNIT_ALT})?",
        lambda m: f"{number_to_words(int(m[1]), dialect)} trên {number_to_words(int(m[2]), dialect)}"
                  + (f" {_unit(m[3])}" if m[3] else ""), out)
    out = re.sub(
        r"(?<![\d/])(\d+)\s*-\s*(\d+)(?![\d/])",
        lambda m: f"{number_to_words(int(m[1]), dialect)} đến {number_to_words(int(m[2]), dialect)}", out)
    out = re.sub(
        rf"(\d+[.,]\d+)\s*({_UNIT_ALT})?",
        lambda m: decimal_to_words(m[1], dialect) + (f" {_unit(m[2])}" if m[2] else ""), out)
    out = re.sub(
        rf"(\d+)\s*({_UNIT_ALT})(?![A-Za-zÀ-ỹ])",
        lambda m: f"{number_to_words(int(m[1]), dialect)} {_unit(m[2])}", out)
    out = re.sub(
        r"\b\d+\b",
        lambda m: digits_to_words(m[0]) if m[0] in _HOTLINES else number_to_words(int(m[0]), dialect),
        out)
    # "phút/ngày" -> "phút mỗi ngày". The right side MUST be a period word, or
    # "anh/chị" (9,760 occurrences) would become "anh mỗi chị".
    out = re.sub(
        rf"\b({_MEASURES})\s*/\s*({'|'.join(_PERIODS)})\b",
        lambda m: f"{m[1]} {_PERIODS[m[2]]}", out)
    # any other word/word slash reads naturally as a space: "anh/chị" -> "anh chị"
    out = re.sub(r"(?<=[A-Za-zÀ-ỹ])\s*/\s*(?=[A-Za-zÀ-ỹ])", " ", out)

    for index, original in enumerate(saved):
        out = out.replace(_slot(index), original)
    return _WHITESPACE.sub(" ", out).strip()


class VietnameseNormalizer:
    """Strip reasoning leakage and markup, then verbalize numbers and units.

    The dialect comes from the speaker (Task 7), so one instance is built per
    speaker_id rather than one per config.
    """

    def __init__(self, dialect: Dialect = NORTHERN) -> None:
        self._dialect = dialect

    def normalize(self, text: str) -> str:
        stripped = strip_markup(text)
        return _normalize_numbers(stripped, self._dialect) if stripped else ""


class EnglishNormalizer:
    """Strip markup, then verbalize numbers with num2words."""

    def normalize(self, text: str) -> str:
        stripped = strip_markup(text)
        if not stripped:
            return ""
        spoken = _NUMBER.sub(lambda m: _say_english(m.group(0)), stripped)
        return _WHITESPACE.sub(" ", spoken).strip()


def _say_english(token: str) -> str:
    if "." in token:
        whole, _, frac = token.partition(".")
        return f"{num2words(int(whole))} point {' '.join(num2words(int(d)) for d in frac)}"
    return num2words(int(token))


def get_normalizer(config: str, dialect: Dialect | None = None) -> Normalizer:
    if config == "vietnamese":
        return VietnameseNormalizer(dialect or NORTHERN)
    if config == "english":
        return EnglishNormalizer()
    raise ValueError(f"no normalizer for config {config!r}")
```

- [ ] **Step 10: Run the normalizer tests to verify they pass**

Run: `pytest tests/tts/test_textprep.py -v`
Expected: 34 passed

- [ ] **Step 11: Verify coverage against the real corpus**

The rules were derived from measurement; confirm no digits survive on real data:

```bash
python3 - <<'EOF'
import os, random
from meddies_tts.textprep import VietnameseNormalizer
random.seed(5)
vn, root = VietnameseNormalizer(), "output_full/vietnamese"
dis = sorted(os.listdir(root)); random.shuffle(dis)
checked = leftover = 0
for d in dis[:40]:
    for conv in sorted(os.listdir(f"{root}/{d}"))[:10]:
        cp = f"{root}/{d}/{conv}"
        if not os.path.isdir(cp): continue
        for turn in os.listdir(cp):
            tp = f"{cp}/{turn}"
            if not os.path.isdir(tp): continue
            for role in ("user", "assistant"):
                f = f"{tp}/{role}.txt"
                if not os.path.exists(f): continue
                out = vn.normalize(open(f, encoding="utf-8").read())
                checked += 1
                if any(c.isdigit() for c in out):
                    leftover += 1
                    if leftover <= 5: print("LEFTOVER:", out[:160])
print(f"checked {checked:,} utterances, {leftover} with digits remaining")
EOF
```

Expected, measured on 10,771 real utterances with this exact rule set:

- **reasoning tags surviving: ~3** (down from 300 before `strip_reasoning`)
- **tokens containing `/`: ~54** (down from 347), mostly bare separators
- **tokens containing a digit: ~84** — all protected identifiers (`B12`, `HbA1c`,
  `T4`, `N95`, `omega-3`, `COVID-19`). These are correct and must NOT be verbalized.

Adapt the snippet above to print leftovers rather than assert zero. Any leftover that is
*not* an identifier names a missing rule — add the rule plus a test before continuing.

- [ ] **Step 12: Commit the normalizer**

```bash
git add meddies_tts/textprep.py tests/tts/test_textprep.py
git commit -m "feat: add markup stripping and per-language text normalizers"
```

---

### Task 4: Rejection rules for degenerate text

**Files:**
- Create: `meddies_tts/reject.py`
- Create: `tests/tts/fixtures/degenerate_vi.txt`
- Test: `tests/tts/test_reject.py`

**Interfaces:**
- Consumes: `TextConfig` from Task 1.
- Produces: `type_token_ratio(text: str) -> float`; `max_ngram_repeat(text: str, n: int = 5) -> int`; `Rejection` frozen dataclass with `.reason: str` and `.detail: str`; `check(text: str, cfg: TextConfig) -> Rejection | None` (returns `None` when the text is acceptable). Task 7 calls `check`.

- [ ] **Step 1: Create the fixture**

Generate a real degenerate sample matching the pattern found in the source data:

```bash
mkdir -p tests/tts/fixtures
python3 - <<'PY'
from pathlib import Path
head = ("Mức độ đau của tôi khoảng 4-5/10 thôi bác ạ, không đến nỗi dữ dội. "
        "Tôi không bị sốt, không ho, không đau răng và thị lực vẫn bình thường. ")
loop = "Tôi cũng không có triệu chứng gì về sức khỏe không có triệu chứng gì "
Path("tests/tts/fixtures/degenerate_vi.txt").write_text(
    head + loop * 400, encoding="utf-8")
PY
wc -c tests/tts/fixtures/degenerate_vi.txt
```

Expected: roughly 27,000 bytes.

- [ ] **Step 2: Write the failing test**

```python
# tests/tts/test_reject.py
from pathlib import Path

from meddies_tts.config import TextConfig
from meddies_tts.reject import Rejection, check, max_ngram_repeat, type_token_ratio

_CFG = TextConfig()
_FIXTURE = Path(__file__).parent / "fixtures" / "degenerate_vi.txt"


def test_type_token_ratio_all_unique_is_one():
    assert type_token_ratio("a b c d") == 1.0


def test_type_token_ratio_all_identical_is_low():
    assert type_token_ratio("a a a a") == 0.25


def test_type_token_ratio_of_empty_text_is_one():
    assert type_token_ratio("") == 1.0


def test_max_ngram_repeat_counts_repeated_five_grams():
    assert max_ngram_repeat("a b c d e a b c d e a b c d e") == 3


def test_max_ngram_repeat_is_one_when_nothing_repeats():
    assert max_ngram_repeat("a b c d e f g h i j") == 1


def test_max_ngram_repeat_short_text_is_one():
    assert max_ngram_repeat("a b c") == 1


def test_accepts_normal_utterance():
    text = ("Chào bác Meddies ạ. Dạo gần đây tôi có một cái mụn nhọt ở ngay vùng "
            "hậu môn, nó sưng to và rất đau ạ.")
    assert check(text, _CFG) is None


def test_rejects_text_over_max_chars():
    result = check("x" * 3001, _CFG)
    assert isinstance(result, Rejection)
    assert result.reason == "too_long"


def test_length_rule_fires_at_the_boundary():
    assert check("x" * 3000, _CFG) is None
    assert check("x" * 3001, _CFG).reason == "too_long"


def test_rejects_real_degenerate_fixture():
    result = check(_FIXTURE.read_text(encoding="utf-8"), _CFG)
    assert result is not None
    assert result.reason in {"too_long", "degenerate"}


def test_degeneration_rule_fires_independently_of_length():
    # Under 3000 chars, but heavily looping: caught by the degeneracy branch.
    text = ("Tôi cũng không có triệu chứng gì về sức khỏe " * 60)
    cfg = TextConfig(max_chars=100_000)
    result = check(text, cfg)
    assert result is not None
    assert result.reason == "degenerate"


def test_short_repetitive_text_is_not_rejected():
    # Fewer than 200 words, so the degeneracy branch does not apply.
    assert check("a a a a a", _CFG) is None


def test_rejection_detail_is_populated():
    assert check("x" * 4000, _CFG).detail
```

- [ ] **Step 3: Run test to verify it fails**

Run: `pytest tests/tts/test_reject.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'meddies_tts.reject'`

- [ ] **Step 4: Write the implementation**

```python
# meddies_tts/reject.py
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from meddies_tts.config import TextConfig

_MIN_WORDS_FOR_DEGENERACY = 200


@dataclass(frozen=True)
class Rejection:
    reason: str
    detail: str


def type_token_ratio(text: str) -> float:
    words = text.split()
    if not words:
        return 1.0
    return len(set(words)) / len(words)


def max_ngram_repeat(text: str, n: int = 5) -> int:
    words = text.split()
    if len(words) < n * 2:
        return 1
    grams = Counter(tuple(words[i : i + n]) for i in range(len(words) - n + 1))
    return grams.most_common(1)[0][1]


def check(text: str, cfg: TextConfig) -> Rejection | None:
    """Return a Rejection if the utterance must not be synthesized, else None."""
    if len(text) > cfg.max_chars:
        return Rejection("too_long", f"{len(text)} chars > max_chars={cfg.max_chars}")

    words = text.split()
    if len(words) <= _MIN_WORDS_FOR_DEGENERACY:
        return None

    ttr = type_token_ratio(text)
    if ttr >= cfg.min_ttr:
        return None

    repeat = max_ngram_repeat(text)
    if repeat < cfg.max_ngram_repeat:
        return None

    return Rejection(
        "degenerate",
        f"words={len(words)} ttr={ttr:.3f}<{cfg.min_ttr} max_5gram_repeat={repeat}",
    )
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/tts/test_reject.py -v`
Expected: 13 passed

- [ ] **Step 6: Commit**

```bash
git add meddies_tts/reject.py tests/tts/test_reject.py tests/tts/fixtures/degenerate_vi.txt
git commit -m "feat: add degenerate-text rejection rules"
```

---

### Task 5: Sentence chunking

**Files:**
- Create: `meddies_tts/chunking.py`
- Test: `tests/tts/test_chunking.py`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: `split_sentences(text: str) -> list[str]`; `chunk_text(text: str, max_chars: int) -> list[str]`. Task 12 calls `chunk_text(text_spoken, cfg.text.chunk_chars)`.

Contract: every chunk is non-empty, no chunk exceeds `max_chars` unless a single whitespace-free token is itself longer, and concatenating chunks with single spaces reproduces the input's tokens in order.

- [ ] **Step 1: Write the failing test**

```python
# tests/tts/test_chunking.py
from meddies_tts.chunking import chunk_text, split_sentences


def test_splits_on_sentence_terminators():
    assert split_sentences("Một. Hai! Ba?") == ["Một.", "Hai!", "Ba?"]


def test_keeps_terminator_attached():
    assert split_sentences("Xin chào bác.")[0].endswith(".")


def test_no_terminator_yields_single_sentence():
    assert split_sentences("không có dấu chấm") == ["không có dấu chấm"]


def test_empty_text_yields_no_sentences():
    assert split_sentences("") == []


def test_short_text_is_one_chunk():
    assert chunk_text("Xin chào bác.", 400) == ["Xin chào bác."]


def test_empty_text_yields_no_chunks():
    assert chunk_text("", 400) == []


def test_whitespace_only_yields_no_chunks():
    assert chunk_text("   \n  ", 400) == []


def test_packs_multiple_sentences_up_to_the_limit():
    text = " ".join(["Câu số một."] * 10)  # 12 chars each incl. space
    chunks = chunk_text(text, 40)
    assert all(len(c) <= 40 for c in chunks)
    assert len(chunks) > 1


def test_no_chunk_exceeds_max_chars():
    text = " ".join(f"Đây là câu số {i}." for i in range(200))
    assert all(len(c) <= 400 for c in chunk_text(text, 400))


def test_single_oversized_sentence_is_hard_split():
    text = "từ " * 500  # one sentence, 1500 chars, no terminator
    chunks = chunk_text(text, 100)
    assert len(chunks) > 1
    assert all(len(c) <= 100 for c in chunks)


def test_single_token_longer_than_limit_is_kept_whole():
    chunks = chunk_text("x" * 250, 100)
    assert chunks == ["x" * 250]


def test_chunks_preserve_all_tokens_in_order():
    text = " ".join(f"từ{i}." for i in range(300))
    assert " ".join(chunk_text(text, 120)).split() == text.split()


def test_no_chunk_is_empty_or_whitespace():
    text = "Một.  Hai.   Ba.    Bốn."
    assert all(c.strip() for c in chunk_text(text, 10))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/tts/test_chunking.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'meddies_tts.chunking'`

- [ ] **Step 3: Write the implementation**

```python
# meddies_tts/chunking.py
from __future__ import annotations

import re

_SENTENCE = re.compile(r"[^.!?…]+[.!?…]+|[^.!?…]+")


def split_sentences(text: str) -> list[str]:
    """Split on sentence terminators, keeping the terminator attached."""
    return [match.strip() for match in _SENTENCE.findall(text) if match.strip()]


def _hard_split(sentence: str, max_chars: int) -> list[str]:
    """Split an oversized sentence on whitespace, never mid-token."""
    chunks: list[str] = []
    current: list[str] = []
    length = 0
    for token in sentence.split():
        addition = len(token) + (1 if current else 0)
        if current and length + addition > max_chars:
            chunks.append(" ".join(current))
            current, length = [token], len(token)
        else:
            current.append(token)
            length += addition
    if current:
        chunks.append(" ".join(current))
    return chunks


def chunk_text(text: str, max_chars: int) -> list[str]:
    """Pack sentences greedily into chunks of at most max_chars characters."""
    chunks: list[str] = []
    current: list[str] = []
    length = 0
    for sentence in split_sentences(text):
        if len(sentence) > max_chars:
            if current:
                chunks.append(" ".join(current))
                current, length = [], 0
            chunks.extend(_hard_split(sentence, max_chars))
            continue
        addition = len(sentence) + (1 if current else 0)
        if current and length + addition > max_chars:
            chunks.append(" ".join(current))
            current, length = [sentence], len(sentence)
        else:
            current.append(sentence)
            length += addition
    if current:
        chunks.append(" ".join(current))
    return chunks
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/tts/test_chunking.py -v`
Expected: 13 passed

- [ ] **Step 5: Commit**

```bash
git add meddies_tts/chunking.py tests/tts/test_chunking.py
git commit -m "feat: add sentence splitting and chunk packing"
```

---

### Task 6: Speaker pool and assignment policies

**Files:**
- Create: `meddies_tts/speakers.py`
- Test: `tests/tts/test_speakers.py`

**Interfaces:**
- Consumes: `SpeakerConfig` from Task 1.
- Produces: `derive_seed(salt: str, *parts: object) -> int`; `Speaker` frozen dataclass (`speaker_id: int`, `wav_path: Path`, `emotions: str`, `unique_source_s: float`, `duration_s: float`); `load_pool(metadata_csv: Path, allow: set[int] | None = None) -> list[Speaker]`; `SpeakerAssigner` Protocol with `assign(config, disease_slug, conv_id, turn, role) -> int`; `PerConversationAssigner`; `PerTurnAssigner`; `get_assigner(cfg: SpeakerConfig, pool: list[Speaker]) -> SpeakerAssigner`. Tasks 7 and 12 use `derive_seed`; Task 7 uses `get_assigner`.

`derive_seed` is defined here (not in a util module) because speaker assignment is its first consumer; Task 12 imports it from here for generation seeds.

- [ ] **Step 1: Write the failing test**

```python
# tests/tts/test_speakers.py
import pytest

from meddies_tts.config import SpeakerConfig
from meddies_tts.speakers import (
    PerConversationAssigner,
    PerTurnAssigner,
    derive_seed,
    get_assigner,
    load_pool,
)

_CSV = """speaker_id,output_path,duration_seconds,clip_count,emotions,unique_source_duration_seconds
0,processed_audio_by_id/speaker_000.wav,12.968,8,angry|happy|neutral|sad,3951.683
1,processed_audio_by_id/speaker_001.wav,12.8,9,angry|neutral,67.904
79,processed_audio_by_id/speaker_079.wav,12.1,10,angry,1.3
136,processed_audio_by_id/speaker_136.wav,11.9,6,neutral,2.0
"""


def _pool_csv(tmp_path):
    root = tmp_path / "ViSEC-processed"
    (root / "processed_audio_by_id").mkdir(parents=True)
    csv = root / "processed_audio_by_id" / "metadata.csv"
    csv.write_text(_CSV, encoding="utf-8")
    for sid in (0, 1, 79, 136):
        (root / "processed_audio_by_id" / f"speaker_{sid:03d}.wav").write_bytes(b"RIFF")
    return csv


def test_derive_seed_is_stable_across_calls():
    assert derive_seed("v1", "vietnamese", "conv_0001") == derive_seed(
        "v1", "vietnamese", "conv_0001"
    )


def test_derive_seed_differs_by_salt():
    assert derive_seed("v1", "a") != derive_seed("v2", "a")


def test_derive_seed_differs_by_parts():
    assert derive_seed("v1", "a") != derive_seed("v1", "b")


def test_derive_seed_fits_in_int64():
    assert 0 <= derive_seed("v1", "x") <= 2**63 - 1


def test_load_pool_reads_every_speaker(tmp_path):
    assert len(load_pool(_pool_csv(tmp_path))) == 4


def test_load_pool_parses_fields(tmp_path):
    speaker = next(s for s in load_pool(_pool_csv(tmp_path)) if s.speaker_id == 79)
    assert speaker.emotions == "angry"
    assert speaker.unique_source_s == pytest.approx(1.3)
    assert speaker.duration_s == pytest.approx(12.1)
    assert speaker.wav_path.name == "speaker_079.wav"
    assert speaker.wav_path.exists()


def test_load_pool_applies_allow_filter(tmp_path):
    pool = load_pool(_pool_csv(tmp_path), allow={0, 1})
    assert [s.speaker_id for s in pool] == [0, 1]


def test_per_conversation_gives_same_speaker_for_every_turn(tmp_path):
    pool = load_pool(_pool_csv(tmp_path))
    assigner = PerConversationAssigner(pool, "v1")
    ids = [assigner.assign("vietnamese", "suy_gan", "conv_0001", t, "user") for t in range(1, 9)]
    assert len(set(ids)) == 1


def test_per_conversation_user_and_assistant_differ(tmp_path):
    pool = load_pool(_pool_csv(tmp_path))
    assigner = PerConversationAssigner(pool, "v1")
    user = assigner.assign("vietnamese", "suy_gan", "conv_0001", 1, "user")
    assistant = assigner.assign("vietnamese", "suy_gan", "conv_0001", 1, "assistant")
    assert user != assistant


def test_per_conversation_is_reproducible(tmp_path):
    pool = load_pool(_pool_csv(tmp_path))
    a = PerConversationAssigner(pool, "v1").assign("vietnamese", "suy_gan", "conv_0007", 3, "user")
    b = PerConversationAssigner(pool, "v1").assign("vietnamese", "suy_gan", "conv_0007", 3, "user")
    assert a == b


def test_changing_salt_reshuffles(tmp_path):
    pool = load_pool(_pool_csv(tmp_path))
    a = [PerConversationAssigner(pool, "v1").assign("vietnamese", "d", f"conv_{i:04d}", 1, "user")
         for i in range(40)]
    b = [PerConversationAssigner(pool, "v2").assign("vietnamese", "d", f"conv_{i:04d}", 1, "user")
         for i in range(40)]
    assert a != b


def test_different_conversations_get_different_pairs(tmp_path):
    pool = load_pool(_pool_csv(tmp_path))
    assigner = PerConversationAssigner(pool, "v1")
    ids = {assigner.assign("vietnamese", "d", f"conv_{i:04d}", 1, "user") for i in range(40)}
    assert len(ids) > 1


def test_per_turn_varies_across_turns(tmp_path):
    pool = load_pool(_pool_csv(tmp_path))
    assigner = PerTurnAssigner(pool, "v1")
    ids = {assigner.assign("vietnamese", "d", "conv_0001", t, "user") for t in range(1, 30)}
    assert len(ids) > 1


def test_per_turn_still_differs_by_role(tmp_path):
    pool = load_pool(_pool_csv(tmp_path))
    assigner = PerTurnAssigner(pool, "v1")
    user = assigner.assign("vietnamese", "d", "conv_0001", 4, "user")
    assistant = assigner.assign("vietnamese", "d", "conv_0001", 4, "assistant")
    assert user != assistant


def test_get_assigner_selects_policy(tmp_path):
    pool = load_pool(_pool_csv(tmp_path))
    assert isinstance(get_assigner(SpeakerConfig(), pool), PerConversationAssigner)
    assert isinstance(
        get_assigner(SpeakerConfig(policy="per_turn"), pool), PerTurnAssigner
    )


def test_pool_smaller_than_two_raises(tmp_path):
    pool = load_pool(_pool_csv(tmp_path), allow={0})
    with pytest.raises(ValueError, match="at least 2"):
        PerConversationAssigner(pool, "v1")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/tts/test_speakers.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'meddies_tts.speakers'`

- [ ] **Step 3: Write the implementation**

```python
# meddies_tts/speakers.py
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/tts/test_speakers.py -v`
Expected: 17 passed

- [ ] **Step 5: Commit**

```bash
git add meddies_tts/speakers.py tests/tts/test_speakers.py
git commit -m "feat: add ViSEC speaker pool loading and assignment policies"
```

---

### Task 7: Shard planning and plan hash

**Files:**
- Create: `meddies_tts/plan.py`
- Test: `tests/tts/test_plan.py`

**Interfaces:**
- Consumes: `Config`/`TextConfig` (Task 1), `read_manifest`/`MANIFEST_SCHEMA` (Task 2), `get_normalizer` (Task 3), `check`/`Rejection` (Task 4), `Speaker`/`get_assigner` (Task 6).
- Produces: `PLAN_SCHEMA: pa.Schema`; `CONFIG_PREFIX: dict[str, str]`; `shard_id(config: str, index: int) -> str`; `shard_repo_path(config: str, index: int, total: int) -> str`; `audio_path(config, disease_slug, conv_id, turn, role) -> str`; `build_plan(manifest: pa.Table, cfg: Config, pool: list[Speaker], normalizers: dict[tuple[str, int], object] | None = None) -> tuple[pa.Table, list[dict]]` (normalizers keyed by `(config, speaker_id)`; speakers are assigned **before** normalization because the dialect follows the speaker); `compute_plan_hash(plan: pa.Table, cfg: Config) -> str`; `shard_totals(plan: pa.Table) -> dict[str, int]`; `write_plan`/`read_plan`. Tasks 12, 13 and 14 consume these.

Plan columns: `config, disease_slug, disease_name, conv_id, turn, role, text_raw, text_spoken, speaker_id, speaker_emotions, speaker_unique_source_s, shard_id, audio_path`.

- [ ] **Step 1: Write the failing test**

```python
# tests/tts/test_plan.py
import pyarrow as pa
import pytest

from meddies_tts.config import Config, HFConfig, RunConfig, TextConfig
from meddies_tts.manifest import MANIFEST_SCHEMA
from meddies_tts.plan import (
    PLAN_SCHEMA,
    audio_path,
    build_plan,
    compute_plan_hash,
    read_plan,
    shard_id,
    shard_repo_path,
    shard_totals,
    write_plan,
)
from meddies_tts.speakers import Speaker


def _cfg(**run_kwargs):
    return Config(hf=HFConfig(repo_id="Meddies/SynthAudio"), run=RunConfig(**run_kwargs))


def _pool(n=6):
    return [
        Speaker(i, f"/refs/speaker_{i:03d}.wav", "neutral", 100.0 + i, 12.0)
        for i in range(n)
    ]


def _manifest(n_convs=5, n_turns=2, text="Xin chào bác sĩ."):
    rows = []
    for c in range(n_convs):
        for t in range(1, n_turns + 1):
            for role in ("assistant", "user"):
                rows.append(
                    {
                        "config": "vietnamese",
                        "disease_slug": "suy_gan",
                        "disease_name": "Suy gan",
                        "conv_id": f"conv_{c:04d}",
                        "turn": t,
                        "role": role,
                        "text_raw": text,
                    }
                )
    columns = {name: [r[name] for r in rows] for name in MANIFEST_SCHEMA.names}
    return pa.Table.from_pydict(columns, schema=MANIFEST_SCHEMA)


_IDENTITY = type("N", (), {"normalize": staticmethod(lambda t: t)})()
# keyed by (config, speaker_id) - the dialect follows the speaker
_NORMALIZERS = {("vietnamese", sid): _IDENTITY for sid in range(6)}


def test_shard_id_is_prefixed_and_zero_padded():
    assert shard_id("vietnamese", 0) == "vi-00000"
    assert shard_id("english", 42) == "en-00042"


def test_shard_id_rejects_unknown_config():
    with pytest.raises(ValueError, match="klingon"):
        shard_id("klingon", 0)


def test_shard_repo_path_follows_hf_convention():
    assert shard_repo_path("vietnamese", 0, 473) == (
        "data/vietnamese/train-00000-of-00473.parquet"
    )


def test_audio_path_mirrors_the_output_full_tree():
    assert audio_path("vietnamese", "suy_gan", "conv_0001", 3, "user") == (
        "vietnamese/suy_gan/conv_0001/Turn3/user.flac"
    )


def test_plan_schema_matches(tmp_path):
    plan, _ = build_plan(_manifest(), _cfg(), _pool(), _NORMALIZERS)
    assert plan.schema.equals(PLAN_SCHEMA)


def test_plan_keeps_every_accepted_utterance():
    plan, rejects = build_plan(_manifest(n_convs=3, n_turns=2), _cfg(), _pool(), _NORMALIZERS)
    assert plan.num_rows == 3 * 2 * 2
    assert rejects == []


def test_degenerate_rows_are_rejected_not_planned():
    manifest = _manifest(n_convs=2, n_turns=1, text="x" * 5000)
    plan, rejects = build_plan(manifest, _cfg(), _pool(), _NORMALIZERS)
    assert plan.num_rows == 0
    assert len(rejects) == 4
    assert rejects[0]["reason"] == "too_long"
    assert rejects[0]["audio_path"].endswith(".flac")


def test_conversation_is_never_split_across_shards():
    plan, _ = build_plan(_manifest(n_convs=10), _cfg(convs_per_shard=3), _pool(), _NORMALIZERS)
    rows = plan.to_pylist()
    by_conv = {}
    for row in rows:
        by_conv.setdefault(row["conv_id"], set()).add(row["shard_id"])
    assert all(len(shards) == 1 for shards in by_conv.values())


def test_shards_respect_convs_per_shard():
    plan, _ = build_plan(_manifest(n_convs=10), _cfg(convs_per_shard=3), _pool(), _NORMALIZERS)
    rows = plan.to_pylist()
    per_shard = {}
    for row in rows:
        per_shard.setdefault(row["shard_id"], set()).add(row["conv_id"])
    assert sorted(len(v) for v in per_shard.values()) == [1, 3, 3, 3]


def test_shard_totals_counts_distinct_shards_per_config():
    plan, _ = build_plan(_manifest(n_convs=10), _cfg(convs_per_shard=3), _pool(), _NORMALIZERS)
    assert shard_totals(plan) == {"vietnamese": 4}


def test_speaker_is_constant_within_a_conversation_for_a_role():
    plan, _ = build_plan(_manifest(n_convs=2, n_turns=4), _cfg(), _pool(), _NORMALIZERS)
    rows = [r for r in plan.to_pylist() if r["conv_id"] == "conv_0000" and r["role"] == "user"]
    assert len({r["speaker_id"] for r in rows}) == 1


def test_speaker_metadata_columns_are_populated():
    plan, _ = build_plan(_manifest(n_convs=1), _cfg(), _pool(), _NORMALIZERS)
    row = plan.to_pylist()[0]
    assert row["speaker_emotions"] == "neutral"
    assert row["speaker_unique_source_s"] >= 100.0


def test_text_spoken_comes_from_the_normalizer():
    upper = type("N", (), {"normalize": staticmethod(str.upper)})()
    shouty = {("vietnamese", sid): upper for sid in range(6)}
    plan, _ = build_plan(_manifest(n_convs=1, n_turns=1), _cfg(), _pool(), shouty)
    row = plan.to_pylist()[0]
    assert row["text_raw"] == "Xin chào bác sĩ."
    assert row["text_spoken"] == "XIN CHÀO BÁC SĨ."


def test_dialect_follows_the_speaker():
    # Two speakers with different dialects must produce different text for the
    # same input, and the same speaker must always produce the same text.
    manifest = _manifest(n_convs=30, n_turns=1, text="Uống 1005 ml mỗi ngày.")
    plan, _ = build_plan(manifest, _cfg(), _pool(), None)
    rows = plan.to_pylist()
    by_speaker = {}
    for row in rows:
        by_speaker.setdefault(row["speaker_id"], set()).add(row["text_spoken"])
    assert all(len(v) == 1 for v in by_speaker.values())      # stable per speaker
    assert len({next(iter(v)) for v in by_speaker.values()}) > 1  # differs across speakers


def test_build_plan_is_deterministic():
    first, _ = build_plan(_manifest(n_convs=6), _cfg(), _pool(), _NORMALIZERS)
    second, _ = build_plan(_manifest(n_convs=6), _cfg(), _pool(), _NORMALIZERS)
    assert first.to_pylist() == second.to_pylist()


def test_plan_hash_is_stable_for_identical_inputs():
    cfg = _cfg()
    plan, _ = build_plan(_manifest(n_convs=4), cfg, _pool(), _NORMALIZERS)
    assert compute_plan_hash(plan, cfg) == compute_plan_hash(plan, cfg)


def test_plan_hash_changes_when_salt_changes():
    from dataclasses import replace

    from meddies_tts.config import SpeakerConfig

    cfg_a = _cfg()
    cfg_b = replace(cfg_a, speaker=SpeakerConfig(seed_salt="v2"))
    plan_a, _ = build_plan(_manifest(n_convs=4), cfg_a, _pool(), _NORMALIZERS)
    plan_b, _ = build_plan(_manifest(n_convs=4), cfg_b, _pool(), _NORMALIZERS)
    assert compute_plan_hash(plan_a, cfg_a) != compute_plan_hash(plan_b, cfg_b)


def test_plan_hash_is_unaffected_by_repo_id():
    from dataclasses import replace

    cfg_a = _cfg()
    cfg_b = replace(cfg_a, hf=HFConfig(repo_id="someone/scratch"))
    plan, _ = build_plan(_manifest(n_convs=4), cfg_a, _pool(), _NORMALIZERS)
    assert compute_plan_hash(plan, cfg_a) == compute_plan_hash(plan, cfg_b)


def test_plan_hash_changes_when_shard_packing_changes():
    cfg_a = _cfg(convs_per_shard=3)
    cfg_b = _cfg(convs_per_shard=5)
    plan_a, _ = build_plan(_manifest(n_convs=10), cfg_a, _pool(), _NORMALIZERS)
    plan_b, _ = build_plan(_manifest(n_convs=10), cfg_b, _pool(), _NORMALIZERS)
    assert compute_plan_hash(plan_a, cfg_a) != compute_plan_hash(plan_b, cfg_b)


def test_write_then_read_round_trips(tmp_path):
    plan, _ = build_plan(_manifest(n_convs=3), _cfg(), _pool(), _NORMALIZERS)
    path = tmp_path / "shard_plan.parquet"
    write_plan(plan, path)
    assert read_plan(path).to_pylist() == plan.to_pylist()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/tts/test_plan.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'meddies_tts.plan'`

- [ ] **Step 3: Write the implementation**

```python
# meddies_tts/plan.py
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from meddies_tts.config import Config
from meddies_tts.reject import check
from meddies_tts.speakers import Speaker, derive_seed, get_assigner
from meddies_tts.textprep import get_normalizer
from meddies_tts.vietnamese_numbers import dialect_from_seed

NORMALIZER_VERSION = "1"

CONFIG_PREFIX = {"vietnamese": "vi", "english": "en"}

PLAN_SCHEMA = pa.schema(
    [
        pa.field("config", pa.string()),
        pa.field("disease_slug", pa.string()),
        pa.field("disease_name", pa.string()),
        pa.field("conv_id", pa.string()),
        pa.field("turn", pa.int32()),
        pa.field("role", pa.string()),
        pa.field("text_raw", pa.string()),
        pa.field("text_spoken", pa.string()),
        pa.field("speaker_id", pa.int32()),
        pa.field("speaker_emotions", pa.string()),
        pa.field("speaker_unique_source_s", pa.float32()),
        pa.field("shard_id", pa.string()),
        pa.field("audio_path", pa.string()),
    ]
)


def shard_id(config: str, index: int) -> str:
    if config not in CONFIG_PREFIX:
        raise ValueError(f"no shard prefix registered for config {config!r}")
    return f"{CONFIG_PREFIX[config]}-{index:05d}"


def shard_repo_path(config: str, index: int, total: int) -> str:
    return f"data/{config}/train-{index:05d}-of-{total:05d}.parquet"


def audio_path(config: str, disease_slug: str, conv_id: str, turn: int, role: str) -> str:
    return f"{config}/{disease_slug}/{conv_id}/Turn{turn}/{role}.flac"


def build_plan(
    manifest: pa.Table,
    cfg: Config,
    pool: list[Speaker],
    normalizers: dict[tuple[str, int], object] | None = None,
) -> tuple[pa.Table, list[dict]]:
    """Normalize, reject, assign speakers and pack conversations into shards."""
    by_id = {speaker.speaker_id: speaker for speaker in pool}
    assigner = get_assigner(cfg.speaker, pool)
    cache: dict[tuple[str, int], object] = dict(normalizers or {})

    kept: list[dict] = []
    rejects: list[dict] = []
    for row in manifest.to_pylist():
        config = row["config"]
        if config not in cfg.run.configs:
            continue
        path = audio_path(config, row["disease_slug"], row["conv_id"], row["turn"], row["role"])
        rejection = check(row["text_raw"], cfg.text)
        if rejection is not None:
            rejects.append(
                {
                    "audio_path": path,
                    "reason": rejection.reason,
                    "detail": rejection.detail,
                    "text_raw": row["text_raw"],
                }
            )
            continue
        # Speaker FIRST: the Vietnamese dialect (linh/nghìn vs lẻ/ngàn, tư vs bốn)
        # is a property of the speaker, so normalization depends on this choice.
        speaker_id = assigner.assign(
            config, row["disease_slug"], row["conv_id"], row["turn"], row["role"]
        )
        speaker = by_id[speaker_id]

        key = (config, speaker_id)
        if key not in cache:
            dialect = dialect_from_seed(
                derive_seed(cfg.speaker.seed_salt, "dialect", speaker_id)
            )
            cache[key] = get_normalizer(config, dialect)
        spoken = cache[key].normalize(row["text_raw"])
        if not spoken:
            rejects.append(
                {
                    "audio_path": path,
                    "reason": "empty_after_normalization",
                    "detail": f"{len(row['text_raw'])} raw chars normalized to nothing",
                    "text_raw": row["text_raw"],
                }
            )
            continue
        kept.append(
            {
                **row,
                "text_spoken": spoken,
                "speaker_id": speaker_id,
                "speaker_emotions": speaker.emotions,
                "speaker_unique_source_s": speaker.unique_source_s,
                "audio_path": path,
                "shard_id": "",
            }
        )

    _assign_shards(kept, cfg.run.convs_per_shard)
    columns = {name: [row[name] for row in kept] for name in PLAN_SCHEMA.names}
    return pa.Table.from_pydict(columns, schema=PLAN_SCHEMA), rejects


def _assign_shards(rows: list[dict], convs_per_shard: int) -> None:
    """Stamp shard_id in place; conversations are packed whole, in sorted order."""
    by_config: dict[str, set[tuple[str, str, str]]] = {}
    for row in rows:
        key = (row["config"], row["disease_slug"], row["conv_id"])
        by_config.setdefault(row["config"], set()).add(key)

    index_of: dict[tuple[str, str, str], str] = {}
    for config, keys in by_config.items():
        for position, key in enumerate(sorted(keys)):
            index_of[key] = shard_id(config, position // convs_per_shard)

    for row in rows:
        row["shard_id"] = index_of[(row["config"], row["disease_slug"], row["conv_id"])]


def shard_totals(plan: pa.Table) -> dict[str, int]:
    totals: dict[str, set[str]] = {}
    for config, sid in zip(
        plan.column("config").to_pylist(), plan.column("shard_id").to_pylist()
    ):
        totals.setdefault(config, set()).add(sid)
    return {config: len(ids) for config, ids in totals.items()}


def compute_plan_hash(plan: pa.Table, cfg: Config) -> str:
    """Hash the identity of the work: conversations, speakers, packing, normalization.

    Deliberately excludes hf.repo_id — retargeting the destination must not
    invalidate a plan or orphan finished shards.
    """
    payload = {
        "normalizer_version": NORMALIZER_VERSION,
        "speaker_policy": cfg.speaker.policy,
        "speaker_pool": cfg.speaker.pool,
        "seed_salt": cfg.speaker.seed_salt,
        "convs_per_shard": cfg.run.convs_per_shard,
        "configs": list(cfg.run.configs),
        "rows": [
            [row["audio_path"], row["speaker_id"], row["shard_id"]]
            for row in plan.select(["audio_path", "speaker_id", "shard_id"]).to_pylist()
        ],
    }
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.blake2b(blob, digest_size=16).hexdigest()


def write_plan(plan: pa.Table, path: Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(plan, path, compression="zstd")


def read_plan(path: Path) -> pa.Table:
    return pq.read_table(path)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/tts/test_plan.py -v`
Expected: 20 passed

- [ ] **Step 5: Commit**

```bash
git add meddies_tts/plan.py tests/tts/test_plan.py
git commit -m "feat: add shard planning, audio paths and plan hashing"
```

---

### Task 8: Audio assembly — join, resample, encode

**Files:**
- Create: `meddies_tts/audio.py`
- Test: `tests/tts/test_audio.py`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: `TARGET_SAMPLE_RATE: int` (16000); `join_chunks(waves: list[np.ndarray], sample_rate: int, silence_ms: int) -> np.ndarray`; `resample(wave: np.ndarray, src_sr: int, dst_sr: int) -> np.ndarray`; `to_flac_bytes(wave: np.ndarray, sample_rate: int) -> bytes`; `duration_seconds(wave: np.ndarray, sample_rate: int) -> float`. Task 12 uses all of these.

- [ ] **Step 1: Write the failing test**

```python
# tests/tts/test_audio.py
import io

import numpy as np
import pytest
import soundfile as sf

from meddies_tts.audio import (
    TARGET_SAMPLE_RATE,
    duration_seconds,
    join_chunks,
    resample,
    to_flac_bytes,
)


def _tone(seconds, sample_rate=48000, freq=440.0):
    t = np.linspace(0, seconds, int(seconds * sample_rate), endpoint=False)
    return (0.3 * np.sin(2 * np.pi * freq * t)).astype(np.float32)


def test_target_sample_rate_is_16k():
    assert TARGET_SAMPLE_RATE == 16000


def test_single_chunk_is_returned_unchanged():
    wave = _tone(0.5)
    assert np.array_equal(join_chunks([wave], 48000, 250), wave)


def test_join_inserts_silence_between_chunks():
    wave = _tone(0.5)
    joined = join_chunks([wave, wave], 48000, 250)
    expected = len(wave) * 2 + int(48000 * 0.25)
    assert len(joined) == expected


def test_join_adds_no_trailing_silence():
    wave = _tone(0.1)
    joined = join_chunks([wave, wave, wave], 48000, 100)
    assert len(joined) == len(wave) * 3 + 2 * int(48000 * 0.1)


def test_join_of_empty_list_raises():
    with pytest.raises(ValueError, match="at least one"):
        join_chunks([], 48000, 250)


def test_join_preserves_float32_dtype():
    assert join_chunks([_tone(0.1), _tone(0.1)], 48000, 250).dtype == np.float32


def test_resample_changes_length_proportionally():
    wave = _tone(1.0, 48000)
    out = resample(wave, 48000, 16000)
    assert abs(len(out) - 16000) <= 8


def test_resample_is_identity_when_rates_match():
    wave = _tone(0.25, 16000)
    assert np.array_equal(resample(wave, 16000, 16000), wave)


def test_resample_preserves_a_440hz_tone():
    out = resample(_tone(1.0, 48000, 440.0), 48000, 16000)
    spectrum = np.abs(np.fft.rfft(out))
    peak_hz = np.fft.rfftfreq(len(out), 1 / 16000)[int(np.argmax(spectrum))]
    assert abs(peak_hz - 440.0) < 5.0


def test_flac_bytes_are_decodable():
    wave = _tone(0.5, 16000)
    decoded, sr = sf.read(io.BytesIO(to_flac_bytes(wave, 16000)), dtype="float32")
    assert sr == 16000
    assert len(decoded) == len(wave)


def test_flac_is_lossless_within_16bit_quantization():
    wave = _tone(0.5, 16000)
    decoded, _ = sf.read(io.BytesIO(to_flac_bytes(wave, 16000)), dtype="float32")
    assert np.max(np.abs(decoded - wave)) < 1e-3


def test_flac_output_is_mono():
    data = to_flac_bytes(_tone(0.2, 16000), 16000)
    with sf.SoundFile(io.BytesIO(data)) as handle:
        assert handle.channels == 1
        assert handle.format == "FLAC"


def test_flac_is_smaller_than_raw_pcm():
    wave = _tone(2.0, 16000)
    assert len(to_flac_bytes(wave, 16000)) < wave.nbytes


def test_duration_seconds():
    assert duration_seconds(np.zeros(32000, dtype=np.float32), 16000) == pytest.approx(2.0)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/tts/test_audio.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'meddies_tts.audio'`

- [ ] **Step 3: Write the implementation**

```python
# meddies_tts/audio.py
from __future__ import annotations

import io

import numpy as np
import soundfile as sf
import soxr

TARGET_SAMPLE_RATE = 16000


def join_chunks(waves: list[np.ndarray], sample_rate: int, silence_ms: int) -> np.ndarray:
    """Concatenate generated chunks, separated by silence, with no trailing pad."""
    if not waves:
        raise ValueError("join_chunks requires at least one wave")
    if len(waves) == 1:
        return waves[0].astype(np.float32, copy=False)
    gap = np.zeros(int(sample_rate * silence_ms / 1000), dtype=np.float32)
    pieces: list[np.ndarray] = []
    for index, wave in enumerate(waves):
        if index:
            pieces.append(gap)
        pieces.append(wave.astype(np.float32, copy=False))
    return np.concatenate(pieces).astype(np.float32, copy=False)


def resample(wave: np.ndarray, src_sr: int, dst_sr: int) -> np.ndarray:
    if src_sr == dst_sr:
        return wave.astype(np.float32, copy=False)
    return soxr.resample(wave, src_sr, dst_sr).astype(np.float32, copy=False)


def to_flac_bytes(wave: np.ndarray, sample_rate: int) -> bytes:
    buffer = io.BytesIO()
    sf.write(buffer, wave, sample_rate, format="FLAC", subtype="PCM_16")
    return buffer.getvalue()


def duration_seconds(wave: np.ndarray, sample_rate: int) -> float:
    return len(wave) / sample_rate
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/tts/test_audio.py -v`
Expected: 14 passed

- [ ] **Step 5: Commit**

```bash
git add meddies_tts/audio.py tests/tts/test_audio.py
git commit -m "feat: add audio joining, resampling and FLAC encoding"
```

---

### Task 9: Per-utterance QC checks

**Files:**
- Create: `meddies_tts/qc.py`
- Test: `tests/tts/test_qc.py`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: `DEFAULT_CHARS_PER_SEC: float` (14.0); `QCResult` frozen dataclass (`ok: bool`, `reason: str | None`, `detail: str`); `check_audio(wave: np.ndarray, sample_rate: int, n_chars: int, chars_per_sec: float = DEFAULT_CHARS_PER_SEC, min_ratio: float = 0.3, max_ratio: float = 3.0, silence_rms: float = 1e-4) -> QCResult`. Task 12 calls this after joining chunks.

- [ ] **Step 1: Write the failing test**

```python
# tests/tts/test_qc.py
import numpy as np

from meddies_tts.qc import DEFAULT_CHARS_PER_SEC, check_audio


def _tone(seconds, sample_rate=16000, amplitude=0.3):
    t = np.linspace(0, seconds, int(seconds * sample_rate), endpoint=False)
    return (amplitude * np.sin(2 * np.pi * 220 * t)).astype(np.float32)


def test_default_chars_per_sec_is_the_spec_assumption():
    assert DEFAULT_CHARS_PER_SEC == 14.0


def test_accepts_audio_of_the_expected_duration():
    # 140 chars at 14 chars/sec -> 10 s expected
    assert check_audio(_tone(10.0), 16000, 140).ok


def test_accepts_within_the_tolerance_band():
    assert check_audio(_tone(5.0), 16000, 140).ok   # 0.5x
    assert check_audio(_tone(25.0), 16000, 140).ok  # 2.5x


def test_rejects_empty_audio():
    result = check_audio(np.zeros(0, dtype=np.float32), 16000, 140)
    assert not result.ok
    assert result.reason == "empty"


def test_rejects_silent_audio():
    result = check_audio(np.zeros(160000, dtype=np.float32), 16000, 140)
    assert not result.ok
    assert result.reason == "silent"


def test_rejects_nan():
    wave = _tone(10.0)
    wave[100] = np.nan
    result = check_audio(wave, 16000, 140)
    assert not result.ok
    assert result.reason == "not_finite"


def test_rejects_inf():
    wave = _tone(10.0)
    wave[100] = np.inf
    assert check_audio(wave, 16000, 140).reason == "not_finite"


def test_rejects_truncated_audio():
    result = check_audio(_tone(1.0), 16000, 140)  # 0.1x expected
    assert not result.ok
    assert result.reason == "too_short"


def test_rejects_runaway_audio():
    result = check_audio(_tone(60.0), 16000, 140)  # ~6x expected
    assert not result.ok
    assert result.reason == "too_long"


def test_zero_length_text_is_rejected_before_duration_maths():
    assert check_audio(_tone(1.0), 16000, 0).reason == "no_text"


def test_calibrated_chars_per_sec_shifts_the_band():
    # 280 chars at 28 chars/sec -> 10 s expected, so 10 s of audio is fine
    assert check_audio(_tone(10.0), 16000, 280, chars_per_sec=28.0).ok


def test_detail_is_populated_on_failure():
    assert check_audio(_tone(1.0), 16000, 140).detail
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/tts/test_qc.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'meddies_tts.qc'`

- [ ] **Step 3: Write the implementation**

```python
# meddies_tts/qc.py
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

DEFAULT_CHARS_PER_SEC = 14.0


@dataclass(frozen=True)
class QCResult:
    ok: bool
    reason: str | None = None
    detail: str = ""


_OK = QCResult(True)


def check_audio(
    wave: np.ndarray,
    sample_rate: int,
    n_chars: int,
    chars_per_sec: float = DEFAULT_CHARS_PER_SEC,
    min_ratio: float = 0.3,
    max_ratio: float = 3.0,
    silence_rms: float = 1e-4,
) -> QCResult:
    """Cheap sanity checks catching dead, truncated and runaway generations."""
    if wave.size == 0:
        return QCResult(False, "empty", "generated 0 samples")
    if not np.all(np.isfinite(wave)):
        return QCResult(False, "not_finite", "wave contains NaN or inf")
    rms = float(np.sqrt(np.mean(np.square(wave, dtype=np.float64))))
    if rms < silence_rms:
        return QCResult(False, "silent", f"rms={rms:.2e} < {silence_rms:.0e}")
    if n_chars <= 0:
        return QCResult(False, "no_text", "utterance has no spoken text")

    duration = wave.size / sample_rate
    expected = n_chars / chars_per_sec
    ratio = duration / expected
    if ratio < min_ratio:
        return QCResult(
            False, "too_short", f"{duration:.1f}s vs expected {expected:.1f}s (x{ratio:.2f})"
        )
    if ratio > max_ratio:
        return QCResult(
            False, "too_long", f"{duration:.1f}s vs expected {expected:.1f}s (x{ratio:.2f})"
        )
    return _OK
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/tts/test_qc.py -v`
Expected: 12 passed

- [ ] **Step 5: Commit**

```bash
git add meddies_tts/qc.py tests/tts/test_qc.py
git commit -m "feat: add per-utterance audio QC checks"
```

---

### Task 10: Parquet shard writer with the HF Audio feature

**Files:**
- Create: `meddies_tts/writer.py`
- Test: `tests/tts/test_writer.py`

**Interfaces:**
- Consumes: `TARGET_SAMPLE_RATE` (Task 8).
- Produces: `FEATURES: datasets.Features`; `build_row(plan_row: dict, flac_bytes: bytes, duration_s: float, n_chunks: int, seed: int, engine_version: str) -> dict`; `write_shard(rows: list[dict], path: Path, plan_hash: str, config_json: str) -> None`. Task 12 calls both.

`write_shard` embeds `plan_hash` and the resolved config in the Parquet key-value metadata, which Task 13 reads back for drift detection.

- [ ] **Step 1: Write the failing test**

```python
# tests/tts/test_writer.py
import io

import pyarrow.parquet as pq
import soundfile as sf
from datasets import load_dataset

from meddies_tts.audio import to_flac_bytes
from meddies_tts.writer import FEATURES, build_row, write_shard
import numpy as np


def _plan_row():
    return {
        "config": "vietnamese",
        "disease_slug": "ap_xe_hau_mon",
        "disease_name": "Áp xe hậu môn",
        "conv_id": "conv_0001",
        "turn": 1,
        "role": "user",
        "text_raw": "**Sốt cao (>38.5°C)**",
        "text_spoken": "Sốt cao trên ba mươi tám phẩy năm độ C",
        "speaker_id": 73,
        "speaker_emotions": "angry|happy|neutral|sad",
        "speaker_unique_source_s": 412.7,
        "shard_id": "vi-00000",
        "audio_path": "vietnamese/ap_xe_hau_mon/conv_0001/Turn1/user.flac",
    }


def _flac(seconds=1.0, sample_rate=16000):
    t = np.linspace(0, seconds, int(seconds * sample_rate), endpoint=False)
    return to_flac_bytes((0.3 * np.sin(2 * np.pi * 220 * t)).astype(np.float32), sample_rate)


def test_features_declare_16k_audio():
    assert FEATURES["audio"].sampling_rate == 16000


def test_build_row_has_every_declared_column():
    row = build_row(_plan_row(), _flac(), 1.0, 1, 12345, "nanovllm-0.1")
    assert set(row) == set(FEATURES)


def test_build_row_keeps_both_text_columns():
    row = build_row(_plan_row(), _flac(), 1.0, 1, 12345, "nanovllm-0.1")
    assert row["text_raw"] == "**Sốt cao (>38.5°C)**"
    assert row["text_spoken"].startswith("Sốt cao trên")


def test_build_row_sets_audio_path_to_the_tree_path():
    row = build_row(_plan_row(), _flac(), 1.0, 1, 12345, "nanovllm-0.1")
    assert row["audio"]["path"] == "vietnamese/ap_xe_hau_mon/conv_0001/Turn1/user.flac"


def test_build_row_carries_provenance():
    row = build_row(_plan_row(), _flac(), 2.5, 3, 999, "nanovllm-0.1")
    assert row["duration_s"] == 2.5
    assert row["n_chunks"] == 3
    assert row["seed"] == 999
    assert row["engine_version"] == "nanovllm-0.1"


def test_build_row_drops_planning_only_columns():
    row = build_row(_plan_row(), _flac(), 1.0, 1, 1, "v")
    assert "shard_id" not in row
    assert "audio_path" not in row


def test_write_shard_creates_a_readable_parquet(tmp_path):
    rows = [build_row(_plan_row(), _flac(), 1.0, 1, 1, "v")]
    path = tmp_path / "train-00000-of-00001.parquet"
    write_shard(rows, path, "abc123", "{}")
    assert pq.read_table(path).num_rows == 1


def test_write_shard_embeds_plan_hash_in_metadata(tmp_path):
    path = tmp_path / "shard.parquet"
    write_shard([build_row(_plan_row(), _flac(), 1.0, 1, 1, "v")], path, "abc123", '{"a":1}')
    metadata = pq.read_table(path).schema.metadata
    assert metadata[b"plan_hash"] == b"abc123"
    assert metadata[b"config_json"] == b'{"a":1}'


def test_shard_loads_via_datasets_with_decodable_audio(tmp_path):
    path = tmp_path / "train-00000-of-00001.parquet"
    write_shard([build_row(_plan_row(), _flac(2.0), 2.0, 1, 1, "v")], path, "h", "{}")
    ds = load_dataset("parquet", data_files=str(path), split="train")
    record = ds[0]
    assert record["text_spoken"].startswith("Sốt cao trên")
    assert record["audio"]["sampling_rate"] == 16000
    assert len(record["audio"]["array"]) == 32000


def test_written_audio_bytes_are_flac(tmp_path):
    path = tmp_path / "shard.parquet"
    write_shard([build_row(_plan_row(), _flac(), 1.0, 1, 1, "v")], path, "h", "{}")
    raw = pq.read_table(path).column("audio").to_pylist()[0]["bytes"]
    with sf.SoundFile(io.BytesIO(raw)) as handle:
        assert handle.format == "FLAC"


def test_empty_row_list_raises(tmp_path):
    import pytest

    with pytest.raises(ValueError, match="no rows"):
        write_shard([], tmp_path / "shard.parquet", "h", "{}")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/tts/test_writer.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'meddies_tts.writer'`

- [ ] **Step 3: Write the implementation**

```python
# meddies_tts/writer.py
from __future__ import annotations

from pathlib import Path

import pyarrow.parquet as pq
from datasets import Audio, Dataset, Features, Value

from meddies_tts.audio import TARGET_SAMPLE_RATE

FEATURES = Features(
    {
        "config": Value("string"),
        "disease_slug": Value("string"),
        "disease_name": Value("string"),
        "conv_id": Value("string"),
        "turn": Value("int32"),
        "role": Value("string"),
        "text_raw": Value("string"),
        "text_spoken": Value("string"),
        "speaker_id": Value("int32"),
        "speaker_emotions": Value("string"),
        "speaker_unique_source_s": Value("float32"),
        "audio": Audio(sampling_rate=TARGET_SAMPLE_RATE),
        "duration_s": Value("float32"),
        "n_chunks": Value("int32"),
        "seed": Value("int64"),
        "engine_version": Value("string"),
    }
)

_PLANNING_ONLY = ("shard_id", "audio_path")


def build_row(
    plan_row: dict,
    flac_bytes: bytes,
    duration_s: float,
    n_chunks: int,
    seed: int,
    engine_version: str,
) -> dict:
    """Turn a plan row plus generated audio into a published dataset row."""
    row = {key: value for key, value in plan_row.items() if key not in _PLANNING_ONLY}
    row["audio"] = {"bytes": flac_bytes, "path": plan_row["audio_path"]}
    row["duration_s"] = duration_s
    row["n_chunks"] = n_chunks
    row["seed"] = seed
    row["engine_version"] = engine_version
    return row


def write_shard(rows: list[dict], path: Path, plan_hash: str, config_json: str) -> None:
    """Write one shard, embedding plan_hash and resolved config as file metadata."""
    if not rows:
        raise ValueError("write_shard received no rows")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    dataset = Dataset.from_list(rows, features=FEATURES)
    table = dataset.data.table
    # Preserve datasets' own b"huggingface" schema metadata (it carries the Audio
    # feature declaration) and add our provenance keys alongside it.
    metadata = dict(table.schema.metadata or {})
    metadata[b"plan_hash"] = plan_hash.encode("utf-8")
    metadata[b"config_json"] = config_json.encode("utf-8")
    pq.write_table(table.replace_schema_metadata(metadata), path, compression="zstd")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/tts/test_writer.py -v`
Expected: 11 passed

- [ ] **Step 5: Commit**

```bash
git add meddies_tts/writer.py tests/tts/test_writer.py
git commit -m "feat: add parquet shard writer with HF Audio feature"
```

---

### Task 11: Engine protocol and FakeEngine

**Files:**
- Create: `meddies_tts/engine.py`
- Create: `tests/tts/fakes.py`
- Test: `tests/tts/test_fakes.py`
- Modify: `pytest.ini`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: `TTSEngine` Protocol with `sample_rate: int`, `async encode_reference(self, wav_bytes: bytes) -> bytes`, `async synthesize(self, text: str, ref_latents: bytes, seed: int) -> np.ndarray`, and `version: str`. `tests/tts/fakes.py` provides `FakeEngine(sample_rate=48000, chars_per_sec=14.0, fail_texts=(), fail_times=0)`. Task 12 depends only on the Protocol; Tasks 12–14 test against `FakeEngine`; Task 15 supplies the real implementation.

**This task creates `meddies_tts/engine.py` containing ONLY the Protocol — no GPU imports.** Task 15 adds the CUDA-dependent implementation in the same file behind a lazy import.

- [ ] **Step 1: Enable asyncio tests**

Replace `pytest.ini` with:

```ini
[pytest]
pythonpath = .
asyncio_mode = auto
```

- [ ] **Step 2: Write the failing test**

```python
# tests/tts/test_fakes.py
import numpy as np
import pytest

from tests.tts.fakes import FakeEngine


async def test_synthesize_returns_float32_audio():
    wave = await FakeEngine().synthesize("xin chào bác sĩ", b"ref", 1)
    assert wave.dtype == np.float32
    assert wave.size > 0


async def test_duration_scales_with_text_length():
    engine = FakeEngine(sample_rate=16000, chars_per_sec=10.0)
    short = await engine.synthesize("x" * 50, b"ref", 1)
    long = await engine.synthesize("x" * 200, b"ref", 1)
    assert len(long) == pytest.approx(4 * len(short), rel=0.05)


async def test_duration_matches_chars_per_sec():
    engine = FakeEngine(sample_rate=16000, chars_per_sec=10.0)
    wave = await engine.synthesize("x" * 100, b"ref", 1)
    assert len(wave) / 16000 == pytest.approx(10.0, rel=0.02)


async def test_same_seed_gives_identical_audio():
    engine = FakeEngine()
    a = await engine.synthesize("xin chào", b"ref", 42)
    b = await engine.synthesize("xin chào", b"ref", 42)
    assert np.array_equal(a, b)


async def test_different_seed_gives_different_audio():
    engine = FakeEngine()
    a = await engine.synthesize("xin chào", b"ref", 1)
    b = await engine.synthesize("xin chào", b"ref", 2)
    assert not np.array_equal(a, b)


async def test_encode_reference_returns_bytes():
    assert isinstance(await FakeEngine().encode_reference(b"RIFF"), bytes)


async def test_records_calls_for_assertions():
    engine = FakeEngine()
    await engine.synthesize("một", b"ref", 1)
    await engine.synthesize("hai", b"ref", 2)
    assert [call.text for call in engine.calls] == ["một", "hai"]


async def test_fail_texts_raise_until_retries_are_exhausted():
    engine = FakeEngine(fail_texts=("boom",), fail_times=2)
    with pytest.raises(RuntimeError):
        await engine.synthesize("boom", b"ref", 1)
    with pytest.raises(RuntimeError):
        await engine.synthesize("boom", b"ref", 2)
    wave = await engine.synthesize("boom", b"ref", 3)
    assert wave.size > 0


async def test_tracks_peak_concurrency():
    import asyncio

    engine = FakeEngine()
    await asyncio.gather(*(engine.synthesize(f"t{i}", b"ref", i) for i in range(8)))
    assert engine.peak_concurrency >= 2
```

- [ ] **Step 3: Run test to verify it fails**

Run: `pytest tests/tts/test_fakes.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'tests.tts.fakes'`

- [ ] **Step 4: Write the implementation**

```python
# meddies_tts/engine.py
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
```

```python
# tests/tts/fakes.py
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
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/tts/test_fakes.py -v`
Expected: 9 passed

- [ ] **Step 6: Commit**

```bash
git add meddies_tts/engine.py tests/tts/fakes.py tests/tts/test_fakes.py pytest.ini
git commit -m "feat: add TTSEngine protocol and FakeEngine for GPU-free testing"
```

---

### Task 12: Shard runner — the batching core

**Files:**
- Create: `meddies_tts/runner.py`
- Test: `tests/tts/test_runner.py`

**Interfaces:**
- Consumes: `Config` (1), `chunk_text` (5), `derive_seed` (6), `join_chunks`/`resample`/`to_flac_bytes`/`duration_seconds`/`TARGET_SAMPLE_RATE` (8), `check_audio`/`DEFAULT_CHARS_PER_SEC` (9), `build_row` (10), `TTSEngine` (11).
- Produces: `ShardResult` frozen dataclass (`shard_id: str`, `n_utterances: int`, `n_failed: int`, `audio_seconds: float`, `failures: list[dict]`); `async run_shard(shard_id: str, plan_rows: list[dict], engine: TTSEngine, refs: dict[int, bytes], cfg: Config, chars_per_sec: float = DEFAULT_CHARS_PER_SEC, max_chunk_retries: int = 2) -> tuple[list[dict], ShardResult]`. Task 16 calls `run_shard`.

**This is where the vLLM lesson lives.** All chunks of all utterances in the shard are submitted concurrently and throttled only by `asyncio.Semaphore(cfg.engine.concurrency)`, so the engine always has work to batch. Do not serialize utterances.

- [ ] **Step 1: Write the failing test**

```python
# tests/tts/test_runner.py
import pytest

from meddies_tts.audio import TARGET_SAMPLE_RATE
from meddies_tts.config import Config, EngineConfig, HFConfig, TextConfig
from meddies_tts.runner import run_shard
from tests.tts.fakes import FakeEngine


def _cfg(concurrency=8, chunk_chars=400):
    return Config(
        hf=HFConfig(repo_id="Meddies/SynthAudio"),
        engine=EngineConfig(concurrency=concurrency, max_num_seqs=concurrency),
        text=TextConfig(chunk_chars=chunk_chars),
    )


def _row(index=0, text="Xin chào bác sĩ. Tôi bị đau bụng."):
    return {
        "config": "vietnamese",
        "disease_slug": "suy_gan",
        "disease_name": "Suy gan",
        "conv_id": f"conv_{index // 4:04d}",
        "turn": (index % 4) + 1,
        "role": "user" if index % 2 == 0 else "assistant",
        "text_raw": text,
        "text_spoken": text,
        "speaker_id": 0,
        "speaker_emotions": "neutral",
        "speaker_unique_source_s": 100.0,
        "shard_id": "vi-00000",
        "audio_path": f"vietnamese/suy_gan/conv_{index:04d}/Turn1/user.flac",
    }


_REFS = {0: b"latents-0"}


async def test_produces_one_row_per_utterance():
    rows, result = await run_shard("vi-00000", [_row(i) for i in range(5)],
                                   FakeEngine(), _REFS, _cfg())
    assert len(rows) == 5
    assert result.n_utterances == 5
    assert result.n_failed == 0


async def test_result_reports_shard_id_and_audio_seconds():
    rows, result = await run_shard("vi-00000", [_row(0)], FakeEngine(), _REFS, _cfg())
    assert result.shard_id == "vi-00000"
    assert result.audio_seconds == pytest.approx(rows[0]["duration_s"], rel=1e-3)


async def test_audio_is_resampled_to_16k():
    rows, _ = await run_shard("vi-00000", [_row(0)], FakeEngine(sample_rate=48000),
                              _REFS, _cfg())
    import io

    import soundfile as sf

    with sf.SoundFile(io.BytesIO(rows[0]["audio"]["bytes"])) as handle:
        assert handle.samplerate == TARGET_SAMPLE_RATE


async def test_keeps_the_engine_busy_with_many_concurrent_requests():
    engine = FakeEngine()
    await run_shard("vi-00000", [_row(i) for i in range(40)], engine, _REFS, _cfg(concurrency=8))
    assert engine.peak_concurrency > 1


async def test_never_exceeds_the_configured_concurrency():
    engine = FakeEngine()
    await run_shard("vi-00000", [_row(i) for i in range(40)], engine, _REFS, _cfg(concurrency=4))
    assert engine.peak_concurrency <= 4


async def test_long_text_is_chunked_and_n_chunks_recorded():
    text = " ".join(f"Đây là câu số {i}." for i in range(60))
    rows, _ = await run_shard("vi-00000", [_row(0, text)], FakeEngine(), _REFS,
                              _cfg(chunk_chars=120))
    assert rows[0]["n_chunks"] > 1


async def test_short_text_is_a_single_chunk():
    rows, _ = await run_shard("vi-00000", [_row(0)], FakeEngine(), _REFS, _cfg())
    assert rows[0]["n_chunks"] == 1


async def test_generation_is_deterministic_for_the_same_row():
    first, _ = await run_shard("vi-00000", [_row(0)], FakeEngine(), _REFS, _cfg())
    second, _ = await run_shard("vi-00000", [_row(0)], FakeEngine(), _REFS, _cfg())
    assert first[0]["seed"] == second[0]["seed"]
    assert first[0]["audio"]["bytes"] == second[0]["audio"]["bytes"]


async def test_different_utterances_get_different_seeds():
    rows, _ = await run_shard("vi-00000", [_row(0), _row(1)], FakeEngine(), _REFS, _cfg())
    assert rows[0]["seed"] != rows[1]["seed"]


async def test_transient_chunk_failure_is_retried_and_succeeds():
    text = "Một câu duy nhất."
    engine = FakeEngine(fail_texts=(text,), fail_times=1)
    rows, result = await run_shard("vi-00000", [_row(0, text)], engine, _REFS, _cfg())
    assert len(rows) == 1
    assert result.n_failed == 0


async def test_permanent_chunk_failure_drops_only_that_utterance():
    bad = "Câu hỏng."
    engine = FakeEngine(fail_texts=(bad,), fail_times=99)
    plan = [_row(0), _row(1, bad), _row(2)]
    rows, result = await run_shard("vi-00000", plan, engine, _REFS, _cfg())
    assert len(rows) == 2
    assert result.n_failed == 1
    assert result.failures[0]["audio_path"] == plan[1]["audio_path"]
    assert result.failures[0]["reason"] == "engine_error"


async def test_qc_failure_is_recorded_as_a_failure():
    # chars_per_sec far from the fake engine's rate makes every duration look wrong
    engine = FakeEngine(chars_per_sec=14.0)
    rows, result = await run_shard("vi-00000", [_row(0)], engine, _REFS, _cfg(),
                                   chars_per_sec=1000.0)
    assert rows == []
    assert result.n_failed == 1
    assert result.failures[0]["reason"].startswith("qc:")


async def test_a_failing_utterance_does_not_abort_the_shard():
    bad = "Câu hỏng."
    engine = FakeEngine(fail_texts=(bad,), fail_times=99)
    plan = [_row(i) for i in range(10)] + [_row(99, bad)]
    rows, result = await run_shard("vi-00000", plan, engine, _REFS, _cfg())
    assert len(rows) == 10
    assert result.n_utterances == 11


async def test_row_order_follows_the_plan():
    plan = [_row(i) for i in range(6)]
    rows, _ = await run_shard("vi-00000", plan, FakeEngine(), _REFS, _cfg())
    assert [r["conv_id"] for r in rows] == [p["conv_id"] for p in plan]


async def test_missing_reference_latents_raises():
    with pytest.raises(KeyError):
        await run_shard("vi-00000", [_row(0)], FakeEngine(), {}, _cfg())
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/tts/test_runner.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'meddies_tts.runner'`

- [ ] **Step 3: Write the implementation**

```python
# meddies_tts/runner.py
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
    last: Exception | None = None
    for attempt in range(max_retries + 1):
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
    chunks = chunk_text(row["text_spoken"], cfg.text.chunk_chars)
    seeds = [
        derive_seed(cfg.speaker.seed_salt, row["audio_path"], f"{salt_suffix}#{index}")
        for index in range(len(chunks))
    ]
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
    ref_latents = refs[row["speaker_id"]]
    last_reason = ""
    for salt_suffix in ("", _QC_RETRY_TAG):
        try:
            wave, n_chunks, seed = await _synthesize_once(
                row, engine, semaphore, ref_latents, cfg, salt_suffix, max_chunk_retries
            )
        except Exception as error:  # noqa: BLE001 - recorded as a shard failure
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/tts/test_runner.py -v`
Expected: 15 passed

- [ ] **Step 5: Run the whole GPU-free suite**

Run: `pytest tests/tts -v`
Expected: all pass — the full Stage 2 pipeline now runs end-to-end on the Mac with no GPU.

- [ ] **Step 6: Commit**

```bash
git add meddies_tts/runner.py tests/tts/test_runner.py
git commit -m "feat: add shard runner with semaphore-bounded concurrent generation"
```

---

### Task 13: Hub client — preflight, resume diff, drift detection

**Files:**
- Create: `meddies_tts/hub.py`
- Test: `tests/tts/test_hub.py`

**Interfaces:**
- Consumes: `shard_repo_path`/`shard_totals` (Task 7).
- Produces: `HubError`; `PlanDriftError`; `plan_path(config: str) -> str`; `plan_hash_path(config: str) -> str`; `preflight(api, repo_id: str, private: bool = False) -> None`; `list_repo_paths(api, repo_id: str) -> set[str]`; `shard_targets(plan) -> list[tuple[str, str]]`; `remaining_targets(plan, existing: set[str]) -> list[tuple[str, str]]`; `read_text(api, repo_id: str, path_in_repo: str) -> str | None`; `check_plan_drift(api, repo_id: str, config: str, local_hash: str) -> None`; `upload_bytes(api, repo_id, data: bytes, path_in_repo: str) -> None`; `upload_path(api, repo_id, local_path, path_in_repo: str) -> None`. Tasks 14 and 16 consume these.

All functions take an `api` object (duck-typed `HfApi`) as their first argument so tests never touch the network.

- [ ] **Step 1: Write the failing test**

```python
# tests/tts/test_hub.py
import pyarrow as pa
import pytest

from meddies_tts.hub import (
    HubError,
    PlanDriftError,
    check_plan_drift,
    list_repo_paths,
    plan_hash_path,
    plan_path,
    preflight,
    remaining_targets,
    shard_targets,
    upload_bytes,
)
from meddies_tts.plan import PLAN_SCHEMA


class FakeApi:
    def __init__(self, files=(), writable=True, exists=True, whoami=None):
        self.files = list(files)
        self._writable = writable
        self._exists = exists
        self._whoami = whoami if whoami is not None else {"name": "tester"}
        self.created = []
        self.uploaded = []
        self.deleted = []

    def whoami(self):
        if self._whoami is None:
            raise RuntimeError("invalid token")
        return self._whoami

    def repo_exists(self, repo_id, repo_type=None):
        return self._exists

    def create_repo(self, repo_id, repo_type=None, private=False, exist_ok=True):
        self.created.append((repo_id, repo_type, private))
        self._exists = True

    def list_repo_files(self, repo_id, repo_type=None):
        if not self._exists:
            raise RuntimeError("repo not found")
        return list(self.files)

    def upload_file(self, path_or_fileobj=None, path_in_repo=None, repo_id=None,
                    repo_type=None, revision=None):
        if not self._writable:
            raise RuntimeError("403 Forbidden: write access required")
        self.uploaded.append(path_in_repo)
        self.files.append(path_in_repo)

    def delete_file(self, path_in_repo=None, repo_id=None, repo_type=None, revision=None):
        self.deleted.append(path_in_repo)
        if path_in_repo in self.files:
            self.files.remove(path_in_repo)

    def hf_hub_download(self, repo_id, filename, repo_type=None):
        raise NotImplementedError


def _plan(shard_ids):
    rows = []
    for sid in shard_ids:
        rows.append(
            {
                "config": "vietnamese", "disease_slug": "d", "disease_name": "D",
                "conv_id": "conv_0001", "turn": 1, "role": "user",
                "text_raw": "x", "text_spoken": "x", "speaker_id": 0,
                "speaker_emotions": "neutral", "speaker_unique_source_s": 1.0,
                "shard_id": sid, "audio_path": f"vietnamese/d/{sid}/Turn1/user.flac",
            }
        )
    columns = {name: [r[name] for r in rows] for name in PLAN_SCHEMA.names}
    return pa.Table.from_pydict(columns, schema=PLAN_SCHEMA)


def test_plan_paths_are_namespaced_by_config():
    assert plan_path("vietnamese") == "plan/shard_plan-vietnamese.parquet"
    assert plan_hash_path("vietnamese") == "plan/plan_hash-vietnamese.txt"


def test_preflight_passes_on_a_writable_existing_repo():
    api = FakeApi()
    preflight(api, "Meddies/SynthAudio")
    assert api.uploaded and api.deleted


def test_preflight_creates_a_missing_repo():
    api = FakeApi(exists=False)
    preflight(api, "Meddies/SynthAudio", private=False)
    assert api.created == [("Meddies/SynthAudio", "dataset", False)]


def test_preflight_rejects_an_invalid_token():
    with pytest.raises(HubError, match="token"):
        preflight(FakeApi(whoami=None), "Meddies/SynthAudio")


def test_preflight_rejects_a_read_only_token():
    with pytest.raises(HubError, match="write"):
        preflight(FakeApi(writable=False), "Meddies/SynthAudio")


def test_preflight_cleans_up_its_probe_file():
    api = FakeApi()
    preflight(api, "Meddies/SynthAudio")
    assert api.files == []


def test_list_repo_paths_returns_a_set():
    assert list_repo_paths(FakeApi(files=["a", "b"]), "r") == {"a", "b"}


def test_shard_targets_pairs_ids_with_hf_paths():
    targets = shard_targets(_plan(["vi-00000", "vi-00001"]))
    assert targets == [
        ("vi-00000", "data/vietnamese/train-00000-of-00002.parquet"),
        ("vi-00001", "data/vietnamese/train-00001-of-00002.parquet"),
    ]


def test_remaining_targets_excludes_uploaded_shards():
    plan = _plan(["vi-00000", "vi-00001", "vi-00002"])
    existing = {"data/vietnamese/train-00001-of-00003.parquet"}
    assert [sid for sid, _ in remaining_targets(plan, existing)] == ["vi-00000", "vi-00002"]


def test_remaining_targets_is_empty_when_all_present():
    plan = _plan(["vi-00000"])
    existing = {"data/vietnamese/train-00000-of-00001.parquet"}
    assert remaining_targets(plan, existing) == []


def test_remaining_targets_ignores_unrelated_repo_files():
    plan = _plan(["vi-00000"])
    assert len(remaining_targets(plan, {"README.md", "plan/x.parquet"})) == 1


def test_check_plan_drift_passes_when_hashes_match(monkeypatch):
    api = FakeApi(files=[plan_hash_path("vietnamese")])
    monkeypatch.setattr("meddies_tts.hub.read_text", lambda *a, **k: "abc123")
    check_plan_drift(api, "r", "vietnamese", "abc123")


def test_check_plan_drift_passes_when_no_remote_hash(monkeypatch):
    monkeypatch.setattr("meddies_tts.hub.read_text", lambda *a, **k: None)
    check_plan_drift(FakeApi(), "r", "vietnamese", "abc123")


def test_check_plan_drift_raises_on_mismatch(monkeypatch):
    monkeypatch.setattr("meddies_tts.hub.read_text", lambda *a, **k: "OLDHASH")
    with pytest.raises(PlanDriftError, match="OLDHASH"):
        check_plan_drift(FakeApi(), "r", "vietnamese", "NEWHASH")


def test_upload_bytes_writes_to_the_given_path():
    api = FakeApi()
    upload_bytes(api, "r", b"data", "plan/plan_hash-vietnamese.txt")
    assert api.uploaded == ["plan/plan_hash-vietnamese.txt"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/tts/test_hub.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'meddies_tts.hub'`

- [ ] **Step 3: Write the implementation**

```python
# meddies_tts/hub.py
from __future__ import annotations

import io
from pathlib import Path

import pyarrow as pa

from meddies_tts.plan import shard_repo_path, shard_totals

_REPO_TYPE = "dataset"
_PROBE_PATH = ".meddies_tts_preflight"


class HubError(RuntimeError):
    """Raised when the Hub is unusable for this run."""


class PlanDriftError(RuntimeError):
    """Raised when the local plan disagrees with what produced the published shards."""


def plan_path(config: str) -> str:
    return f"plan/shard_plan-{config}.parquet"


def plan_hash_path(config: str) -> str:
    return f"plan/plan_hash-{config}.txt"


def preflight(api, repo_id: str, private: bool = False) -> None:
    """Verify token, repo and write access before any GPU is requested."""
    try:
        api.whoami()
    except Exception as error:  # noqa: BLE001
        raise HubError(
            f"Hugging Face token is missing or invalid ({error}). Check the Modal "
            "Secret named by hf.token_secret."
        ) from error

    if not api.repo_exists(repo_id, repo_type=_REPO_TYPE):
        try:
            api.create_repo(repo_id, repo_type=_REPO_TYPE, private=private, exist_ok=True)
        except Exception as error:  # noqa: BLE001
            raise HubError(f"cannot create dataset repo {repo_id!r}: {error}") from error

    try:
        api.upload_file(
            path_or_fileobj=io.BytesIO(b"preflight"),
            path_in_repo=_PROBE_PATH,
            repo_id=repo_id,
            repo_type=_REPO_TYPE,
        )
    except Exception as error:  # noqa: BLE001
        raise HubError(
            f"token lacks write access to {repo_id!r}: {error}. A read-scoped token "
            "would only fail after a shard had already been generated."
        ) from error

    api.delete_file(path_in_repo=_PROBE_PATH, repo_id=repo_id, repo_type=_REPO_TYPE)
    list_repo_paths(api, repo_id)


def list_repo_paths(api, repo_id: str) -> set[str]:
    """One call, not one per shard — this is what resumption diffs against."""
    try:
        return set(api.list_repo_files(repo_id, repo_type=_REPO_TYPE))
    except Exception as error:  # noqa: BLE001
        raise HubError(f"cannot list files in {repo_id!r}: {error}") from error


def shard_targets(plan: pa.Table) -> list[tuple[str, str]]:
    """Every (shard_id, repo_path) the plan expects, in shard order."""
    totals = shard_totals(plan)
    seen: dict[str, str] = {}
    for config, sid in zip(
        plan.column("config").to_pylist(), plan.column("shard_id").to_pylist()
    ):
        if sid in seen:
            continue
        index = int(sid.split("-")[1])
        seen[sid] = shard_repo_path(config, index, totals[config])
    return [(sid, seen[sid]) for sid in sorted(seen)]


def remaining_targets(plan: pa.Table, existing: set[str]) -> list[tuple[str, str]]:
    return [(sid, path) for sid, path in shard_targets(plan) if path not in existing]


def read_text(api, repo_id: str, path_in_repo: str) -> str | None:
    try:
        local = api.hf_hub_download(repo_id, path_in_repo, repo_type=_REPO_TYPE)
    except Exception:  # noqa: BLE001 - absent file is the common, benign case
        return None
    return Path(local).read_text(encoding="utf-8").strip()


def check_plan_drift(api, repo_id: str, config: str, local_hash: str) -> None:
    """Refuse to dispatch when the local plan differs from the published one."""
    remote = read_text(api, repo_id, plan_hash_path(config))
    if remote is None or remote == local_hash:
        return
    raise PlanDriftError(
        f"plan hash mismatch for config {config!r}: published shards were produced by "
        f"plan {remote}, local plan is {local_hash}. Re-planning changed the work "
        "partition; dispatching now would write incompatible shards alongside the old "
        "ones. Restore the published plan, or start a fresh repo."
    )


def upload_bytes(api, repo_id: str, data: bytes, path_in_repo: str) -> None:
    api.upload_file(
        path_or_fileobj=io.BytesIO(data),
        path_in_repo=path_in_repo,
        repo_id=repo_id,
        repo_type=_REPO_TYPE,
    )


def upload_path(api, repo_id: str, local_path: Path, path_in_repo: str) -> None:
    api.upload_file(
        path_or_fileobj=str(local_path),
        path_in_repo=path_in_repo,
        repo_id=repo_id,
        repo_type=_REPO_TYPE,
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/tts/test_hub.py -v`
Expected: 15 passed

- [ ] **Step 5: Commit**

```bash
git add meddies_tts/hub.py tests/tts/test_hub.py
git commit -m "feat: add hub client with preflight, resume diff and drift detection"
```

---

### Task 14: CLI

**Files:**
- Create: `cli.py`
- Test: `tests/tts/test_cli_tts.py`

**Interfaces:**
- Consumes: everything from Tasks 1–13.
- Produces: `main(argv: list[str] | None = None) -> int` with subcommands `build-manifest`, `plan`, `preflight`, `estimate`, `status`, `show-config`, `materialize-tree`. Stage 1 (`plan`) runs locally because the normalizer is pure Python (Task 3).

Global flags: `--config PATH` (default `config.yaml`), `--hf-repo ID` (overrides `hf.repo_id`).

- [ ] **Step 1: Write the failing test**

```python
# tests/tts/test_cli_tts.py
import json

import pytest

import cli
from meddies_tts.manifest import read_manifest
from meddies_tts.plan import read_plan

_CONFIG = """
hf:
  repo_id: "Meddies/SynthAudio"
run:
  convs_per_shard: 2
  configs: ["vietnamese"]
"""

_VISEC = """speaker_id,output_path,duration_seconds,clip_count,emotions,unique_source_duration_seconds
0,processed_audio_by_id/speaker_000.wav,12.9,8,neutral,100.0
1,processed_audio_by_id/speaker_001.wav,12.8,9,neutral,120.0
2,processed_audio_by_id/speaker_002.wav,12.5,7,neutral,140.0
"""


@pytest.fixture()
def workspace(tmp_path):
    (tmp_path / "config.yaml").write_text(_CONFIG, encoding="utf-8")
    tree = tmp_path / "output_full" / "vietnamese" / "suy_gan"
    for conv in ("conv_0001", "conv_0002", "conv_0003"):
        for turn in (1, 2):
            d = tree / conv / f"Turn{turn}"
            d.mkdir(parents=True)
            (d / "user.txt").write_text("Xin chào bác sĩ.", encoding="utf-8")
            (d / "assistant.txt").write_text("Chào bạn.", encoding="utf-8")
    (tree / "_disease_name.txt").write_text("Suy gan", encoding="utf-8")
    visec = tmp_path / "ViSEC" / "processed_audio_by_id"
    visec.mkdir(parents=True)
    (visec / "metadata.csv").write_text(_VISEC, encoding="utf-8")
    for sid in range(3):
        (visec / f"speaker_{sid:03d}.wav").write_bytes(b"RIFF")
    return tmp_path


def _run(workspace, *args):
    return cli.main([
        "--config", str(workspace / "config.yaml"), *args
    ])


def test_build_manifest_writes_parquet(workspace):
    out = workspace / "manifest.parquet"
    assert _run(workspace, "build-manifest",
                "--output-root", str(workspace / "output_full"),
                "--out", str(out)) == 0
    assert read_manifest(out).num_rows == 12


def _make_plan(workspace):
    manifest = workspace / "manifest.parquet"
    _run(workspace, "build-manifest", "--output-root", str(workspace / "output_full"),
         "--out", str(manifest))
    plan_out = workspace / "shard_plan.parquet"
    _run(workspace, "plan", "--manifest", str(manifest),
         "--visec", str(workspace / "ViSEC" / "processed_audio_by_id" / "metadata.csv"),
         "--out", str(plan_out), "--rejects", str(workspace / "rejects.jsonl"))
    return plan_out


def test_plan_writes_plan_and_rejects(workspace):
    plan_out = _make_plan(workspace)
    assert read_plan(plan_out).num_rows == 12
    assert (workspace / "rejects.jsonl").exists()


def test_plan_packs_conversations_into_shards(workspace):
    shards = set(read_plan(_make_plan(workspace)).column("shard_id").to_pylist())
    assert shards == {"vi-00000", "vi-00001"}


def test_plan_writes_a_hash_file(workspace):
    plan_out = _make_plan(workspace)
    assert plan_out.with_suffix(".hash").read_text(encoding="utf-8").strip()


def test_plan_normalizes_numbers_into_text_spoken(workspace):
    (workspace / "output_full" / "vietnamese" / "suy_gan" / "conv_0001" / "Turn1"
     / "user.txt").write_text("Sốt cao 38.5°C, gọi 115.", encoding="utf-8")
    rows = read_plan(_make_plan(workspace)).to_pylist()
    row = next(r for r in rows if r["conv_id"] == "conv_0001" and r["turn"] == 1
               and r["role"] == "user")
    assert row["text_raw"] == "Sốt cao 38.5°C, gọi 115."
    assert row["text_spoken"] == "Sốt cao ba mươi tám phẩy năm độ C, gọi một một năm."


def test_estimate_reports_cost_and_storage(workspace, capsys):
    plan_out = _make_plan(workspace)
    assert _run(workspace, "estimate", "--plan", str(plan_out)) == 0
    out = capsys.readouterr().out
    assert "GPU-hours" in out and "USD" in out and "GB" in out


def test_missing_repo_id_exits_nonzero(workspace, capsys):
    (workspace / "bad.yaml").write_text("hf: {}\n", encoding="utf-8")
    code = cli.main(["--config", str(workspace / "bad.yaml"), "estimate",
                     "--plan", str(workspace / "nope.parquet")])
    assert code == 2
    assert "hf.repo_id" in capsys.readouterr().err


def test_hf_repo_override_is_applied(workspace, capsys):
    _run(workspace, "build-manifest", "--output-root", str(workspace / "output_full"),
         "--out", str(workspace / "m.parquet"))
    cli.main(["--config", str(workspace / "config.yaml"), "--hf-repo", "someone/scratch",
              "show-config"])
    assert "someone/scratch" in capsys.readouterr().out


def test_materialize_tree_rebuilds_the_output_full_shape(workspace, tmp_path):
    from meddies_tts.audio import to_flac_bytes
    from meddies_tts.writer import build_row, write_shard
    import numpy as np

    row = {
        "config": "vietnamese", "disease_slug": "suy_gan", "disease_name": "Suy gan",
        "conv_id": "conv_0001", "turn": 1, "role": "user",
        "text_raw": "x", "text_spoken": "x", "speaker_id": 0,
        "speaker_emotions": "neutral", "speaker_unique_source_s": 100.0,
        "shard_id": "vi-00000",
        "audio_path": "vietnamese/suy_gan/conv_0001/Turn1/user.flac",
    }
    shard = workspace / "shard.parquet"
    write_shard([build_row(row, to_flac_bytes(np.zeros(1600, dtype=np.float32), 16000),
                           0.1, 1, 1, "v")], shard, "h", "{}")
    dest = tmp_path / "tree"
    assert _run(workspace, "materialize-tree", "--shard", str(shard),
                "--dest", str(dest)) == 0
    assert (dest / "vietnamese/suy_gan/conv_0001/Turn1/user.flac").exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/tts/test_cli_tts.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'cli'`

- [ ] **Step 3: Write the implementation**

```python
# cli.py
"""Local, GPU-free commands for the Meddies TTS pipeline."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pyarrow.parquet as pq

from meddies_tts.config import ConfigError, load_config
from meddies_tts.manifest import build_manifest, read_manifest, write_manifest
from meddies_tts.plan import (
    build_plan,
    compute_plan_hash,
    read_plan,
    shard_totals,
    write_plan,
)
from meddies_tts.qc import DEFAULT_CHARS_PER_SEC
from meddies_tts.speakers import load_pool

# Modal A100-40GB, USD/sec, from modal.com/pricing
_A100_USD_PER_SEC = 0.000583
# Aggregate realtime multiple at concurrency 48 on one GPU (spec §2)
_AGGREGATE_SPEEDUP = 70.0
# 16 kHz 16-bit FLAC, bytes per second of audio
_FLAC_BYTES_PER_SEC = 19_000


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cli.py", description=__doc__)
    parser.add_argument("--config", default="config.yaml", help="path to config.yaml")
    parser.add_argument("--hf-repo", default=None, help="override hf.repo_id")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("build-manifest", help="flatten output_full/ into manifest.parquet")
    p.add_argument("--output-root", required=True)
    p.add_argument("--out", required=True)

    p = sub.add_parser("plan", help="normalize, reject, assign speakers, pack shards")
    p.add_argument("--manifest", required=True)
    p.add_argument("--visec", required=True, help="path to ViSEC metadata.csv")
    p.add_argument("--out", required=True)
    p.add_argument("--rejects", required=True)

    p = sub.add_parser("preflight", help="verify HF token, repo and write access")

    p = sub.add_parser("estimate", help="project GPU-hours, cost and storage")
    p.add_argument("--plan", required=True)
    p.add_argument("--chars-per-sec", type=float, default=DEFAULT_CHARS_PER_SEC)

    p = sub.add_parser("status", help="report done/remaining shards against the Hub")
    p.add_argument("--plan", required=True)

    p = sub.add_parser("show-config", help="print the resolved configuration")

    p = sub.add_parser("materialize-tree", help="rebuild the output_full tree from a shard")
    p.add_argument("--shard", required=True)
    p.add_argument("--dest", required=True)

    return parser


def _cmd_build_manifest(args, cfg) -> int:
    table = build_manifest(Path(args.output_root), cfg.run.configs)
    write_manifest(table, Path(args.out))
    print(f"manifest: {table.num_rows:,} utterances -> {args.out}")
    return 0


def _cmd_plan(args, cfg) -> int:
    manifest = read_manifest(Path(args.manifest))
    pool = load_pool(Path(args.visec))
    plan, rejects = build_plan(manifest, cfg, pool)

    write_plan(plan, Path(args.out))
    with Path(args.rejects).open("w", encoding="utf-8") as handle:
        for record in rejects:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    plan_hash = compute_plan_hash(plan, cfg)
    Path(args.out).with_suffix(".hash").write_text(plan_hash, encoding="utf-8")
    print(
        f"plan: {plan.num_rows:,} utterances, {sum(shard_totals(plan).values())} shards, "
        f"{len(rejects):,} rejected -> {args.out} (hash {plan_hash})"
    )
    return 0


def _cmd_preflight(args, cfg) -> int:
    from huggingface_hub import HfApi

    from meddies_tts.hub import preflight

    preflight(HfApi(), cfg.hf.repo_id, cfg.hf.private)
    print(f"preflight OK: {cfg.hf.repo_id} is writable")
    return 0


def _cmd_estimate(args, cfg) -> int:
    plan = read_plan(Path(args.plan))
    chars = sum(len(text) for text in plan.column("text_spoken").to_pylist())
    audio_sec = chars / args.chars_per_sec
    gpu_sec = audio_sec / _AGGREGATE_SPEEDUP
    print(f"utterances : {plan.num_rows:,}")
    print(f"shards     : {sum(shard_totals(plan).values()):,}")
    print(f"audio      : {audio_sec / 3600:,.1f} h  (at {args.chars_per_sec} chars/sec)")
    print(f"GPU-hours  : {gpu_sec / 3600:,.1f}")
    print(f"cost       : {gpu_sec * _A100_USD_PER_SEC:,.2f} USD  (A100-40GB)")
    print(f"storage    : {audio_sec * _FLAC_BYTES_PER_SEC / 1e9:,.1f} GB  (16 kHz FLAC)")
    return 0


def _cmd_status(args, cfg) -> int:
    from huggingface_hub import HfApi

    from meddies_tts.hub import (
        check_plan_drift,
        list_repo_paths,
        remaining_targets,
        shard_targets,
    )

    plan = read_plan(Path(args.plan))
    local_hash = Path(args.plan).with_suffix(".hash").read_text(encoding="utf-8").strip()
    api = HfApi()
    for config in cfg.run.configs:
        check_plan_drift(api, cfg.hf.repo_id, config, local_hash)
    existing = list_repo_paths(api, cfg.hf.repo_id)
    total = len(shard_targets(plan))
    remaining = remaining_targets(plan, existing)
    print(f"plan hash : {local_hash}")
    print(f"shards    : {total}")
    print(f"done      : {total - len(remaining)}")
    print(f"remaining : {len(remaining)}")
    return 0


def _cmd_show_config(args, cfg) -> int:
    print(json.dumps({"repo_id": cfg.hf.repo_id, "configs": list(cfg.run.configs)}, indent=2))
    return 0


def _cmd_materialize_tree(args, cfg) -> int:
    table = pq.read_table(Path(args.shard))
    dest = Path(args.dest)
    written = 0
    for record in table.column("audio").to_pylist():
        target = dest / record["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(record["bytes"])
        written += 1
    print(f"materialized {written} files under {dest}")
    return 0


_COMMANDS = {
    "build-manifest": _cmd_build_manifest,
    "plan": _cmd_plan,
    "preflight": _cmd_preflight,
    "estimate": _cmd_estimate,
    "status": _cmd_status,
    "show-config": _cmd_show_config,
    "materialize-tree": _cmd_materialize_tree,
}


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        cfg = load_config(Path(args.config), {"hf.repo_id": args.hf_repo})
    except ConfigError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    return _COMMANDS[args.command](args, cfg)


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/tts/test_cli_tts.py -v`
Expected: 9 passed

- [ ] **Step 5: Run the whole GPU-free suite**

Run: `pytest -v`
Expected: all pass, including the pre-existing `meddies/` tests.

- [ ] **Step 6: Commit**

```bash
git add cli.py tests/tts/test_cli_tts.py
git commit -m "feat: add local CLI for manifest, planning, estimation and status"
```

---

## Phase 2 — GPU and Modal

Everything above runs and is fully tested on the dev Mac. Everything below requires
Linux + NVIDIA and cannot be unit-tested locally, so each task's verification is an
explicit manual run against Modal.

---

### Task 15: Real VoxCPM engine adapter

**Files:**
- Modify: `meddies_tts/engine.py` (append; the `TTSEngine` Protocol from Task 11 stays at the top and gains no imports)
- Create: `requirements-gpu.txt`

**Interfaces:**
- Consumes: `EngineConfig` (Task 1), `TTSEngine` Protocol (Task 11).
- Produces: `class VoxCPMEngine` satisfying `TTSEngine`, with `async classmethod create(model_path: str, cfg: EngineConfig, devices: list[int] | None = None) -> VoxCPMEngine` and `async close() -> None`. Task 16 instantiates it in `@modal.enter()`.

**Constraint:** `nano-vllm-voxcpm` must be imported *inside* `create`, never at module top level, so `meddies_tts.engine` still imports on the Mac for Task 11's Protocol and Task 12's type hints.

- [ ] **Step 1: Create the GPU requirements file**

```
# requirements-gpu.txt — installed only in the Modal image, never on the Mac
torch>=2.5
nano-vllm-voxcpm>=0.1
librosa>=0.10
```

- [ ] **Step 2: Append the implementation to `meddies_tts/engine.py`**

```python
# appended to meddies_tts/engine.py


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
        from nanovllm_voxcpm import VoxCPM  # imported lazily: requires CUDA + flash-attn

        server = VoxCPM.from_pretrained(
            model=model_path,
            inference_timesteps=cfg.inference_timesteps,
            max_num_batched_tokens=cfg.max_num_batched_tokens,
            max_num_seqs=cfg.max_num_seqs,
            devices=devices or [0],
        )
        await server.wait_for_ready()
        info = await server.get_model_info()
        version = f"nanovllm-voxcpm/{_package_version()}"
        return cls(server, int(info["sample_rate"]), version, cfg)

    async def encode_reference(self, wav_bytes: bytes) -> bytes:
        # encode_latents resamples and mono-mixes internally, so the 16 kHz
        # ViSEC WAVs need no preprocessing.
        return await self._server.encode_latents(wav_bytes, "wav")

    async def synthesize(self, text: str, ref_latents: bytes, seed: int) -> np.ndarray:
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
        await self._server.stop()


def _package_version() -> str:
    try:
        import importlib.metadata

        return importlib.metadata.version("nano-vllm-voxcpm")
    except Exception:  # noqa: BLE001
        return "unknown"
```

- [ ] **Step 3: Verify the module still imports on the Mac**

Run: `python3 -c "import meddies_tts.engine as e; print(e.TTSEngine, e.VoxCPMEngine)"`
Expected: prints both names with no CUDA error — proving the lazy import works.

- [ ] **Step 4: Run the full local suite to confirm nothing regressed**

Run: `pytest -v`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add meddies_tts/engine.py requirements-gpu.txt
git commit -m "feat: add VoxCPM engine adapter behind a lazy CUDA import"
```

---

### Task 16: Modal application

**Files:**
- Create: `app.py`

**Interfaces:**
- Consumes: `load_config` (1), `read_plan`/`compute_plan_hash`/`shard_totals` (7), `load_pool` (6), `run_shard` (12), `write_shard` (10), `hub` helpers (13), `VoxCPMEngine` (15).
- Produces: Modal app `meddies-tts` with `fetch_weights()`, `class Synthesizer` (`run_shard`), and `@app.local_entrypoint() main(shards, config_path, plan_path, limit)`.

**Two-level parallelism, from the spec:** `asyncio.Semaphore(cfg.engine.concurrency)` inside `run_shard` (Task 12) feeds nano-vllm's batcher; `max_containers` scales across GPUs. Do not add `@modal.concurrent` — the work unit is a whole shard, so Modal-level input concurrency would only multiply GPU memory pressure.

- [ ] **Step 1: Write `app.py`**

```python
"""Modal application: one container per shard, generate -> parquet -> HF -> delete."""
from __future__ import annotations

import json
import os
from pathlib import Path

import modal

APP_NAME = "meddies-tts"
MODEL_REPO = "openbmb/VoxCPM2"
MODEL_DIR = "/weights/VoxCPM2"
PLAN_DIR = "/plan"
REFS_DIR = "/refs"

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("git", "ffmpeg")
    .pip_install_from_requirements("requirements.txt")
    .pip_install_from_requirements("requirements-gpu.txt")
    .pip_install("flash-attn", extra_options="--no-build-isolation")
    .env({"HF_HUB_ENABLE_HF_TRANSFER": "1"})
    .add_local_python_source("meddies_tts")
)

app = modal.App(APP_NAME)
weights_vol = modal.Volume.from_name("voxcpm2-weights", create_if_missing=True)
plan_vol = modal.Volume.from_name("meddies-tts-plan", create_if_missing=True)
refs_vol = modal.Volume.from_name("visec-refs", create_if_missing=True)
hf_secret = modal.Secret.from_name("huggingface")


@app.function(image=image, volumes={"/weights": weights_vol}, timeout=3600,
              secrets=[hf_secret])
def fetch_weights() -> str:
    """Download VoxCPM2 once onto the weights Volume, and assert safetensors."""
    from huggingface_hub import snapshot_download

    path = snapshot_download(repo_id=MODEL_REPO, local_dir=MODEL_DIR)
    files = set(os.listdir(path))
    if "config.json" not in files:
        raise RuntimeError(f"config.json missing from {path}")
    if not any(name.endswith(".safetensors") for name in files):
        raise RuntimeError(
            "nano-vllm-voxcpm raises 'ValueError: Missing parameters' on .pt "
            f"checkpoints; {path} has no .safetensors weights. Convert first."
        )
    weights_vol.commit()
    return path


@app.cls(
    image=image,
    gpu=os.environ.get("MEDDIES_GPU", "A100-40GB"),
    volumes={"/weights": weights_vol, PLAN_DIR: plan_vol, REFS_DIR: refs_vol},
    secrets=[hf_secret],
    timeout=7200,
    max_containers=20,
)
class Synthesizer:
    @modal.enter()
    async def load(self) -> None:
        from huggingface_hub import HfApi

        from meddies_tts.config import load_config
        from meddies_tts.engine import VoxCPMEngine
        from meddies_tts.plan import read_plan
        from meddies_tts.speakers import load_pool

        self.cfg = load_config(Path(f"{PLAN_DIR}/config.yaml"))
        self.plan = read_plan(Path(f"{PLAN_DIR}/shard_plan.parquet"))
        self.plan_hash = Path(f"{PLAN_DIR}/shard_plan.hash").read_text().strip()
        self.api = HfApi()

        # Load the engine ONCE per container — this is what makes the shard-as-work-unit
        # design pay for itself across ~1,500 utterances.
        self.engine = await VoxCPMEngine.create(MODEL_DIR, self.cfg.engine)

        # Encode all 147 references ONCE, not per utterance.
        pool = load_pool(Path(f"{REFS_DIR}/processed_audio_by_id/metadata.csv"))
        self.refs = {
            speaker.speaker_id: await self.engine.encode_reference(
                Path(speaker.wav_path).read_bytes()
            )
            for speaker in pool
        }
        print(f"ready: engine={self.engine.version} refs={len(self.refs)} "
              f"sample_rate={self.engine.sample_rate}")

    @modal.method()
    async def run_shard(self, shard_id: str, repo_path: str) -> dict:
        import time

        from meddies_tts.hub import upload_path
        from meddies_tts.runner import run_shard as run
        from meddies_tts.writer import write_shard

        started = time.time()
        rows = [r for r in self.plan.to_pylist() if r["shard_id"] == shard_id]
        built, result = await run(shard_id, rows, self.engine, self.refs, self.cfg)
        if not built:
            return {"shard_id": shard_id, "status": "empty", "failed": result.n_failed}

        local = Path(f"/tmp/{shard_id}.parquet")
        write_shard(built, local, self.plan_hash, json.dumps({"gpu": self.cfg.run.gpu}))
        # Atomic by construction: nothing is uploaded until the whole shard is written.
        upload_path(self.api, self.cfg.hf.repo_id, local, repo_path)
        local.unlink()

        elapsed = time.time() - started
        return {
            "shard_id": shard_id,
            "status": "ok",
            "utterances": len(built),
            "failed": result.n_failed,
            "audio_seconds": result.audio_seconds,
            "wall_seconds": elapsed,
            "rtf": elapsed / result.audio_seconds if result.audio_seconds else None,
            "failures": result.failures[:20],
        }


@app.local_entrypoint()
def main(shards: str = "remaining", config_path: str = "config.yaml",
         plan_path: str = "shard_plan.parquet", limit: int = 0) -> None:
    from huggingface_hub import HfApi

    from meddies_tts.config import load_config
    from meddies_tts.hub import (
        check_plan_drift,
        list_repo_paths,
        plan_hash_path,
        preflight,
        remaining_targets,
        shard_targets,
        upload_bytes,
    )
    from meddies_tts.plan import read_plan

    cfg = load_config(Path(config_path))
    plan = read_plan(Path(plan_path))
    plan_hash = Path(plan_path).with_suffix(".hash").read_text(encoding="utf-8").strip()

    api = HfApi()
    preflight(api, cfg.hf.repo_id, cfg.hf.private)          # fails in seconds, not dollars
    for config in cfg.run.configs:
        check_plan_drift(api, cfg.hf.repo_id, config, plan_hash)

    existing = list_repo_paths(api, cfg.hf.repo_id)
    targets = (
        remaining_targets(plan, existing)
        if shards == "remaining"
        else [t for t in shard_targets(plan) if t[0] in set(shards.split(","))]
    )
    if limit:
        targets = targets[:limit]
    if not targets:
        print("nothing to do — every planned shard is already published")
        return

    for config in cfg.run.configs:
        upload_bytes(api, cfg.hf.repo_id, plan_hash.encode(), plan_hash_path(config))

    print(f"dispatching {len(targets)} shard(s) to {cfg.run.gpu}")
    synth = Synthesizer()
    total_audio = 0.0
    for outcome in synth.run_shard.starmap(targets):
        total_audio += outcome.get("audio_seconds") or 0.0
        print(json.dumps(outcome, ensure_ascii=False))
    print(f"done: {total_audio / 3600:.2f} h of audio generated")
```

- [ ] **Step 2: Create the Modal Secret and upload inputs**

```bash
pip install modal && modal setup
modal secret create huggingface HF_TOKEN=<your write-scoped token>

# Stage 0 + 1, both local and pure Python
python cli.py build-manifest --output-root output_full --out manifest.parquet
python cli.py plan --manifest manifest.parquet \
  --visec ~/Desktop/Project/ASR-syntheticdata/data/ViSEC-processed/processed_audio_by_id/metadata.csv \
  --out shard_plan.parquet --rejects rejects.jsonl
python cli.py estimate --plan shard_plan.parquet
head -3 rejects.jsonl        # sanity-check what the reject rule threw away

# upload the plan, config and reference audio
modal volume put meddies-tts-plan shard_plan.parquet /shard_plan.parquet
modal volume put meddies-tts-plan shard_plan.hash    /shard_plan.hash
modal volume put meddies-tts-plan config.yaml        /config.yaml
modal volume put visec-refs \
  ~/Desktop/Project/ASR-syntheticdata/data/ViSEC-processed/processed_audio_by_id \
  /processed_audio_by_id
```

Expected: ~709k utterances, ~473 shards and ~2.3k rejects.

- [ ] **Step 3: Fetch the model weights**

Run: `modal run app.py::fetch_weights`
Expected: prints the model directory; fails loudly if the checkpoint lacks `.safetensors`.

- [ ] **Step 4: Verify preflight fails fast on a bad repo**

Run: `python cli.py --hf-repo Meddies/DoesNotExistAndCannotBeCreated preflight`
Expected: non-zero exit with a `HubError` naming the repo — proving no GPU would have been requested.

- [ ] **Step 5: Smoke-test one shard end to end**

Run: `modal run app.py --shards vi-00000 --limit 1`
Expected: JSON with `"status": "ok"`, a non-null `rtf`, and one new file at
`data/vietnamese/train-00000-of-*.parquet` in `Meddies/SynthAudio`.

- [ ] **Step 6: Verify the published shard loads**

```bash
python3 -c "
from datasets import load_dataset
ds = load_dataset('Meddies/SynthAudio', 'vietnamese', split='train', streaming=True)
row = next(iter(ds))
print(row['text_spoken'][:80])
print(row['audio']['sampling_rate'], len(row['audio']['array']))
"
```
Expected: prints Vietnamese text, `16000`, and a non-zero sample count.

- [ ] **Step 7: Verify resumption skips the finished shard**

Run: `modal run app.py --shards vi-00000`
Expected: `nothing to do — every planned shard is already published`.

- [ ] **Step 8: Commit**

```bash
git add app.py
git commit -m "feat: add Modal app running one shard per container with HF upload"
```

---

### Task 17: Pilot run and calibration gate

**Files:**
- Create: `scripts/pilot_report.py`
- Create: `docs/superpowers/reports/2026-07-28-pilot_report.md` (generated)

**Interfaces:**
- Consumes: the published pilot shards and the JSON emitted by `Synthesizer.run_shard`.
- Produces: `measure_chars_per_sec(shard_paths: list[str]) -> float` and a written report. Its output *replaces* `DEFAULT_CHARS_PER_SEC` in every subsequent estimate.

**This is a hard gate.** Every cost figure in the spec rests on an unverified 14 chars/sec assumption. Do not launch the full run before this report exists and has been reviewed.

- [ ] **Step 1: Write the measurement script**

```python
# scripts/pilot_report.py
"""Measure the real chars/sec and RTF from published pilot shards."""
from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

import pyarrow.parquet as pq


def measure_chars_per_sec(shard_paths: list[str]) -> float:
    chars = 0
    seconds = 0.0
    for path in shard_paths:
        table = pq.read_table(path, columns=["text_spoken", "duration_s"])
        chars += sum(len(t) for t in table.column("text_spoken").to_pylist())
        seconds += float(sum(table.column("duration_s").to_pylist()))
    if seconds <= 0:
        raise ValueError("pilot shards contain no audio")
    return chars / seconds


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--shards", nargs="+", required=True)
    parser.add_argument("--outcomes", required=True, help="JSONL of run_shard outputs")
    parser.add_argument("--total-utterances", type=int, required=True)
    args = parser.parse_args()

    cps = measure_chars_per_sec(args.shards)
    outcomes = [json.loads(line) for line in Path(args.outcomes).read_text().splitlines()]
    rtfs = [o["rtf"] for o in outcomes if o.get("rtf")]
    audio = sum(o.get("audio_seconds") or 0.0 for o in outcomes)
    utts = sum(o.get("utterances") or 0 for o in outcomes)
    failed = sum(o.get("failed") or 0 for o in outcomes)

    scale = args.total_utterances / utts
    projected_audio_h = audio * scale / 3600
    aggregate_rtf = statistics.median(rtfs)
    projected_gpu_h = projected_audio_h * aggregate_rtf
    print(f"measured chars/sec     : {cps:.2f}   (spec assumed 14.0)")
    print(f"median shard RTF       : {aggregate_rtf:.4f}")
    print(f"failure rate           : {failed / max(utts + failed, 1):.3%}")
    print(f"projected audio        : {projected_audio_h:,.0f} h")
    print(f"projected GPU-hours    : {projected_gpu_h:,.0f}")
    print(f"projected cost (A100)  : {projected_gpu_h * 3600 * 0.000583:,.0f} USD")
    print(f"projected storage      : {projected_audio_h * 3600 * 19_000 / 1e9:,.0f} GB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Run the pilot — 3 shards**

```bash
modal run app.py --shards vi-00000,vi-00001,vi-00002 2>&1 | tee pilot_outcomes.jsonl
```
Expected: three `"status": "ok"` records. Cost should be roughly $2.

- [ ] **Step 3: Sweep concurrency to find the real optimum**

Re-run one shard at `engine.concurrency` ∈ {1, 8, 16, 32, 48, 64} (editing `config.yaml`
and re-uploading it to the plan Volume each time), recording the reported `rtf`:

```bash
for c in 1 8 16 32 48 64; do
  sed -i '' "s/  concurrency: .*/  concurrency: $c/" config.yaml
  sed -i '' "s/  max_num_seqs: .*/  max_num_seqs: $((c > 64 ? c : 64))/" config.yaml
  modal volume put --force meddies-tts-plan config.yaml /config.yaml
  # note: engine.* changes do not affect plan_hash, so no re-plan is needed
  echo "concurrency=$c"; modal run app.py --shards vi-00003 --limit 1
  # delete the shard from the repo between runs so it re-generates
done
```
Expected: aggregate throughput rises sharply from concurrency 1 to ~48 and then flattens.
**Set `engine.concurrency` to the knee of that curve.** This is the measurement that
justifies the whole architecture.

- [ ] **Step 4: Generate the report**

```bash
python scripts/pilot_report.py \
  --shards $(ls pilot_shards/*.parquet) \
  --outcomes pilot_outcomes.jsonl \
  --total-utterances $(python -c "
from meddies_tts.plan import read_plan; print(read_plan('shard_plan.parquet').num_rows)")
```

Write the output, plus the concurrency sweep table and notes from **two listening
passes**, into `docs/superpowers/reports/2026-07-28-pilot_report.md`:

1. **Speaker quality** — the same sentence across a clean-neutral speaker, speaker 79
   (whose reference is 1.3 s of looped audio), a pure-`angry` speaker, and a 4-emotion
   splice. Decides whether the full 147-speaker pool stays or gets filtered.
2. **Normalizer correctness** — 20 utterances chosen for dense numbers and units
   (`38.5°C`, `4-5/10`, `115`, dosages). Confirm each is spoken correctly. This
   replaces the automated ASR round-trip and is the *only* check on verbalized numbers,
   so do not skip it:

```bash
python3 -c "
import pyarrow.parquet as pq, re
t = pq.read_table('pilot_shards/train-00000-of-00473.parquet',
                  columns=['text_raw','text_spoken','audio'])
rows = [r for r in t.to_pylist() if len(re.findall(r'[0-9]', r['text_raw'])) >= 6][:20]
for i, r in enumerate(rows):
    open(f'/tmp/num_{i}.flac','wb').write(r['audio']['bytes'])
    print(i, r['text_spoken'][:120])
"
```

- [ ] **Step 5: Re-estimate with the measured rate**

Run: `python cli.py estimate --plan shard_plan.parquet --chars-per-sec <measured>`
Expected: corrected GPU-hours, USD and GB. **Compare against the spec's $250–400 and
480 GB. If it differs by more than ~2×, stop and revisit scope before proceeding.**

- [ ] **Step 6: Commit the report**

```bash
git add scripts/pilot_report.py docs/superpowers/reports/2026-07-28-pilot_report.md
git commit -m "docs: add pilot calibration report and measurement script"
```

- [ ] **Step 7: Launch the full run (only after the report is reviewed)**

```bash
python cli.py status --plan shard_plan.parquet
modal run app.py --shards remaining
```

Re-run `modal run app.py --shards remaining` as often as needed — credits running out,
a closed laptop, or a months-long gap all resume correctly, because completion state
lives on the Hub and shards are atomic.

---

## Self-Review

**Spec coverage.** Every spec section maps to a task: §3.1 16 kHz FLAC → Task 8; §3.2
sharded Parquet → Task 10; §3.3 manifest transport → Tasks 2 and 14; §3.4 speaker
assignment → Task 6; §3.5 full 147-speaker pool with quality columns → Tasks 6, 7, 10;
§3.6 normalization, rejection and chunking → Tasks 3, 4, 5; §3.7 runtime config and
preflight → Tasks 1, 13, 14; §3.6 Vietnamese number rules → Task 3 (`vietnamese_numbers.py`); §3.8 multi-config → Tasks 3, 7 (`CONFIG_PREFIX`), 10; §4
architecture → Tasks 12, 16; §5 rejection rules → Task 4; §6 schema and shard sizing →
Tasks 7, 10; §7 generation core → Task 12; §8 error handling and §8.1 resumption →
Tasks 12, 13, 16; §9 QC and the pilot gate → Tasks 9, 17; §10 cost controls → Task 14
(`estimate`, `status`); §11 testing → Tasks 11 and every task's test file; Appendix A
layout → Tasks 7 (`shard_repo_path`), 13 (`plan_path`), 16.

**Known gaps, deliberately deferred and recorded here rather than silently dropped:**

1. **No automated ASR round-trip, by design.** Removed from the spec (§9): scoring
   TTS output with Whisper is circular, the deterministic pipeline gives it no drift to
   detect, and the pilot's listening packs are a better signal. Task 17 covers the
   residual normalizer risk with a number-heavy listening pack instead.
2. **The dataset card body (Appendix A.2) has no task.** Stage 3 is one hand-written
   Markdown file plus a `hub.upload_bytes` call; it is not worth a TDD cycle, but it *is*
   required by HF for large datasets and must be written before the repo is shared.
3. **`--budget-usd` is present in config (Task 1) but not enforced.** `estimate` and
   `status` give you the numbers to stop manually; automatic mid-run cutoff would need
   Modal cost telemetry the local entrypoint does not have.
4. **`cli.py sample --config english -n 20`** (spec §3.8's audition path) is not a task —
   it is `modal run app.py --shards <id> --limit 1` against an English plan, which Task 16
   already supports. A dedicated command is worth adding only if auditioning becomes
   frequent.

**Type consistency.** Verified: `derive_seed` is defined once (Task 6) and imported by
Tasks 7 and 12; `TTSEngine` (Task 11) is the only engine type Task 12 depends on, and
`VoxCPMEngine` (Task 15) and `FakeEngine` (Task 11) both satisfy it — `sample_rate`,
`version`, `encode_reference`, `synthesize` match across all three; `shard_repo_path` and
`shard_totals` (Task 7) are used with identical signatures in Task 13; `build_row`'s
argument order (Task 10) matches its call site in Task 12; `write_shard(rows, path,
plan_hash, config_json)` matches Task 16's call.

**Placeholder scan.** No TBD/TODO markers; every code step contains runnable code; every
test step contains real assertions.
