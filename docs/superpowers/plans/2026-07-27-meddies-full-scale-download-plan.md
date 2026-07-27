# Meddies Full-Scale Download (Feature 2) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let `download_meddies.py` process the complete `vietnamese` (58,064 rows) and `english` (109,005 rows) configs instead of just a sample, with a "process everything" flag and progress output for the multi-minute run.

**Architecture:** Two small, additive changes to `run()` in `download_meddies.py` — no new files, no new modules. The existing pipeline (`meddies/pipeline.py`, `meddies/writer.py`, etc.) is untouched.

**Tech Stack:** Python 3.10+, `datasets` (Hugging Face), `pytest` — same as Feature 1, no new dependencies.

## Global Constraints

- `--limit 0` means "no cap, process every row in the config"; the CLI default stays `100` — unaffected unless `0` is passed explicitly.
- Progress reporting: print one line every 5,000 rows *iterated* within a config (counting every row reached, written or skipped) — fires only at exact multiples of 5,000 (row 5000, 10000, 15000, ...). The end-of-run summary already printed by `main()` is unchanged and is not a duplicate of this.
- No disk-space preflight check (explicitly out of scope).
- No new resumability/chunking mechanism — the existing reprocess-refusal guard from Feature 1 is unchanged and still governs reruns.
- `RandomQA` / `RandomQuestion` configs are out of scope for this feature.
- No test should process the real 167k-row dataset — use small fake datasets via `Dataset.from_list(...)` and monkeypatched `load_dataset`, exactly like Feature 1's CLI tests. The real full-scale run is a manual verification task, not an automated test.

---

### Task 1: `--limit 0` means "process every row"

**Files:**
- Modify: `download_meddies.py` (the `n = min(limit, len(dataset))` line inside `run()`)
- Test: `tests/test_cli.py`

**Interfaces:**
- Consumes: existing `run(configs: list[str], limit: int, output_root: Path) -> dict` signature — unchanged, only its internal row-count logic changes.
- Produces: nothing new for other tasks to consume; Task 2 touches the same loop but is otherwise independent.

- [ ] **Step 1: Write the failing test**

```python
# in tests/test_cli.py

def test_run_limit_zero_processes_every_row(tmp_path, monkeypatch):
    fake_dataset = Dataset.from_list(
        [_fake_row(f"row-{i}", "Bong gân cổ chân") for i in range(12)]
    )

    def fake_load_dataset(repo_id, config_name, streaming=False):
        return {"train": fake_dataset}

    monkeypatch.setattr(download_meddies, "load_dataset", fake_load_dataset)

    summary = download_meddies.run(
        configs=["vietnamese"], limit=0, output_root=tmp_path
    )

    assert summary["vietnamese"] == {"processed": 12, "skipped": 0, "warnings": 0}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_cli.py::test_run_limit_zero_processes_every_row -v`
Expected: FAIL — with `limit=0`, the current code computes `min(0, 12) == 0`, so `dataset.select(range(0))` processes zero rows; the assertion `{"processed": 12, ...}` fails against the actual `{"processed": 0, ...}`.

- [ ] **Step 3: Implement the fix**

In `download_meddies.py`, inside `run()`, find this line (it appears once, in the per-config loop after `load_dataset`):

```python
            n = min(limit, len(dataset))
```

Replace it with:

```python
            n = len(dataset) if limit == 0 else min(limit, len(dataset))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_cli.py::test_run_limit_zero_processes_every_row -v`
Expected: PASS

- [ ] **Step 5: Run the full test suite to confirm no regressions**

Run: `pytest -v`
Expected: all existing tests (52 before this task) plus the new one pass, since default `limit=100` behavior and every existing test's explicit non-zero `limit` values are untouched by this change.

- [ ] **Step 6: Commit**

```bash
git add download_meddies.py tests/test_cli.py
git commit -m "feat: support --limit 0 to process every row in a config"
```

---

### Task 2: Progress reporting every 5,000 rows

**Files:**
- Modify: `download_meddies.py` (the `for row in dataset.select(range(n)):` loop inside `run()`)
- Test: `tests/test_cli.py`

**Interfaces:**
- Consumes: nothing new from Task 1 — this task's test passes an explicit `limit` value sized to its fake dataset rather than relying on `limit=0`, so it's independently testable regardless of task execution order.
- Produces: nothing new for other tasks to consume.

- [ ] **Step 1: Write the failing test**

```python
# in tests/test_cli.py

def test_run_prints_progress_every_5000_rows(tmp_path, monkeypatch, capsys):
    fake_dataset = Dataset.from_list(
        [_fake_row(f"row-{i}", "Bong gân cổ chân") for i in range(10001)]
    )

    def fake_load_dataset(repo_id, config_name, streaming=False):
        return {"train": fake_dataset}

    monkeypatch.setattr(download_meddies, "load_dataset", fake_load_dataset)

    download_meddies.run(configs=["vietnamese"], limit=10001, output_root=tmp_path)

    captured = capsys.readouterr()
    assert "vietnamese: 5000/10001 rows iterated" in captured.out
    assert "vietnamese: 10000/10001 rows iterated" in captured.out
    # No boundary at 10001 itself — only exact multiples of 5000 fire.
    assert "vietnamese: 10001/10001 rows iterated" not in captured.out
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_cli.py::test_run_prints_progress_every_5000_rows -v`
Expected: FAIL — nothing is currently printed during the row loop, so `captured.out` doesn't contain either expected substring.

