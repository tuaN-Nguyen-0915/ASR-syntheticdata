# Meddies Dataset Pipeline (Feature 1) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Download a 100-row sample each of the `vietnamese` and `english` configs of `Meddies/meddies-consultant` and restructure every conversation on disk as per-turn `assistant.txt`/`user.txt` files, organized by disease.

**Architecture:** A small `meddies` package with one module per concern (slugify, think-stripping, turn-pairing, filesystem writing, row orchestration), wired together by a thin `download_meddies.py` CLI. Each module is unit-tested in isolation with plain dict/string fixtures; the CLI is tested by monkeypatching `datasets.load_dataset` with an in-memory `Dataset.from_list(...)` so tests never hit the network. A final manual task runs the real script against the live dataset to verify actual output.

**Tech Stack:** Python 3.10+, `datasets` (Hugging Face) for loading, `pytest` for tests, standard library only otherwise (`unicodedata`, `re`, `pathlib`, `argparse`).

## Global Constraints

- Sample scope: 100 rows per config (`vietnamese`, `english`) via `dataset.select(range(limit))`, default `limit=100`.
- Load with `load_dataset("Meddies/meddies-consultant", config, streaming=False)` — non-streaming, per the spec's resumability rationale.
- Output root defaults to `output/`; layout is `output/<config>/<disease_slug>/conv_NNNN/TurnM/{assistant.txt,user.txt}`.
- All written files are UTF-8 plain text, content only (no headers/metadata inside message files).
- `<disease_slug>`: ASCII, diacritics stripped, lowercased, non-alphanumeric collapsed to `_`; empty/missing `target_disease` → `unknown_disease`.
- Each disease folder gets a `_disease_name.txt` holding the original, un-slugified `target_disease` string (written once, not overwritten).
- `conv_NNNN` (zero-padded 4 digits) restarts at 1 **within each `<disease_slug>` folder** — not global, not shared across configs.
- `TurnM` increments per `(assistant, user)` pair starting at 1.
- Think-block stripping: strip `<think>...</think>` only if both tags present; if `<think>` present but unclosed, keep the message untouched and log a warning (row is still written).
- Role validation: messages must alternate starting with `assistant` (even 0-based index = assistant, odd = user). Any row violating this is skipped entirely and logged to `skipped_rows.log`.
- Odd-length conversations: the trailing unpaired `assistant` message's `TurnM` folder gets `assistant.txt` only, no `user.txt`.
- `RandomQA` / `RandomQuestion` configs and `patient_persona` are out of scope for this feature.
- CLI flags: `--configs` (default `vietnamese english`), `--limit` (default `100`), `--output` (default `output/`).

---

### Task 1: Project scaffolding

**Files:**
- Create: `requirements.txt`
- Create: `meddies/__init__.py`
- Create: `.gitignore`
- Test: `tests/test_smoke.py`

**Interfaces:**
- Produces: the `meddies` package (importable, empty) that all later tasks add modules to.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_smoke.py
import meddies


def test_meddies_package_imports():
    assert meddies is not None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_smoke.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'meddies'`

- [ ] **Step 3: Create the package and support files**

```python
# meddies/__init__.py
```//empty file

```
# requirements.txt
datasets
pytest
```

```
# .gitignore
output/
__pycache__/
*.pyc
.pytest_cache/
```

- [ ] **Step 4: Install dependencies and run test to verify it passes**

Run: `pip install -r requirements.txt && pytest tests/test_smoke.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add requirements.txt meddies/__init__.py .gitignore tests/test_smoke.py
git commit -m "chore: scaffold meddies package and test setup"
```

---

### Task 2: Disease name slugification

**Files:**
- Create: `meddies/slugify.py`
- Test: `tests/test_slugify.py`

**Interfaces:**
- Produces: `slugify_disease(name: str | None) -> str` — used by Task 6 (pipeline).

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_slugify.py
from meddies.slugify import slugify_disease


def test_strips_vietnamese_diacritics_and_spaces():
    assert slugify_disease("Bong gân cổ chân") == "bong_gan_co_chan"


def test_lowercases_and_replaces_punctuation():
    assert slugify_disease("COVID-19") == "covid_19"


def test_none_returns_unknown_disease():
    assert slugify_disease(None) == "unknown_disease"


def test_empty_string_returns_unknown_disease():
    assert slugify_disease("") == "unknown_disease"


def test_whitespace_only_returns_unknown_disease():
    assert slugify_disease("   ") == "unknown_disease"


def test_symbols_only_returns_unknown_disease():
    assert slugify_disease("!!!") == "unknown_disease"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_slugify.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'meddies.slugify'`

