# Meddies TTS Synthesis — Design

**Date:** 2026-07-28
**Status:** Approved, ready for implementation planning

Turn the Vietnamese half of `output_full/` into a spoken-conversation ASR corpus by
synthesizing every turn with VoxCPM2, voice-cloned from ViSEC reference speakers, on
Modal GPUs, published to Hugging Face as sharded Parquet.

---

## 1. Goal and scope

Generate one audio clip per `user.txt` / `assistant.txt` in
`output_full/vietnamese/`, voiced by two distinct ViSEC reference speakers held fixed
for the duration of each conversation, and publish the result as a Hugging Face dataset
suitable for training Vietnamese ASR.

**Bulk run:** Vietnamese only (57,756 conversations, 711,647 utterances). English at full
scale would roughly triple total cost and would be spoken by Vietnamese reference
speakers, i.e. Vietnamese-accented English — a decision to take later, deliberately.

**But the pipeline is multi-config from day one.** English is fully implemented, not
stubbed: `cli.py sample --config english -n 20` generates a listening pack without
uploading anything, and switching the bulk run to English is a config change plus a
Stage 1 re-plan — no code change. See §3.8.

### Measured inputs

| | value |
|---|---|
| conversations (vietnamese) | 57,756 |
| utterances | 711,647 |
| mean chars — user / assistant | 380 / 597 |
| p50 / p90 / p99 chars | 343 / 1,089 / 2,067 |
| max chars observed | 75,915 (degenerate, see §5) |
| reference speakers | 147, 16 kHz mono, 10.0–14.2 s each |

### Estimated outputs

All figures below derive from an **assumed 14 chars/sec** speech rate. This assumption
is unverified and is the single largest source of error in this document; §9 makes
measuring it a hard gate before the full run.

| | estimate |
|---|---|
| audio generated | ~6,900 h |
| A100-40GB GPU-hours (at ~70× realtime aggregate) | ~99 |
| GPU cost (`$0.000583`/sec) | ~$210, realistically $250–400 |
| storage as 16 kHz FLAC | ~480 GB |
| shards | ~473 |
| wall clock at 20 containers | ~5 h |

---

## 2. Background: what the two upstream repos give us

**VoxCPM2** (`openbmb/VoxCPM2`) — 2B-param tokenizer-free diffusion-autoregressive TTS
(LocEnc → TSLM → RALM → LocDiT over AudioVAE V2 latents). 30 languages including
Vietnamese. Native output 48 kHz. ~8 GB VRAM, CUDA ≥ 12, PyTorch ≥ 2.5.

**nanovllm-voxcpm** (`a710128/nanovllm-voxcpm`) — a nano-vLLM-derived serving engine for
VoxCPM. Requires Linux/Windows + NVIDIA + `flash-attn`; **CPU execution is unsupported**,
which is why none of this can run on the development Mac.

Its value is **continuous batching**. Published RTX 4090 benchmarks (short prompt, no LoRA):

| concurrency | per-stream RTF | aggregate throughput |
|---|---|---|
| 1 | 0.098 | ~10× realtime |
| 8 | 0.143 | ~56× |
| 16 | 0.222 | ~72× |
| 64 | 0.696 | **~92×** |

Per-stream latency degrades with concurrency while total throughput improves ~9×. **A
sequential loop over utterances would waste ~90% of the GPU.** Keeping many requests in
flight is therefore the central architectural constraint, not an optimization.

### Relevant API surface (verified by reading the source)

```python
VoxCPM.from_pretrained(model, inference_timesteps=10, max_num_batched_tokens=16384,
                       max_num_seqs=512, max_model_len=4096,
                       gpu_memory_utilization=0.9, enforce_eager=False, devices=[0])

await server.wait_for_ready()
info = await server.get_model_info()          # -> sample_rate, encoder_sample_rate, channels

await server.encode_latents(wav: bytes, wav_format: str) -> bytes   # NO transcript needed
await server.add_prompt(wav: bytes, wav_format: str, prompt_text: str)  # transcript REQUIRED

async for chunk in server.generate(              # async generator of float32 np arrays
        target_text: str,
        ref_audio_latents: bytes | None = None,
        prompt_latents: bytes | None = None, prompt_text: str = "",
        prompt_id: str | None = None,
        max_generate_length: int = 2000,
        temperature: float = 1.0, cfg_value: float = 2.0,
        seed: int | None = None):
    ...
```

