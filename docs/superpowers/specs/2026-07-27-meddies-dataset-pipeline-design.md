# Meddies Dataset Pipeline — Design Spec

This is a living spec for the ASR-syntheticdata project's work on the
[`Meddies/meddies-consultant`](https://huggingface.co/datasets/Meddies/meddies-consultant)
dataset. New features get appended as their own numbered section below;
existing sections should stay intact unless a feature is explicitly revised.

## Dataset background

`Meddies/meddies-consultant` is a synthetic Vietnamese-first medical
consultation dataset (CC-BY-NC-4.0). It has 4 configs:

- `vietnamese` — 58,064 rows, multi-turn consultations (~12.33 turns avg)
- `english` — 109,005 rows, multi-turn consultations (~16.12 turns avg)
- `RandomQA` — 67,372 rows, 2-turn Q&A (not used by Feature 1)
- `RandomQuestion` — 61,162 rows, question-only (not used by Feature 1)

Each row in `vietnamese`/`english` has: `id`, `subset`, `messages`,
`target_disease`, `turns_count`, `patient_persona`. `messages` is a list of
`{role, content}` alternating `assistant`/`user`, starting with `assistant`.
Every `assistant` message content is prefixed with a `<think>...</think>`
reasoning block (verified present in both `vietnamese` and `english`
samples) followed by the natural-language reply actually said to the
patient.

---

## Feature 1: Download & restructure consultation transcripts into per-turn files

### Goal

Fetch a sample of the `vietnamese` and `english` configs and materialize
each conversation on disk as one folder per turn, containing the spoken
assistant reply and the paired user message as plain text files — organized
by `target_disease` — so the conversations are easy to browse and usable
as source material for downstream ASR/TTS work.

### Scope (this feature)

Sample only: **first 100 rows** of `vietnamese` and first 100 rows of
`english` (via `dataset.select(range(100))`, not random sampling). Full
dataset processing is an explicit future feature (see below), gated on
reviewing this sample's output first.

### Data source

`datasets.load_dataset("Meddies/meddies-consultant", config_name, streaming=False)`
for `config_name in ["vietnamese", "english"]`.

Non-streaming was chosen over streaming after explicit debate: streaming
saves disk only during the download step, but since every row's content
gets written out to output files regardless, that saving is moot — while
streaming loses local caching/resumability. A non-streaming load caches
the parquet shards locally, so reruns (debugging, crash recovery) read
from disk instead of re-fetching over the network.

### Output structure

```
output/
  <config>/                          # "vietnamese" or "english"
    <disease_slug>/
      _disease_name.txt              # original, un-slugified target_disease
      conv_0001/
        Turn1/
          assistant.txt
          user.txt
        Turn2/
          assistant.txt
          user.txt
        ...
      conv_0002/
        ...
    skipped_rows.log                 # rows that failed validation, with reason
```

- `<disease_slug>`: `target_disease` normalized to ASCII (diacritics
  stripped via unicode normalization), lowercased, spaces/punctuation
  collapsed to underscores. Empty/missing `target_disease` → `unknown_disease`.
- `_disease_name.txt`: holds the original `target_disease` string exactly
  as it appears in the dataset. Exists because ASCII-slugging can map two
  distinct disease names to the same slug; this file is the source of
  truth if that happens, so no information is silently lost.
- `conv_NNNN`: zero-padded, **counter restarts at 1 within each
  `<disease_slug>` folder** (not global across the config, not shared
  between `vietnamese` and `english`).
- `TurnM`: `M` increments per `(assistant, user)` pair, in conversation
  order, starting at 1.

### Processing rules

1. **Role validation**: before pairing, check the row's `messages` list
   alternates strictly starting with `assistant` (even 0-based index =
   assistant, odd = user). If a row violates this, skip the row entirely
   and append `{row_id, config, reason}` to `skipped_rows.log` — do not
   attempt to pair/write it.
2. **Think-block stripping**: for each `assistant` message, look for a
   `<think>...</think>` block.
   - If both open and close tags are found, strip that block (and any
     surrounding whitespace) and write only the remaining text to
     `assistant.txt`.
   - If `<think>` is found but `</think>` is missing (e.g. truncated
     generation), do **not** strip anything — write the full raw content
     to `assistant.txt` and log `{row_id, turn, reason: "unclosed think tag"}`
     to `skipped_rows.log` (the row itself is still written; this is a
     content warning, not a row-skip).
3. **Turn pairing**: walk `messages` in order, grouping into
   `(assistant[i], user[i+1])` pairs → `TurnM` folders.
4. **Odd-length conversations**: if the last message is an unpaired
   `assistant` message (no following `user` message), its `TurnM` folder
   gets `assistant.txt` only — no empty `user.txt` is created.
5. **Encoding**: all files written as UTF-8 plain text, no trailing
   metadata or headers — file content is exactly the message text (after
   think-stripping where applicable).

### CLI interface

Single script: `download_meddies.py`

```
python download_meddies.py --configs vietnamese english --limit 100 --output output/
```

- `--configs`: space-separated list, defaults to `vietnamese english`.
- `--limit`: rows per config, defaults to `100`. Passing a value larger
  than a config's row count just processes all available rows.
- `--output`: output root directory, defaults to `output/`.

Flag-driven so the eventual full-dataset run (Feature 2) is a
`--limit` change, not a script rewrite.

### Verification

On completion, print a summary:
- rows processed per config
- rows skipped (with counts by reason, referencing `skipped_rows.log`)
- folders/files created
- the file tree of the first written conversation, as a spot-check

### Explicitly out of scope for this feature

- `RandomQA` / `RandomQuestion` configs (different structure, no think
  blocks in the same sense, not part of the assistant/user turn format
  requested).
- Full-dataset processing (~167k rows, millions of files) — planned as a
  later feature once this sample's output is reviewed.
- Deduplication or filtering of `target_disease` values beyond ASCII
  slugging.
- Any transformation of `patient_persona` (left unused for this feature).

---

## Future features

_(Append new dated feature sections below this line as they're designed.
Do not renumber or remove completed feature sections — treat them as a
changelog of what shipped.)_