- [ ] **Step 3: Implement `slugify_disease`**

```python
# meddies/slugify.py
import re
import unicodedata


def slugify_disease(name: str | None) -> str:
    if not name or not name.strip():
        return "unknown_disease"
    normalized = unicodedata.normalize("NFKD", name)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
    lowered = ascii_only.lower()
    slug = re.sub(r"[^a-z0-9]+", "_", lowered).strip("_")
    return slug if slug else "unknown_disease"
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_slugify.py -v`
Expected: PASS (6 passed)

- [ ] **Step 5: Commit**

```bash
git add meddies/slugify.py tests/test_slugify.py
git commit -m "feat: add disease name slugification"
```

---

### Task 3: Think-block stripping

**Files:**
- Create: `meddies/think_strip.py`
- Test: `tests/test_think_strip.py`

**Interfaces:**
- Produces: `strip_think_block(content: str) -> tuple[str, str | None]` — returns `(text_to_write, warning)`; `warning` is `None` normally or `"unclosed think tag"` if `<think>` has no matching `</think>`. Used by Task 5 (writer).

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_think_strip.py
from meddies.think_strip import strip_think_block


def test_strips_closed_think_block():
    content = "<think> internal reasoning here </think> Hello, how can I help?"
    cleaned, warning = strip_think_block(content)
    assert cleaned == "Hello, how can I help?"
    assert warning is None


def test_passes_through_content_without_think_tag():
    content = "Hello, how can I help?"
    cleaned, warning = strip_think_block(content)
    assert cleaned == "Hello, how can I help?"
    assert warning is None


def test_unclosed_think_tag_returns_original_with_warning():
    content = "<think> reasoning that never closes... still going"
    cleaned, warning = strip_think_block(content)
    assert cleaned == content
    assert warning == "unclosed think tag"


def test_strips_only_first_think_block_and_trims_whitespace():
    content = "<think>plan</think>   Reply text here.  "
    cleaned, warning = strip_think_block(content)
    assert cleaned == "Reply text here."
    assert warning is None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_think_strip.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'meddies.think_strip'`

- [ ] **Step 3: Implement `strip_think_block`**

```python
# meddies/think_strip.py
import re

_THINK_BLOCK_RE = re.compile(r"<think>.*?</think>", re.DOTALL)
_OPEN_TAG = "<think>"
_CLOSE_TAG = "</think>"


def strip_think_block(content: str) -> tuple[str, str | None]:
    if _OPEN_TAG not in content:
        return content.strip(), None
    if _CLOSE_TAG not in content:
        return content, "unclosed think tag"
    cleaned = _THINK_BLOCK_RE.sub("", content, count=1).strip()
    return cleaned, None
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_think_strip.py -v`
Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add meddies/think_strip.py tests/test_think_strip.py
git commit -m "feat: add think-block stripping for assistant messages"
```

---

### Task 4: Turn pairing and role validation

**Files:**
- Create: `meddies/pairing.py`
- Test: `tests/test_pairing.py`

**Interfaces:**
- Produces: `pair_turns(messages: list[dict]) -> list[tuple[dict, dict | None]]`, raising `ValueError` on role-alternation violations. Used by Task 6 (pipeline).
- Consumes: message dicts shaped `{"role": str, "content": str}`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_pairing.py
import pytest