Two consequences:

- ViSEC has **no reference transcripts**, so `add_prompt` / `prompt_id` (which require
  `prompt_text`) are unusable. We use **`encode_latents` + `ref_audio_latents`**, which
  needs no transcript. This is timbre/style conditioning rather than VoxCPM's
  prompt-continuation "ultimate cloning" mode; slightly lower fidelity, fully functional.
- `generate` accepts a **`seed`**, giving bit-reproducible output per request. This is
  what makes retries idempotent (§8).

`encode_latents` internally resamples and mono-mixes via librosa, so the 16 kHz ViSEC
WAVs need no preprocessing.

---

## 3. Key decisions and their rationale

### 3.1 Output sample rate: 16 kHz, not VoxCPM's native 48 kHz

Every ViSEC reference WAV is **16 kHz mono** — zero energy above 8 kHz. Generating 48 kHz
from an 8 kHz-band-limited conditioning signal means the model invents the top two
octaves. 16 kHz is the honest ceiling of the source material, and is what Whisper /
wav2vec2 consume anyway. Encoded as **FLAC** (lossless at that rate).

This also reduces storage 6× versus 48 kHz WAV: ~480 GB instead of ~2.4 TB.

### 3.2 Storage: sharded Parquet on Hugging Face, not a mirrored file tree

The original request was for a tree mirroring `output_full/` with audio instead of text.
That is not publishable. Hugging Face's documented limits:

| HF limit | mirrored tree |
|---|---|
| files per repo: <100k recommended | 711,647 |
| entries per folder: 10k **hard max** | — |
| commit size ~50–100 files | 7,000–14,000 commits; HF warns UX degrades past a few thousand |
| free-user public storage: "best-effort" | 480 GB likely flagged; PRO gives 10 TB |

HF explicitly recommends Parquet or WebDataset for large datasets, and requires one of
them for the dataset viewer and script-free `load_dataset()`.

**The tree structure is not lost — it is demoted from filesystem paths to columns.** Each
row carries `disease_slug` / `conv_id` / `turn` / `role`, and its `audio.path` field holds
the original tree path (`vietnamese/ap_xe_hau_mon/conv_0001/Turn1/user.flac`). A short
script can materialize the `output_full`-shaped tree on demand. The canonical artifact is
~473 files rather than 711,647.

### 3.3 Input transport: a manifest Parquet, not the file tree

`output_full/` is 2.47M files on a laptop; uploading it to a Modal Volume would be slow
and fragile. But the *content* is only ~490 MB of text. Stage 0 flattens the tree into a
single local `manifest.parquet` (~130 MB compressed); Stage 1 turns that into
`shard_plan.parquet`, which additionally carries `text_spoken`, speaker assignments and
shard ids (~300 MB compressed).

**Only `shard_plan.parquet` is uploaded to the Modal Volume** — it is the sole input the
GPU containers read. `manifest.parquet` stays local as the intermediate that Stage 1
re-plans from. The 711k-file tree never leaves the development machine.

Normalization and rejection therefore run **locally in Stage 1**, not on the GPU: vinorm
over 711k utterances takes roughly 20 minutes of CPU, and doing it up front means text is
validated before any GPU time is spent and the GPU image needs no vinorm dependency.

### 3.4 Speaker assignment: random per conversation, fixed across turns

Each conversation draws an unordered pair of distinct speakers — one for all `user` turns,
one for all `assistant` turns — uniformly at random from the pool. Re-rolling per turn
would change both voices mid-conversation, destroying the speaker continuity that makes
conversational ASR data valuable.

The draw is seeded from the conversation's identity rather than a global RNG:

```python
rng = Random(blake2b(f"{salt}/{config}/{disease_slug}/{conv_id}".encode(),
                     digest_size=8).digest())
user_spk, asst_spk = rng.sample(pool, 2)
```

Statistically identical to `random.sample`, but repeatable — so regenerating a shard
reproduces the same voices, plans can be rebuilt without retaining the file, and adding
data later does not reshuffle existing conversations.

Imbalance is not a concern at this scale: 57,756 conversations over 147 speakers gives
~393 conversations per speaker per role (σ ≈ 20), so essentially all speakers land in
[360, 426]. No balanced or round-robin assignment is needed.

