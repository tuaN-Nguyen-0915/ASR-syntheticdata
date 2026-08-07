# ASR-syntheticdata

Turns the [`Meddies/meddies-consultant`](https://huggingface.co/datasets/Meddies/meddies-consultant)
text corpus (Vietnamese synthetic medical consultations) into a **speech** dataset:
every conversation turn is synthesized with VoxCPM2, voice-cloned from a reference
speaker, and published as sharded Parquet on Hugging Face.

```
Meddies/meddies-consultant        58,064 Vietnamese rows
        │  download_meddies.py
        ▼
output_full/vietnamese/…          712,881 per-turn .txt files
        │  cli.py build-manifest → plan       (local, GPU-free)
        ▼
shard_plan.parquet                normalized text + speaker + shard assignment
        │  app.py on Modal        (one A100 container per shard)
        ▼
<hf-repo>/data/vietnamese/*.parquet   audio + transcript + provenance
```

**Status:** the pipeline runs end to end and has been validated on a 54-utterance
pilot. The full corpus run has **not** been done — see [Before a full run](#before-a-full-run).

---

## Stage 1 — download the text corpus

```bash
pip install -r requirements.txt
python download_meddies.py --configs vietnamese english --limit 0 --output output_full/
```

`--limit 0` processes every row. Download is non-streaming on purpose: the dataset
caches locally, so re-running after a crash reads from disk instead of refetching.

Output layout, one directory per conversation turn:

```
output_full/
  vietnamese/
    <disease_slug>/
      _disease_name.txt        original disease name(s)
      conv_0001/Turn1/assistant.txt
      conv_0001/Turn1/user.txt
  skipped_rows.log             malformed or warned rows
```

Re-running against a directory that already holds data for a config is refused
rather than silently duplicated.

## Stage 2 — synthesize speech

Local, GPU-free commands (everything except `app.py` and `engine.py` runs on a Mac):

```bash
python3 cli.py --config config.yaml build-manifest --root output_full --out manifest.parquet
python3 cli.py --config config.yaml plan --manifest manifest.parquet \
    --visec <refs>/metadata.csv --out shard_plan.parquet --rejects rejects.jsonl
python3 cli.py --config config.yaml estimate      # GPU-hours, cost, storage
python3 cli.py --config config.yaml preflight     # verify the HF token before spending
python3 cli.py --config config.yaml status        # done vs remaining shards
```

The GPU work runs on [Modal](https://modal.com) — VoxCPM2 needs Linux + NVIDIA +
flash-attn and cannot run on macOS:

```bash
modal run app.py --shards remaining      # resumable; skips what is already published
```

Each container loads the model once and synthesizes a whole shard, so the ~90 s
engine load amortizes over ~1,500 utterances. Shards are uploaded to the Hub and
deleted locally as they finish, so a full run never needs the whole corpus on disk.

### Pilot and experiments

ViSEC reference audio is not in the repo. `run_pilot.sh` searches upward for
`data/ViSEC-processed/`, or set `MEDDIES_VISEC_DIR`. Only needed when
`refs.source` is `visec` — the VIVOS pools are built by `cli.py build-refs`.

```bash
./pilot/run_pilot.sh setup            # volumes, uploads, image build — free, idempotent
./pilot/run_pilot.sh generate --yes   # the paid run (~$0.03)
./pilot/run_pilot.sh verify           # read the published shard, print measured chars/sec

./pilot/sweep_refs.sh 30              # one reference-duration variant, end to end
```

Audition arbitrary text without publishing anything:

```bash
modal run app.py::try_text --text-file pilot/try/example.txt --speaker VIVOSSPK22
```

Output lands in `pilot/try_out/` as FLAC plus a `report.json` showing raw vs spoken
text. It reuses the real normalizer and shard runner, so it exercises the actual
pipeline rather than a shortcut.

---

## How the text pipeline works

Order is load-bearing — several rules break if moved:

```
1. strip_reasoning       remove leaked <thinking> / (internal_reasoning) blocks
2. strip_markup          bold, bullets, headings, blockquotes
3. strip_assistant_echo  remove a quoted assistant turn (user turns only)
4. verbalize numbers     digits → Vietnamese words, per speaker dialect
5. clean_punctuation     reduce punctuation to '.' and ','
6. chunk_text            130 chars + 14 tolerance, sentence-first
```

Number verbalization must precede punctuation cleanup, because range (`6-8`),
decimal (`38.5`), fraction (`140/90`) and comparator (`>`) rules all need marks
that step 5 removes. Echo detection must precede verbalization, because the two
speakers in a turn get different number dialects.

Chunking exists because VoxCPM2 degrades past roughly 13 s per generation. Chunks
are generated independently and rejoined with 250 ms of silence.

**Full details, with real input/output for every rule:**
[`docs/PREPROCESSING.md`](docs/PREPROCESSING.md)

## Configuration

`config.yaml` drives everything. The values that matter most:

| key | meaning |
|---|---|
| `refs.source` / `dir` | which reference-voice pool (`visec` 147 speakers, or `vivos` 65) |
| `engine.inference_timesteps` | diffusion steps; too few causes runaway generations |
| `engine.temperature` | 1.0 — lowering it caused mass degenerate repetition |
| `text.chunk_max_chars` | fixed character budget, not seconds-derived |
| `text.chars_per_sec` | feeds QC's expected-duration check |

Every one of these is a **plan-hash input**: changing it invalidates published
shards and forces a re-plan. Decide before a run, never during.

## Documentation

| file | what it covers |
|---|---|
| [`docs/RUNBOOK.md`](docs/RUNBOOK.md) | infrastructure, settled config, full experiment log with numbers |
| [`docs/PREPROCESSING.md`](docs/PREPROCESSING.md) | every text rule with real examples, plus known gaps |
| [`docs/slash-forms.md`](docs/slash-forms.md) | all 15,251 `x/y` forms found in the corpus |
| [`docs/acronyms-table.md`](docs/acronyms-table.md) | 400 acronyms with usage sentences, pending decisions |
| `docs/superpowers/specs/` · `plans/` | original design spec and implementation plan |

## Before a full run

Open items, all recorded in the docs above:

- **`text.chars_per_sec` is 14.0 but measures 15.26.** It feeds QC and the plan
  hash, so it must be set first.
- **Acronym pronunciation is undecided** — 135,907 occurrences currently vary
  per utterance because nothing pins them.
- **Six reproducible normalization gaps** (`%` after a range, bare `°`, `≥`/`≤`,
  `omega-3`, `11h30`, `500k`) and 737,684 unhandled parentheses.
- **~3.5% of user turns are pure assistant echo** and are synthesized from their
  original text by choice, to keep conversations whole.
- **VIVOS references are CC-BY-NC-SA 4.0** — non-commercial and share-alike.

Because every text change alters the plan hash, batch them into one change rather
than fixing them one at a time.

## Development

```bash
pytest -q          # 432 tests, no GPU required
```

Everything except `app.py` and `meddies_tts/engine.py` is GPU-free and testable
locally; a `FakeEngine` covers the full pipeline in tests.