from meddies.pairing import pair_turns


def _msg(role, content):
    return {"role": role, "content": content}


def test_pairs_even_length_alternating_conversation():
    messages = [
        _msg("assistant", "a1"), _msg("user", "u1"),
        _msg("assistant", "a2"), _msg("user", "u2"),
    ]
    pairs = pair_turns(messages)
    assert pairs == [
        (messages[0], messages[1]),
        (messages[2], messages[3]),
    ]


def test_odd_length_conversation_has_trailing_unpaired_assistant():
    messages = [
        _msg("assistant", "a1"), _msg("user", "u1"),
        _msg("assistant", "a2"),
    ]
    pairs = pair_turns(messages)
    assert pairs == [
        (messages[0], messages[1]),
        (messages[2], None),
    ]


def test_empty_messages_returns_empty_list():
    assert pair_turns([]) == []


def test_starting_with_user_raises_value_error():
    messages = [_msg("user", "u1"), _msg("assistant", "a1")]
    with pytest.raises(ValueError, match="index 0"):
        pair_turns(messages)


def test_two_assistants_in_a_row_raises_value_error():
    messages = [
        _msg("assistant", "a1"), _msg("assistant", "a2"), _msg("user", "u1"),
    ]
    with pytest.raises(ValueError, match="index 1"):
        pair_turns(messages)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_pairing.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'meddies.pairing'`

- [ ] **Step 3: Implement `pair_turns`**

```python
# meddies/pairing.py
def pair_turns(messages: list[dict]) -> list[tuple[dict, dict | None]]:
    for i, msg in enumerate(messages):
        expected_role = "assistant" if i % 2 == 0 else "user"
        if msg.get("role") != expected_role:
            raise ValueError(
                f"role mismatch at index {i}: expected '{expected_role}', "
                f"got '{msg.get('role')}'"
            )

    pairs: list[tuple[dict, dict | None]] = []
    i = 0
    while i < len(messages):
        assistant_msg = messages[i]
        user_msg = messages[i + 1] if i + 1 < len(messages) else None
        pairs.append((assistant_msg, user_msg))
        i += 2
    return pairs
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_pairing.py -v`
Expected: PASS (5 passed)

- [ ] **Step 5: Commit**

```bash
git add meddies/pairing.py tests/test_pairing.py
git commit -m "feat: add turn pairing with role alternation validation"
```

---

### Task 5: Filesystem writer

**Files:**
- Create: `meddies/writer.py`
- Test: `tests/test_writer.py`

**Interfaces:**
- Consumes: `strip_think_block(content: str) -> tuple[str, str | None]` from `meddies.think_strip` (Task 3).
- Produces:
  - `get_next_conv_number(disease_dir: Path) -> int`
  - `write_disease_name_file(disease_dir: Path, original_name: str) -> None`
  - `write_conversation(disease_dir: Path, conv_number: int, pairs: list[tuple[dict, dict | None]]) -> tuple[Path, list[str]]` — returns `(conv_dir, warnings)`, where `warnings` are strings like `"Turn2: unclosed think tag"`. Used by Task 6 (pipeline).

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_writer.py
from meddies.writer import (
    get_next_conv_number,
    write_conversation,
    write_disease_name_file,
)


def _msg(role, content):
    return {"role": role, "content": content}


def test_get_next_conv_number_starts_at_one_for_new_dir(tmp_path):
    disease_dir = tmp_path / "some_disease"
    assert get_next_conv_number(disease_dir) == 1


def test_get_next_conv_number_counts_existing_conv_dirs(tmp_path):
    disease_dir = tmp_path / "some_disease"
    (disease_dir / "conv_0001").mkdir(parents=True)
    (disease_dir / "conv_0002").mkdir(parents=True)
    assert get_next_conv_number(disease_dir) == 3


def test_write_disease_name_file_creates_file_once(tmp_path):
    disease_dir = tmp_path / "some_disease"
    write_disease_name_file(disease_dir, "Bong gân cổ chân")
    name_file = disease_dir / "_disease_name.txt"
    assert name_file.read_text(encoding="utf-8") == "Bong gân cổ chân"

    write_disease_name_file(disease_dir, "should not overwrite")
    assert name_file.read_text(encoding="utf-8") == "Bong gân cổ chân"


def test_write_conversation_creates_turn_folders_with_files(tmp_path):
    disease_dir = tmp_path / "some_disease"
    pairs = [
        (_msg("assistant", "<think>plan</think> Hello!"), _msg("user", "Hi doctor")),
        (_msg("assistant", "Take care."), None),
    ]

    conv_dir, warnings = write_conversation(disease_dir, 1, pairs)

    assert conv_dir == disease_dir / "conv_0001"
    assert (conv_dir / "Turn1" / "assistant.txt").read_text(encoding="utf-8") == "Hello!"
    assert (conv_dir / "Turn1" / "user.txt").read_text(encoding="utf-8") == "Hi doctor"
    assert (conv_dir / "Turn2" / "assistant.txt").read_text(encoding="utf-8") == "Take care."
    assert not (conv_dir / "Turn2" / "user.txt").exists()
    assert warnings == []


def test_write_conversation_logs_unclosed_think_warning(tmp_path):
    disease_dir = tmp_path / "some_disease"
    pairs = [(_msg("assistant", "<think>never closes"), _msg("user", "Hi"))]

    _, warnings = write_conversation(disease_dir, 1, pairs)

    assert warnings == ["Turn1: unclosed think tag"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_writer.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'meddies.writer'`