`PerTurnAssigner` is implemented alongside `PerConversationAssigner` and selected by
config (§3.7).

### 3.5 Speaker pool: all 147, with quality flags carried into the data

Metadata analysis found real quality problems:

| filter | speakers |
|---|---|
| all | 147 |
| unique source audio ≥ 12 s (no repetition) | 100 |
| contains any neutral speech | 112 |
| contains neutral **and** no repetition | 87 |
| neutral-only | 13 |
| neutral-only **and** no repetition | **1** |

- **49 of 147** speakers have less unique source audio than their own reference file.
  Speaker 79 has **1.3 s** of unique material padded into a 12.1 s file across 10 "clips";
  speakers 136, 146, 140, 144 have 2–3 s. These are effectively cloned from looped snippets.
- **35 speakers contain no neutral speech at all** — 6 pure `angry`, 3 pure `happy`,
  13 pure `sad`. A pure-angry reference yields an angry doctor.
- **36 speakers splice all four emotions** into one 12 s file, giving prosodically
  incoherent conditioning.

Since a clean-neutral non-repeated pool is exactly **one** speaker, no filter is
satisfactory. **Decision: use all 147**, and carry `speaker_id`, `speaker_emotions`, and
`speaker_unique_source_s` as columns so weak voices can be filtered **at training time**
rather than baked out at generation time. The pool is also a config value, so a filtered
pool can be selected later without code changes.

### 3.6 Text preparation

Measured over 10,342 sampled Vietnamese utterances:

| pattern | % of utterances | user / assistant |
|---|---|---|
| `**bold**` | 25.7% | 7.8% / 41.0% |
| numbered list | 23.3% | 6.8% / 37.3% |
| bullet `- ` | 19.4% | 6.6% / 30.3% |
| digits | 43.7% | 31.7% / 54.0% |
| parenthetical | 25.8% | 6.9% / 42.0% |
| ALLCAPS word | 16.1% | 4.8% / 25.8% |
| slash `a/b` | 17.3% | 6.0% / 26.9% |

**Normalization** is a per-language strategy behind one protocol, so adding a language is
a new class rather than a branch scattered through the pipeline:

```python
class Normalizer(Protocol):
    def normalize(self, text: str) -> str: ...

VietnameseNormalizer  # markdown strip → vinorm
EnglishNormalizer     # markdown strip → num2words for digits/units
```

Shared markdown stripping (emphasis, bullets, list numbering, whitespace collapse) lives
in one function used by both. Vietnamese then runs **`vinorm`**, the standard Vietnamese
TTS normalizer — `38.5°C` → `ba mươi tám phẩy năm độ C`. English runs `num2words` for the
equivalent job. The normalizer is selected by the row's `config` value.

**This changes what the transcript is.** The ASR ground truth must match what was spoken,
so every row stores both `text_raw` (original) and **`text_spoken`** (post-vinorm, what
the model actually said). Training targets `text_spoken`.

**Chunking:** 12.3% of utterances exceed 1,000 chars — too long for one stable
autoregressive generation. Split on sentence boundaries, greedily pack into ≤400-char
chunks, generate each independently against the same `ref_audio_latents`, concatenate with
250 ms of silence. Chunks stay independent so they batch freely in the engine. 88% of
utterances need no chunking at all. Seamless continuation via `prompt_latents` is a
possible later upgrade; it is not used initially because it serializes chunks within an
utterance and lets drift accumulate.

### 3.7 Runtime configuration

Everything tunable is config, not code, and the resolved config is stamped into each
shard's Parquet metadata for provenance:

```yaml
speaker:
  policy: per_conversation      # or per_turn
  pool: all                     # or a file listing allowed speaker_ids
  seed_salt: "v1"               # bump to reshuffle every voice
engine:
  concurrency: 48               # MUST be <= max_num_seqs
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
  qc_asr_sample_rate: 0.01
```

Speaker assignment is resolved in Stage 1, which is CPU-only and takes seconds — so
changing policy or pool costs no GPU time.

### 3.8 Multi-config support

`config` is a first-class dimension, never a hardcoded `"vietnamese"`:

- **Manifest** — Stage 0 enumerates every config present under `output_full/`, so
  `manifest.parquet` already contains both languages. The bulk run is narrowed by
  `run.configs`, not by what was ingested.
