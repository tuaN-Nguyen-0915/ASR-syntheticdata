# Meddies TTS — setup and experiment log

Synthesizes speech for the Vietnamese medical-consultation corpus with VoxCPM2,
voice-cloned from reference speakers, on Modal GPUs, published as sharded Parquet
to Hugging Face.

Source corpus: [`Meddies/meddies-consultant`](https://huggingface.co/datasets/Meddies/meddies-consultant)
(58,064 Vietnamese rows) → downloaded to `output_full/` → planned → synthesized.

---

## Current settled configuration

| setting | value | why |
|---|---|---|
| `refs.source` / `dir` | `vivos` / `/refs/vivos/v30` | chosen by listening; see [Reference pools](#reference-pools) |
| `refs.target_seconds` | 30 | 15s measured equal and cheaper, but 30s won on ear |
| `engine.cfg_value` | 2.0 | 1.8 was 24% faster but loosened the outlier tail |
| `engine.temperature` | 1.0 | 0.7 caused mass degenerate repetition |
| `engine.inference_timesteps` | 26 | 10 produced runaway generations; 30 no better than 26 |
| `text.chunk_max_chars` | 130 | fixed, not seconds-derived — speech rate varies by pool |
| `text.chunk_overflow_chars` | 14 | absorbing a near-fit sentence cuts 9.6% of chunks |
| `text.chars_per_sec` | **14.0 — STALE** | measured 15.26 at this config; see [Open items](#open-items) |
| `run.gpu` | A100-40GB | |
| `run.convs_per_shard` | 122 | |

Every value above except `concurrency` is a **plan-hash input**: changing it
invalidates published shards and forces a re-plan. Decide before a full run,
never during.

---

## Infrastructure

**Modal app** `meddies-tts` (`app.py`). One container per shard; the shard is the
unit of work so the ~90 s engine load plus reference encoding amortizes over
~1,500 utterances instead of being paid per utterance.

**Volumes**

| volume | contents |
|---|---|
| `voxcpm2-weights` | VoxCPM2 snapshot, fetched once |
| `meddies-tts-plan` | `shard_plan.parquet`, `shard_plan.hash`, `config.yaml` |
| `visec-refs` | 147 ViSEC WAVs at `/processed_audio_by_id` |
| `vivos-refs` | VIVOS WAVs at `/v10/…` and `/v30/…`, one subdir per duration variant |

Both reference volumes mount simultaneously (`/refs/visec`, `/refs/vivos`), so
switching pools is a config edit and never re-uploads anything.

**Secret** `huggingface`, key `HF_TOKEN`, write-scoped. Set it in the Modal
dashboard — never on a command line. The container runs `preflight` in
`@modal.enter()`, before loading the model, so a bad token fails at boot in
seconds instead of after generating a shard.

**Image** — the version pins are a four-way contract; changing one breaks the
others:

```
CUDA 12.9 devel base + python 3.11
torch / torchaudio / torchcodec  2.8.0 / 2.8.0 / 0.7.0, all +cu128, ONE index
flash-attn 2.8.3.post1  (prebuilt wheel: cp311 × torch2.8 × cu12 × cxx11abiTRUE)
nano-vllm-voxcpm 2.0.3
```

A build-time import of the whole stack catches mismatches on the builder rather
than on a paid GPU. Nothing in the engine path runs on arm64 macOS.

---

## Reference pools

| | ViSEC | VIVOS |
|---|---|---|
| speakers | 147 | 65 |
| character | emotional, spontaneous | read speech, neutral |
| transcripts | none | yes (enables transcript-assisted cloning, unused so far) |
| quality issues | 112/147 mix emotions; 35 have no neutral speech; speaker 79 is 1.3 s looped to 12.1 s | 30/325 clips digitally clipped |
| licence | none declared | **CC-BY-NC-SA 4.0** — non-commercial + share-alike |

VIVOS ships nested 5/10/15/20/30 s variants per speaker; `build-refs`
materializes one into ViSEC's on-disk layout so `load_pool` reads both unchanged.

Speaker pairing is **uniform over the pool** — no gender constraint. Measured over
3,000 conversations: 49.8% mixed, 27.8% male-male, 22.4% female-female.

---

## Experiment log

All runs: 54 utterances, 3 conversations, A100-40GB, concurrency 16.
`c/s` = measured chars/sec. Runs marked † predate the echo fix, so their text
differs and audio-seconds are not comparable across that line.

### Engine parameters

| run | pool | steps | temp | CFG | ok/fail | rtf | ×RT | c/s | max ratio |
|---|---|---|---|---|---|---|---|---|---|
| † baseline | ViSEC | 10 | 1.0 | 2.0 | 54/0 | 0.0775 | 12.9 | 16.63 | **2.51** |
| † temperature | ViSEC | 24 | **0.7** | 2.0 | **41/13** | 0.6072 | 1.6 | 10.76 | — |
| † reverted | ViSEC | 24 | 1.0 | 2.0 | 54/0 | 0.1384 | 7.2 | 17.42 | 1.28 |
| † pool switch | VIVOS 10s | 24 | 1.0 | 2.0 | 54/0 | 0.1175 | 8.5 | 15.56 | 1.53 |
| † chunking | VIVOS 10s | 24 | 1.0 | 2.0 | 54/0 | 0.0999 | 10.0 | 14.94 | 2.01 |
| post-echo-fix | VIVOS 30s | 30 | 1.0 | 2.0 | 54/0 | 0.1651 | 6.1 | 15.62 | — |
| **chosen** | VIVOS 30s | **26** | 1.0 | 2.0 | 54/0 | 0.1400 | 7.1 | **15.26** | 1.63 |
| CFG probe | VIVOS 30s | 26 | 1.0 | **1.8** | 54/0 | 0.1132 | 8.8 | 15.21 | **2.12** |

**Findings**

- **Temperature 0.7 was harmful.** 13/54 failed `qc:too_long`, each failing both
  the first attempt and the reseeded retry. Survivors ran 43% longer for the same
  text. Lowering temperature sharpens the sampling distribution, which is a known
  way to lock autoregressive models into repetition loops.
- **`inference_timesteps` affects duration, not just fidelity.** Same seed, same
  text, same temperature, single chunk: 7.84 s at 10 steps vs 3.04 s at 24.
  VoxCPM2 is diffusion-*autoregressive* — LocDiT latents feed back into the AR
  context, so coarse diffusion degrades the trajectory and lets a generation run
  away. 24 steps collapsed the duration-ratio spread from 2.51 to 1.28.
- **CFG 1.8 is 24% faster but loosens adherence.** Max duration ratio rose
  1.63 → 2.12. It passed QC only because `chars_per_sec` is stale at 14.0; at the
  measured rate it would have failed. The real risk — a dropped or swapped word
  inside a normal-length utterance — is **invisible to every check we have**.

### Reference duration sweep (VIVOS, 24 steps)

| variant | clone err | chunk F0 spread | rtf | ×RT |
|---|---|---|---|---|
| 10 s | 4.7% | 41.4% | 0.0999 | 10.0 |
| 15 s | 3.3% | 44.5% | 0.0978 | 10.2 |
| 20 s | 4.6% | 41.9% | 0.1302 | 7.7 |
| 30 s | 3.3% | 45.1% | 0.1373 | 7.3 |

Clone error is **non-monotonic** and a paired sign test rejects nothing (30 s vs
10 s: better in 30/54, p=0.50). Effective n is **6 speakers**, not 54 utterances,
and one hard-to-clone speaker moves the median more than duration does.
Throughput *is* real and steps rather than scales: 10 s and 15 s ~10×, 20 s and
30 s ~7.5×. 30 s was chosen on listening, against the statistics.

*Caveat: F0 measured by crude autocorrelation; ~100% spreads are octave-doubling
artifacts. Between-run comparison is sound, absolute magnitudes are not.*

---

## Corpus defects found

**Assistant echo.** `user.txt` frequently contains a verbatim copy of an
assistant turn before the patient's reply. Measured over 20,000 user utterances,
comparing against *every* assistant turn in the conversation:

| | share |
|---|---|
| clean | 96.19% |
| pure echo — no patient speech at all | **3.50%** |
| echo + real reply (removable) | 0.30% |

533 of 5,294 conversations (10.07%) are affected, but 360 of those have exactly
one bad turn.

**Policy: clean but never drop.** Conversations stay whole. When a file is nothing
but the quote, the original text is used — knowingly bad audio rather than a hole
in the dialogue. Cost of the alternative: dropping whole conversations would lose
12.38% of utterances instead of 1.56%, a 7.9× multiplier.

Detection matches on a canonical letters/digits form with head and tail anchors,
floor 150 chars. The 40–150 char band is deliberately ignored — sampling showed it
is ~50/50 contaminated vs genuine short patient turns quoted back by a later
assistant turn, with no structural signal separating them.

**Other:** corpus files contain **zero newlines**, so line-anchored markdown rules
barely fire. One utterance carries a 10,433-digit run, which crashed `int()`
(now capped at 15 digits). ~0.30% of conversations have single-role turns in the
source.

---

## How to run

```bash
# Full pilot: setup is free and idempotent; generate bills.
./pilot/run_pilot.sh setup
./pilot/run_pilot.sh generate --yes
./pilot/run_pilot.sh verify          # reads the published shard, prints measured chars/sec

# One reference-duration variant, end to end (paid)
./pilot/sweep_refs.sh 30

# Audition ad-hoc text — nothing is uploaded, audio lands in pilot/try_out/
modal run app.py::try_text --text-file pilot/try/example.txt --speaker VIVOSSPK22

# Local, GPU-free
python3 cli.py --config config.yaml show-config | plan | estimate | status | preflight
python3 cli.py --config config.yaml build-refs --dest pilot/refs_vivos30 --target-seconds 30
```

**Before any re-run that changes a plan-hash input:** delete the published shard
and its plan-hash file from the target repo, or `remaining_targets` reports
"nothing to do" and drift detection refuses.

`try_text` reuses `normalizer_for` and `run_shard` verbatim, so it exercises the
real normalization, chunking, QC and joining rather than a shortcut.

---

## Open items

| item | status |
|---|---|
| **`chars_per_sec` is 14.0, measured 15.26** | must be set before a full run; feeds QC's expected-duration check and the plan hash |
| **VIVOS licence CC-BY-NC-SA** | unresolved; may propagate to the synthetic corpus |
| 3.50% of user turns are doctor-voice by policy | accepted trade to keep conversations whole |
| 40–150 char echo band (0.53%) | knowingly unhandled |
| `refs` section absent ⇒ silently defaults to ViSEC | present in both configs now, but the trap remains for a new one |
| `?` and `!` rewritten to `.` | makes period-splitting viable, but the model never sees a question mark, so questions lose rising intonation |
| Reference transcripts unused | VIVOS ships them; would enable VoxCPM2's higher-fidelity cloning mode |
| No text-fidelity check | QC only measures duration; a dropped or swapped word is undetectable |
| No provenance link to source rows | `meddies-consultant` has an `id` column we don't carry; linking back needs text matching |
| `6ecdcc4` is a broken commit | shipped with a failing test; fixed in `5a74667` |