- [ ] **Step 3: Implement the writer functions**

```python
# meddies/writer.py
from pathlib import Path

from .think_strip import strip_think_block


def get_next_conv_number(disease_dir: Path) -> int:
    if not disease_dir.exists():
        return 1
    existing = [
        p for p in disease_dir.iterdir() if p.is_dir() and p.name.startswith("conv_")
    ]
    return len(existing) + 1


def write_disease_name_file(disease_dir: Path, original_name: str) -> None:
    disease_dir.mkdir(parents=True, exist_ok=True)
    name_file = disease_dir / "_disease_name.txt"
    if not name_file.exists():
        name_file.write_text(original_name, encoding="utf-8")


def write_conversation(
    disease_dir: Path,
    conv_number: int,
    pairs: list[tuple[dict, dict | None]],
) -> tuple[Path, list[str]]:
    conv_dir = disease_dir / f"conv_{conv_number:04d}"
    warnings: list[str] = []

    for turn_index, (assistant_msg, user_msg) in enumerate(pairs, start=1):
        turn_dir = conv_dir / f"Turn{turn_index}"
        turn_dir.mkdir(parents=True, exist_ok=True)

        cleaned, warning = strip_think_block(assistant_msg["content"])
        (turn_dir / "assistant.txt").write_text(cleaned, encoding="utf-8")
        if warning:
            warnings.append(f"Turn{turn_index}: {warning}")

        if user_msg is not None:
            (turn_dir / "user.txt").write_text(
                user_msg["content"].strip(), encoding="utf-8"
            )

    return conv_dir, warnings
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_writer.py -v`
Expected: PASS (5 passed)

- [ ] **Step 5: Commit**

```bash
git add meddies/writer.py tests/test_writer.py
git commit -m "feat: add filesystem writer for conversations and disease folders"
```

---

### Task 6: Row processing orchestration

**Files:**
- Create: `meddies/pipeline.py`
- Test: `tests/test_pipeline.py`