- **Normalization** — selected per row by `config` (§3.6).
- **Reject thresholds and QC duration bounds** — `text.*` and the calibrated chars/sec are
  keyed by config, because English and Vietnamese differ in both speech rate and typical
  type-token ratio. Applying Vietnamese thresholds to English would silently mis-reject.
- **Shard ids** — namespaced by config (`vi-00000-of-00473`, `en-00000-of-01100`), so the
  two languages can be planned and run independently and neither renumbers the other.
- **Publication** — one HF dataset repo with two configs rather than two repos:

  ```
  data/vietnamese/train-00000-of-00473.parquet
  data/english/train-00000-of-01100.parquet
  ```

  declared via `configs:` in the dataset card, giving
  `load_dataset("<user>/meddies-speech", "vietnamese")`. Adding English later is new files
  in an existing repo, not a migration.
- **Reference speakers** — unchanged. The same 147 Vietnamese speakers voice both
  languages; English output is therefore Vietnamese-accented by construction. That is a
  property to evaluate in the listening pack, not a bug.

**Auditioning before committing:** `cli.py sample --config english -n 20` picks random
conversations, runs the full path (normalize → chunk → generate → QC), and writes WAVs
plus a small local Parquet for listening. It uploads nothing and needs no plan, so it is
safe to run at any time against either language for a few cents.

---

## 4. Architecture

```
STAGE 0  local, CPU, one-off
  output_full/vietnamese/**  ──►  manifest.parquet  (~130 MB, stays local)
  711,647 rows: config, disease_slug, disease_name, conv_id, turn, role, text_raw

STAGE 1  local, CPU  (~20 min first time; seconds to re-plan speakers only)
  normalize (markdown strip + vinorm) ──► text_spoken
  reject degenerate utterances (§5)   ──► rejects.jsonl
  assign speakers per conversation
  pack conversations into ~473 shards; a conversation is never split
  ──► shard_plan.parquet  (~300 MB)  ──► uploaded once to a Modal Volume

STAGE 2  Modal, GPU     modal run app.py --shards 0-472
  per container:
    @modal.enter():  load engine ONCE
                     encode_latents() × 147 refs ONCE   (amortized over ~1,500 utterances)
    per shard:       ~1,500 utterances → ~2,400 chunk requests
                     asyncio.Semaphore(48) + gather      ← the batching
                     chunks → join w/ 250 ms silence → 48k→16k → FLAC
                     write shard parquet → upload to HF → rm local
    ~12 min/shard

STAGE 3  local
  dataset card, README, split metadata, QC summary
```

### Why this shape

Three architectures were considered:

- **A — shard as work unit, asyncio fan-out inside the container (chosen).** Large
  payloads never cross Modal's result boundary; the batching concurrency is an explicit,
  measurable semaphore; crash-resume is free at shard granularity; scaling to H100 is a
  one-word change.
- **B — utterance as work unit via `@modal.concurrent(max_inputs=48)`.** Rejected:
  711,647 Modal inputs incur per-input scheduling overhead, audio returns through Modal's
  result path, a second aggregation pass is needed to build shards, and the batching is
  hidden inside Modal.
- **C — persistent engine as a Modal service with a separate driver.** Rejected as the
  bulk pipeline: the driver becomes a bottleneck and 480 GB of audio would cross HTTP. Worth
  building later as a small interactive audition endpoint.

### Module layout

```
meddies_tts/
  manifest.py   tree → manifest parquet
  textprep.py   markdown strip · vinorm · reject rules
  chunking.py   sentence split · ≤400-char packing
  speakers.py   pool loading · PerConversation / PerTurn assigners
  shards.py     shard planning · parquet schema · writer
  audio.py      concat · silence join · 48k→16k · FLAC
  qc.py         per-utterance sanity checks · ASR round-trip
  engine.py     nano-vllm wrapper — the ONLY GPU-dependent module
app.py          Modal app: image, volumes, @enter, shard function
cli.py          build-manifest · plan · estimate · status · sample · materialize-tree
```

Every module except `engine.py` and `app.py` is pure Python with no GPU import, so the
whole pipeline is unit-testable on the development Mac.

### Modal application