- [ ] **Step 3: Implement progress printing**

In `download_meddies.py`, inside `run()`, find this loop (it appears once, in the per-config loop):

```python
            for row in dataset.select(range(n)):
                status = processor.process_row(
                    dict(row), config, lambda line, c=counts: log_fn(line, c)
                )
                if status == STATUS_WRITTEN:
                    counts["processed"] += 1
                else:
                    counts["skipped"] += 1
```

Replace it with:

```python
            for i, row in enumerate(dataset.select(range(n)), start=1):
                status = processor.process_row(
                    dict(row), config, lambda line, c=counts: log_fn(line, c)
                )
                if status == STATUS_WRITTEN:
                    counts["processed"] += 1
                else:
                    counts["skipped"] += 1
                if i % 5000 == 0:
                    print(f"{config}: {i}/{n} rows iterated...")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_cli.py::test_run_prints_progress_every_5000_rows -v`
Expected: PASS

- [ ] **Step 5: Run the full test suite to confirm no regressions**

Run: `pytest -v`
Expected: all tests (54 before this task) plus the new one pass. In particular, confirm `test_run_processes_rows_up_to_limit_and_writes_output` and other small-row-count tests still pass — they process fewer than 5,000 rows, so no progress line fires for them, and none of them assert on stdout content in a way this would break.

- [ ] **Step 6: Commit**

```bash
git add download_meddies.py tests/test_cli.py
git commit -m "feat: print progress every 5,000 rows iterated during a run"
```

---

### Task 3: Real full-scale run and manual verification

**Files:**
- None created — this task runs the real script against the live Hugging Face dataset at full scale (no mocking) and verifies the output, following the same pattern as Feature 1's Task 8.

**Interfaces:**
- Consumes: `main()` / `run()` from `download_meddies.py` (Tasks 1-2), exercised via the actual CLI against the real network at `--limit 0`.

- [ ] **Step 1: Confirm a clean output directory and that it's gitignored**

Run: `ls output/ 2>&1` — if `output/vietnamese` or `output/english` already exist with data from earlier sample runs, use a fresh directory name for this run (e.g. `output_full/`) instead of clearing `output/`, since the reprocess-refusal guard (Feature 1) will otherwise refuse to touch a config that already has data.

The current `.gitignore` only contains the exact entry `output/`, which will NOT match a differently-named directory like `output_full/`. Before running, update `.gitignore` to a wildcard pattern that covers both:

```
# .gitignore
output*/
__pycache__/
*.pyc
.pytest_cache/
```

Commit this change on its own:

```bash
git add .gitignore
git commit -m "chore: gitignore all output*/ directories, not just output/"
```

- [ ] **Step 2: Run the full-scale download**

Run: `HF_HUB_DISABLE_IMPLICIT_TOKEN=1 python3 download_meddies.py --configs vietnamese english --limit 0 --output output_full/`

(The `HF_HUB_DISABLE_IMPLICIT_TOKEN=1` prefix works around a stale cached HF OAuth token on this machine, unrelated to this project's code — same as Feature 1's Task 8.)

Expected: completes in roughly 6-10 minutes; progress lines appear periodically (e.g. `vietnamese: 5000/58064 rows iterated...`); final summary reports `processed`/`skipped`/`warnings` counts per config close to the full row counts (58,064 for vietnamese, 109,005 for english, minus any genuinely malformed rows skipped).

- [ ] **Step 3: Cross-check row counts against the filesystem**

Run: `find output_full/vietnamese -maxdepth 2 -type d -name 'conv_*' | wc -l` and the same for `output_full/english`
Expected: each count matches the `processed` count the script printed for that config.

- [ ] **Step 4: Spot-check a handful of conversations across different diseases**

Run: `find output_full/vietnamese -maxdepth 1 -type d | shuf | head -3` to sample a few disease folders, then inspect one `conv_0001/Turn1/assistant.txt` in each.
Expected: contains only the natural-language reply, no `<think>` tag content, consistent with Feature 1's verified behavior.

- [ ] **Step 5: Review `skipped_rows.log` for anomaly rate**

Run: `wc -l output_full/skipped_rows.log` and `grep -c SKIPPED output_full/skipped_rows.log`
Expected: skip rate roughly consistent with Feature 1's sample finding (2 skipped out of 100 vietnamese rows, i.e. ~2%) — a wildly different rate at full scale would be worth investigating before treating the output as ready to use.

- [ ] **Step 6: Record the outcome**

No commit needed for the output data itself (`output_full/` is now covered by the wildcard `.gitignore` pattern added in Step 1 — confirm with `git check-ignore output_full/`). Note final processed/skipped/warning counts and total disk usage (`du -sh output_full/`) for the record.