**Interfaces:**
- Consumes:
  - `slugify_disease(name: str | None) -> str` from `meddies.slugify` (Task 2)
  - `pair_turns(messages: list[dict]) -> list[tuple[dict, dict | None]]` from `meddies.pairing` (Task 4), raises `ValueError`
  - `get_next_conv_number(disease_dir: Path) -> int`, `write_disease_name_file(disease_dir: Path, original_name: str) -> None`, `write_conversation(disease_dir: Path, conv_number: int, pairs) -> tuple[Path, list[str]]` from `meddies.writer` (Task 5)
- Produces: `class MeddiesProcessor` with `__init__(self, output_root: Path)`, `process_row(self, row: dict, config: str, log_fn: Callable[[str], None]) -> str` (returns `"written"` if the row was written, with or without warnings, or `"skipped"` if it failed role validation), and an instance attribute `first_written_conv_dir: Path | None` that captures the directory of the very first successfully written conversation across the processor's lifetime (stays `None` until then, never overwritten after). Used by Task 7 (CLI) for the automated spot-check.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_pipeline.py
from meddies.pipeline import MeddiesProcessor


def _row(row_id, messages, target_disease="Bong gân cổ chân"):
    return {
        "id": row_id,
        "messages": messages,
        "target_disease": target_disease,
        "turns_count": len(messages),
        "patient_persona": "unused",
    }


def _msg(role, content):
    return {"role": role, "content": content}


def test_process_row_writes_conversation_and_disease_name_file(tmp_path):
    processor = MeddiesProcessor(tmp_path)
    logs = []
    row = _row("row-1", [_msg("assistant", "Hello"), _msg("user", "Hi")])

    status = processor.process_row(row, "vietnamese", logs.append)

    disease_dir = tmp_path / "vietnamese" / "bong_gan_co_chan"
    assert status == "written"
    assert (disease_dir / "_disease_name.txt").read_text(encoding="utf-8") == "Bong gân cổ chân"
    assert (disease_dir / "conv_0001" / "Turn1" / "assistant.txt").read_text(
        encoding="utf-8"
    ) == "Hello"
    assert logs == []


def test_process_row_increments_conv_number_per_disease(tmp_path):
    processor = MeddiesProcessor(tmp_path)
    logs = []
    row1 = _row("row-1", [_msg("assistant", "a1"), _msg("user", "u1")])
    row2 = _row("row-2", [_msg("assistant", "a2"), _msg("user", "u2")])

    processor.process_row(row1, "vietnamese", logs.append)
    processor.process_row(row2, "vietnamese", logs.append)

    disease_dir = tmp_path / "vietnamese" / "bong_gan_co_chan"
    assert (disease_dir / "conv_0001").exists()
    assert (disease_dir / "conv_0002").exists()


def test_process_row_skips_and_logs_invalid_role_order(tmp_path):
    processor = MeddiesProcessor(tmp_path)
    logs = []
    row = _row("row-bad", [_msg("user", "u1"), _msg("assistant", "a1")])

    status = processor.process_row(row, "vietnamese", logs.append)

    assert status == "skipped"
    assert not (tmp_path / "vietnamese").exists()
    assert len(logs) == 1
    assert "row-bad" in logs[0]
    assert "SKIPPED" in logs[0]


def test_first_written_conv_dir_is_set_once_and_not_overwritten(tmp_path):
    processor = MeddiesProcessor(tmp_path)
    logs = []
    row1 = _row("row-1", [_msg("assistant", "a1"), _msg("user", "u1")])
    row2 = _row("row-2", [_msg("assistant", "a2"), _msg("user", "u2")])

    assert processor.first_written_conv_dir is None

    processor.process_row(row1, "vietnamese", logs.append)
    first_dir = processor.first_written_conv_dir
    assert first_dir == tmp_path / "vietnamese" / "bong_gan_co_chan" / "conv_0001"

    processor.process_row(row2, "vietnamese", logs.append)
    assert processor.first_written_conv_dir == first_dir