```python
image = (modal.Image.debian_slim(python_version="3.11")
         .pip_install("torch", "nano-vllm-voxcpm", "vinorm", "datasets",
                      "soundfile", "soxr", "huggingface_hub[hf_transfer]")
         .pip_install("flash-attn", extra_options="--no-build-isolation")
         .env({"HF_HUB_ENABLE_HF_TRANSFER": "1"}))

@app.cls(image=image, gpu="A100-40GB",
         volumes={"/weights": weights, "/plan": plan},
         secrets=[modal.Secret.from_name("huggingface")],
         timeout=3600, max_containers=20)
class Synthesizer:
    @modal.enter()
    async def load(self):
        self.server = VoxCPM.from_pretrained(model="/weights/VoxCPM2",
                                             max_num_seqs=64, devices=[0])
        await self.server.wait_for_ready()
        self.sr = int((await self.server.get_model_info())["sample_rate"])
        self.refs = {sid: await self.server.encode_latents(wav, "wav")
                     for sid, wav in load_reference_wavs()}

    @modal.method()
    async def run_shard(self, shard_id: int) -> dict: ...
```

VoxCPM2 weights are fetched once via `snapshot_download` onto a Modal Volume and mounted
read-only. Two known build hazards: `flash-attn` requires `--no-build-isolation`, and
nano-vllm raises `ValueError: Missing parameters` on `.pt` checkpoints — it needs
safetensors alongside `config.json`. The image build asserts this rather than discovering
it on first GPU run.

---

## 5. Rejection rules

The upstream dataset contains LLM degeneration. The worst sampled example
(`vietnamese/viem_xoang_mui_di_ung/conv_0007/Turn4/user.txt`, 75,915 chars) has 12,855
words and 513 unique, collapsing into `... Tri Tri Tri không triệu triệu triệu tri tri`.
Synthesized, that single utterance would be ~90 minutes of looping gibberish costing
~1.5 GPU-hours.

Measured cost share over 10,342 sampled utterances:

| rule | % of utterances | **% of GPU budget** |
|---|---|---|
| TTR < 0.25 and >200 words | 0.11% | **4.1%** |
| `len>3000 OR TTR<0.35` | 0.33% | **5.7%** |
| len > 2000 | 1.16% | 9.5% |

**Rule:** reject an utterance if
`len > max_chars` **OR** (`words > 200` **AND** `type_token_ratio < min_ttr`
**AND** `max_5gram_repeat >= max_ngram_repeat`).

Definitions, over whitespace-split tokens: `type_token_ratio = len(set(words))/len(words)`;
`max_5gram_repeat` is the highest frequency of any contiguous 5-token n-gram.

The 0.33% / 5.7% figures in the table above were measured for the two-branch rule
`len>3000 OR (words>200 AND TTR<0.35)`. Adding the n-gram conjunct makes the rule
marginally stricter, so actual rejections will be at or slightly below those figures; the
`len>3000` branch alone accounts for 0.31% of utterances and 5.6% of characters, so the
totals are dominated by it either way.

Rejected utterances are dropped — not truncated, since the tail of a degenerate text is
also gibberish — and written to `rejects.jsonl` with path, reason and text so the rule
stays auditable and tunable. The rest of the conversation is retained. Net effect: ~0.33%
of utterances removed, ~5.7% of GPU spend saved, and degenerate audio kept out of a
published dataset.

---

## 6. Data schema

One row per utterance. The `audio` column uses the HF `Audio` feature so the dataset
viewer and `load_dataset()` work with no loading script.

| column | type | notes |
|---|---|---|
| `config` | string | `"vietnamese"` |
| `disease_slug` | string | `"ap_xe_hau_mon"` |
| `disease_name` | string | original un-slugified name |
| `conv_id` | string | `"conv_0001"` |
| `turn` | int32 | 1-based |
| `role` | string | `"user"` \| `"assistant"` |
| `text_raw` | string | original `.txt` content |
| `text_spoken` | string | post-vinorm — **the ASR ground truth** |
| `speaker_id` | int32 | 0–146 |
| `speaker_emotions` | string | e.g. `"angry\|happy\|neutral\|sad"` |
| `speaker_unique_source_s` | float32 | for filtering looped-reference voices |
| `audio` | `{bytes, path}` | FLAC 16 kHz mono; `path` = `vietnamese/<slug>/<conv>/Turn<N>/<role>.flac` |
| `duration_s` | float32 | |
| `n_chunks` | int32 | how many generations were joined |
| `seed` | int64 | generation seed |
| `engine_version` | string | nano-vllm + model version |