def test_process_row_logs_think_tag_warning_without_skipping(tmp_path):
    processor = MeddiesProcessor(tmp_path)
    logs = []
    row = _row(
        "row-warn",
        [_msg("assistant", "<think>never closes"), _msg("user", "u1")],
    )

    status = processor.process_row(row, "vietnamese", logs.append)

    disease_dir = tmp_path / "vietnamese" / "bong_gan_co_chan"
    assert status == "written"
    assert (disease_dir / "conv_0001" / "Turn1" / "assistant.txt").exists()
    assert len(logs) == 1
    assert "row-warn" in logs[0]
    assert "WARNING" in logs[0]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_pipeline.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'meddies.pipeline'`

- [ ] **Step 3: Implement `MeddiesProcessor`**

```python
# meddies/pipeline.py
from pathlib import Path
from typing import Callable

from .pairing import pair_turns
from .slugify import slugify_disease
from .writer import get_next_conv_number, write_conversation, write_disease_name_file


class MeddiesProcessor:
    def __init__(self, output_root: Path):
        self.output_root = output_root
        self._conv_counters: dict[tuple[str, str], int] = {}
        self.first_written_conv_dir: Path | None = None

    def process_row(
        self, row: dict, config: str, log_fn: Callable[[str], None]
    ) -> str:
        row_id = row.get("id", "<unknown>")

        try:
            pairs = pair_turns(row["messages"])
        except ValueError as exc:
            log_fn(f"{config}\t{row_id}\tSKIPPED\t{exc}")
            return "skipped"

        original_disease_name = row.get("target_disease") or ""
        disease_slug = slugify_disease(original_disease_name)
        disease_dir = self.output_root / config / disease_slug
        write_disease_name_file(disease_dir, original_disease_name)

        counter_key = (config, disease_slug)
        if counter_key not in self._conv_counters:
            self._conv_counters[counter_key] = get_next_conv_number(disease_dir)
        conv_number = self._conv_counters[counter_key]
        self._conv_counters[counter_key] += 1

        conv_dir, warnings = write_conversation(disease_dir, conv_number, pairs)
        if self.first_written_conv_dir is None:
            self.first_written_conv_dir = conv_dir
        for warning in warnings:
            log_fn(f"{config}\t{row_id}\tWARNING\t{warning}")
        return "written"
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_pipeline.py -v`
Expected: PASS (5 passed)

- [ ] **Step 5: Commit**

```bash
git add meddies/pipeline.py tests/test_pipeline.py
git commit -m "feat: add row processing orchestration with skip/warning logging"
```

---

### Task 7: CLI entrypoint

**Files:**
- Create: `download_meddies.py`
- Test: `tests/test_cli.py`

**Interfaces:**
- Consumes: `MeddiesProcessor(output_root: Path)` / `.process_row(row, config, log_fn) -> str` / `.first_written_conv_dir: Path | None` from `meddies.pipeline` (Task 6); `datasets.load_dataset`.
- Produces: `build_arg_parser() -> argparse.ArgumentParser`, `run(configs: list[str], limit: int, output_root: Path) -> dict` (summary with per-config `{"processed": int, "skipped": int, "warnings": int}` plus a top-level `"first_written_conv_dir": Path | None`), `format_tree(path: Path) -> str`, `main() -> None`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_cli.py
from datasets import Dataset

import download_meddies


def _fake_row(row_id, disease, messages=None):
    return {
        "id": row_id,
        "subset": "vietnamese",
        "messages": messages
        if messages is not None
        else [
            {"role": "assistant", "content": "Hello"},
            {"role": "user", "content": "Hi"},
        ],
        "target_disease": disease,
        "turns_count": 2,
        "patient_persona": "unused",
    }


def test_run_processes_rows_up_to_limit_and_writes_output(tmp_path, monkeypatch):
    fake_dataset = Dataset.from_list(
        [_fake_row(f"row-{i}", "Bong gân cổ chân") for i in range(5)]
    )

    def fake_load_dataset(repo_id, config_name, streaming=False):
        assert repo_id == "Meddies/meddies-consultant"
        return {"train": fake_dataset}

    monkeypatch.setattr(download_meddies, "load_dataset", fake_load_dataset)

    summary = download_meddies.run(
        configs=["vietnamese"], limit=3, output_root=tmp_path
    )

    assert summary["vietnamese"] == {"processed": 3, "skipped": 0, "warnings": 0}
    disease_dir = tmp_path / "vietnamese" / "bong_gan_co_chan"
    assert (disease_dir / "conv_0001").exists()
    assert (disease_dir / "conv_0003").exists()
    assert not (disease_dir / "conv_0004").exists()
    assert summary["first_written_conv_dir"] == disease_dir / "conv_0001"


def test_run_limit_larger_than_dataset_processes_all_rows(tmp_path, monkeypatch):
    fake_dataset = Dataset.from_list(
        [_fake_row(f"row-{i}", "Bong gân cổ chân") for i in range(2)]
    )

    def fake_load_dataset(repo_id, config_name, streaming=False):
        return {"train": fake_dataset}

    monkeypatch.setattr(download_meddies, "load_dataset", fake_load_dataset)

    summary = download_meddies.run(
        configs=["vietnamese"], limit=100, output_root=tmp_path
    )

    assert summary["vietnamese"] == {"processed": 2, "skipped": 0, "warnings": 0}


def test_run_counts_skipped_and_warning_rows(tmp_path, monkeypatch):
    good_row = _fake_row("row-good", "Bong gân cổ chân")
    skipped_row = _fake_row(
        "row-skip",
        "Bong gân cổ chân",
        messages=[
            {"role": "user", "content": "u1"},
            {"role": "assistant", "content": "a1"},
        ],
    )
    warning_row = _fake_row(
        "row-warn",
        "Bong gân cổ chân",
        messages=[
            {"role": "assistant", "content": "<think>never closes"},
            {"role": "user", "content": "u1"},
        ],
    )
    fake_dataset = Dataset.from_list([good_row, skipped_row, warning_row])

    def fake_load_dataset(repo_id, config_name, streaming=False):
        return {"train": fake_dataset}

    monkeypatch.setattr(download_meddies, "load_dataset", fake_load_dataset)

    summary = download_meddies.run(
        configs=["vietnamese"], limit=3, output_root=tmp_path
    )

    assert summary["vietnamese"] == {"processed": 2, "skipped": 1, "warnings": 1}
    assert (tmp_path / "skipped_rows.log").exists()


def test_format_tree_lists_files_under_directory(tmp_path):
    conv_dir = tmp_path / "conv_0001"
    (conv_dir / "Turn1").mkdir(parents=True)
    (conv_dir / "Turn1" / "assistant.txt").write_text("hi", encoding="utf-8")

    tree = download_meddies.format_tree(conv_dir)

    assert "Turn1" in tree
    assert "assistant.txt" in tree


def test_build_arg_parser_defaults():
    parser = download_meddies.build_arg_parser()
    args = parser.parse_args([])
    assert args.configs == ["vietnamese", "english"]
    assert args.limit == 100
    assert str(args.output) == "output"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_cli.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'download_meddies'`