**Shard sizing:** 16 kHz 16-bit FLAC ≈ 19 KB/s of audio, so a ~1 GB shard holds ~14.6 h
≈ 122 conversations ≈ 1,500 utterances ≈ 12 min of A100 time. ~473 shards total, named
`data/vietnamese/train-00000-of-00473.parquet` (§3.8). Shards are packed from a sorted
enumeration so shard ids are stable across re-planning, and a conversation is never split
across shards.

---

## 7. Generation core

```python
sem = asyncio.Semaphore(cfg.engine.concurrency)     # <= max_num_seqs

async def synth_chunk(req) -> np.ndarray:
    async with sem:
        buf = [d async for d in server.generate(
            target_text=req.text,
            ref_audio_latents=refs[req.speaker_id],
            cfg_value=cfg.engine.cfg_value,
            temperature=cfg.engine.temperature,
            seed=req.seed)]
        return np.concatenate(buf, axis=0)

waves = await asyncio.gather(*(synth_chunk(c) for c in shard_chunks))
```

All ~2,400 chunk requests for a shard are submitted at once and throttled only by the
semaphore, so the engine always has work to batch. The generation seed is
`int.from_bytes(blake2b(f"{salt}/{audio_path}#{chunk_idx}", digest_size=8).digest())`,
making every chunk independently reproducible.

---

## 8. Error handling

| level | behaviour | rationale |
|---|---|---|
| **chunk** | retry ×2 with a derived seed, then mark failed | transient engine/CUDA faults must not cost a shard |
| **utterance** | drop, append to `failures.jsonl`, continue | one bad turn must not delete a conversation |
| **shard** | abandon; upload nothing | upload happens only after the complete Parquet is written, so a shard is atomic and HF never holds a partial shard |
| **run** | re-run the same `.map()` | the driver diffs the plan against what is already on the Hub and dispatches only the gap |

Combined with seeded generation, re-running the full job is always safe and cheap, and a
regenerated shard is bit-identical to the original.

### 8.1 Resuming after an interruption

The run must survive exhausted credits, a closed laptop, or a three-month gap, and pick up
exactly where it stopped. Four properties make that work:

**Completion state lives on the Hub, not locally.** The driver calls
`HfApi.list_repo_files()` **once** at startup (not `file_exists` per shard — that would be
473 round-trips), diffs it against the plan, and dispatches only missing shard ids. There
is no local checkpoint file to lose, and resuming from a different machine works with no
setup beyond credentials.

**Shards are atomic.** Upload happens only after a complete Parquet is written, so an
interruption — including credits running out mid-container — leaves either a whole shard
or nothing. A partial shard can never be mistaken for a finished one.

**The plan is a stored artifact, not a recomputation.** `shard_plan.parquet` is uploaded
to the Modal Volume *and* published to the dataset repo under `plan/`. Resuming reads that
file rather than rebuilding it, so a newer vinorm version, a different machine, or an
edited config cannot silently repartition the work and orphan finished shards.

**Drift is detected, not discovered.** The plan carries a `plan_hash` over (config,
conversation set, speaker salt, normalization version, shard packing). Every uploaded
shard records the hash that produced it. `cli.py status` compares the current plan against
the hashes on the Hub and **refuses to dispatch** on a mismatch, reporting what changed
rather than quietly writing incompatible shards next to old ones. This is the failure that
actually bites after a long gap, so it fails loudly.

```
$ modal run app.py --shards remaining
$ python cli.py status
  plan  vi  plan_hash=8f3c…  473 shards
  done  312   remaining 161   failed 0
  spent ~$137   projected remaining ~$71   ~2.0 h at 20 containers
```

`--shards remaining` is the normal way to run; explicit ids and ranges stay available for
the pilot and for re-doing specific shards.

---

## 9. Quality control

**Per utterance (no model, microseconds):**

- non-empty; no NaN/inf
- RMS above a silence floor — catches dead audio
- `duration_s` within `[0.3×, 3×]` of the expected duration from the calibrated
  chars/sec — catches truncation *and* runaway looping
- `max_generate_length` not reached — truncation signal

A failing check triggers a retry with a new seed; a second failure rejects the utterance.