- [ ] **Step 3: Implement the CLI**

```python
# download_meddies.py
import argparse
from pathlib import Path

from datasets import load_dataset

from meddies.pipeline import MeddiesProcessor


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Download and restructure Meddies consultation transcripts."
    )
    parser.add_argument(
        "--configs", nargs="+", default=["vietnamese", "english"]
    )
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--output", type=Path, default=Path("output"))
    return parser


def format_tree(root: Path) -> str:
    lines = [root.name]
    for path in sorted(root.rglob("*")):
        depth = len(path.relative_to(root).parts) - 1
        lines.append("  " * depth + path.name)
    return "\n".join(lines)


def run(configs: list[str], limit: int, output_root: Path) -> dict:
    output_root.mkdir(parents=True, exist_ok=True)
    log_path = output_root / "skipped_rows.log"
    processor = MeddiesProcessor(output_root)
    summary: dict = {}

    with log_path.open("a", encoding="utf-8") as log_file:
        for config in configs:
            counts = {"processed": 0, "skipped": 0, "warnings": 0}

            def log_fn(line: str, counts=counts) -> None:
                log_file.write(line + "\n")
                if "\tWARNING\t" in line:
                    counts["warnings"] += 1

            dataset = load_dataset(
                "Meddies/meddies-consultant", config, streaming=False
            )["train"]
            n = min(limit, len(dataset))
            for row in dataset.select(range(n)):
                status = processor.process_row(dict(row), config, log_fn)
                if status == "written":
                    counts["processed"] += 1
                else:
                    counts["skipped"] += 1
            summary[config] = counts

    summary["first_written_conv_dir"] = processor.first_written_conv_dir
    return summary


def main() -> None:
    args = build_arg_parser().parse_args()
    summary = run(args.configs, args.limit, args.output)
    for config in args.configs:
        stats = summary[config]
        print(
            f"{config}: processed {stats['processed']} rows, "
            f"skipped {stats['skipped']}, warnings {stats['warnings']}"
        )
    print(f"Output written to: {args.output.resolve()}")

    first_conv_dir = summary["first_written_conv_dir"]
    if first_conv_dir is not None:
        print(f"\nSpot-check — first conversation written ({first_conv_dir}):")
        print(format_tree(first_conv_dir))
    else:
        print("\nNo conversations were written.")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_cli.py -v`