**Sampled ASR round-trip:** Whisper transcribes `qc_asr_sample_rate` of utterances (1% in
the full run, 100% during the pilot) and CER/WER is computed against `text_spoken`,
summarized per shard. This is the only check that verifies the model *said the right
words* — particularly for vinorm-verbalized numbers, where Vietnamese TTS fails silently.
Cost is negligible relative to TTS.

**Pilot gate.** Before the full run, 3 shards (~366 conversations, ~4,500 utterances,
roughly $2) produce `pilot_report.md` containing:

- the measured **chars → seconds** ratio, and corrected totals for hours, GB and dollars
- **RTF swept over concurrency ∈ {1, 8, 16, 32, 48, 64}**, fixing the semaphore value
- CER from a full Whisper round-trip
- a listening pack: one sentence across ~10 speakers spanning clean-neutral,
  1.3 s-looped, pure-angry and 4-emotion-splice categories

The full run is not launched until this report is reviewed. Every cost figure in this
document depends on the first bullet.

---

## 10. Cost controls

- `cli.py estimate` projects GPU-hours, dollars and GB from the manifest before launch
- `cli.py status` reports done / remaining / spent / projected-remaining at any time
- `--max-shards` and Modal `max_containers` cap burn rate
- `--budget-usd` stops dispatching new shards once projected spend is reached
- per-shard actual cost is logged, making drift from estimate visible during the run

Because completion state lives on the Hub (§8.1), budget caps and resumption compose: a
run capped at `--budget-usd 50` stops cleanly, and the next `--shards remaining`
continues from exactly that point whenever credits allow. The corpus is usable at every
intermediate point — each finished shard is a valid, loadable slice of the dataset — so
stopping early degrades size rather than breaking the artifact.

---

## 11. Testing

Everything except `engine.py` is GPU-free and runs on the development Mac.

**Unit:**
- `textprep` — shared markdown stripping; `VietnameseNormalizer` and `EnglishNormalizer`
  each selected by `config`; rejection rules, using the real
  `viem_xoang_mui_di_ung/conv_0007/Turn4` degenerate text as a fixture
- `chunking` — sentence boundaries, packing limits, a long sentence with no punctuation
- `speakers` — determinism under a fixed salt, `A != B`, policy swap, distribution sanity
- `shards` — a conversation is never split; shard ids stable across re-planning; ids
  namespaced per config so planning English cannot renumber Vietnamese
- `audio` — concatenation, silence joining, 48k→16k resample, FLAC round-trip
- `qc` — each threshold fires on a crafted failure and passes clean audio
- `resume` — given a plan and a fake repo listing, the driver dispatches exactly the
  missing shard ids; a changed salt/config/packing alters `plan_hash` and `status`
  refuses to dispatch rather than writing incompatible shards

**Integration with `FakeEngine`:** a stand-in implementing the same protocol as
`engine.py` and yielding sine waves. Runs the entire Stage 2 locally, writes a real
Parquet shard, and asserts `load_dataset()` reads it back with decodable audio — full
pipeline coverage with no GPU and no cost.

**Modal smoke test:** one shard of 2 conversations against the real engine, asserting the
uploaded shard round-trips.

---

## 12. Open risks

1. **The 14 chars/sec assumption is unverified.** All cost, storage and duration figures
   scale linearly with it. Resolved by the pilot (§9).
2. **Reference audio quality.** 49 speakers are cloned from looped snippets and 35 have no
   neutral speech. Mitigated by carrying quality columns for train-time filtering, and by
   the pilot listening pack.
3. **`ref_audio_latents` fidelity.** Without transcripts we cannot use VoxCPM's
   prompt-continuation cloning mode. Expected to be adequate; the pilot's CER and listening
   pack will confirm.
4. **vinorm behaviour on medical text.** Dosages, ranges (`4-5/10`) and units may verbalize
   oddly. The 100% round-trip during the pilot surfaces this.
5. **HF storage tier.** ~480 GB on a free account is "best-effort" and may be flagged; a
   PRO plan provides 10 TB of public storage.
6. **Speaker diversity.** 147 speakers across ~6,900 h is ~47 h per speaker — high volume,
   low acoustic diversity. **Consciously deferred:** noted and accepted for this iteration,
   to be addressed later (more speakers, or noise/RIR/rate augmentation). The
   `speaker_id` / `speaker_emotions` / `speaker_unique_source_s` columns and the
   config-selectable speaker pool exist so that work needs no change to this pipeline.