Expected: PASS (5 passed)

- [ ] **Step 5: Run the full test suite**

Run: `pytest -v`
Expected: all tests across every task pass (smoke, slugify, think_strip, pairing, writer, pipeline, cli)

- [ ] **Step 6: Commit**

```bash
git add download_meddies.py tests/test_cli.py
git commit -m "feat: add CLI entrypoint for downloading and restructuring Meddies dataset"
```

---

### Task 8: Real end-to-end run and manual verification

**Files:**
- None created — this task runs the real script against the live Hugging Face dataset (no mocking) and manually verifies the output described in the spec's Verification section.

**Interfaces:**
- Consumes: `main()` / `run()` from `download_meddies.py` (Task 7), exercised via the actual CLI against the real network.

- [ ] **Step 1: Run the script against the real dataset**

Run: `python download_meddies.py --configs vietnamese english --limit 100 --output output/`
Expected: no crash; prints per-config `processed`/`skipped`/`warnings` counts, the output path, and a spot-check file tree of the first conversation written (this is all automated by Task 7's `main()` — no manual counting needed here).

- [ ] **Step 2: Cross-check the printed row counts against the filesystem**

Run: `find output/vietnamese -maxdepth 2 -type d -name 'conv_*' | wc -l` and the same for `output/english`
Expected: total conv folders across all disease subfolders matches the `processed` count the script printed for that config.

- [ ] **Step 3: Inspect a sample `assistant.txt` for think-block stripping**

Run: open any `Turn1/assistant.txt` under a `vietnamese` conversation and confirm it contains only the natural-language reply, no `<think>` tag content.

- [ ] **Step 4: Review `skipped_rows.log`**

Run: `cat output/skipped_rows.log` (file may not exist if nothing was skipped/warned — that's a valid outcome)
Expected: any `SKIPPED` or `WARNING` lines are legible and reference a real row id, and their counts match what the script printed.

- [ ] **Step 5: Record the outcome**

No commit needed for this task (the `output/` directory is gitignored), but note in the PR/summary how many rows were processed vs. skipped, and flag anything surprising in the real data (e.g. more role-order violations than expected) as input to the next feature.

---

## Future features

_(Append new dated feature plans below this line as they're designed. Do not renumber or remove completed task sections — treat them as a changelog of what shipped.)_
