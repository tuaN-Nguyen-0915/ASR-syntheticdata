#!/usr/bin/env bash
#
# Pilot runner for the Meddies TTS pipeline — 54 utterances, 1 shard, ~$0.02 of A100.
#
# Two stages, deliberately separated:
#   ./pilot/run_pilot.sh setup      volumes + uploads + image build + weights   (no GPU generation)
#   ./pilot/run_pilot.sh generate --yes   the actual paid run                     (spends money)
#
# `setup` is safe and idempotent — re-run it freely. `generate` is the one that bills.
# The split exists because the image build compiles flash-attn from source and has
# never run; if it fails we want to know before any GPU time is bought.
#
set -euo pipefail

cd "$(dirname "$0")/.."
REPO_ROOT="$(pwd)"
VISEC="/Users/phananhtuannguyen/Desktop/Project/ASR-syntheticdata/data/ViSEC-processed/processed_audio_by_id"
VIVOS="pilot/refs_vivos/processed_audio_by_id"
# Which pool this run uses, read straight from the config so the script and the
# container can never disagree about it.
REFS_SOURCE="$(python3 -c "import yaml;print((yaml.safe_load(open('pilot/pilot.yaml')).get('refs') or {}).get('source','visec'))")"
CONFIG="pilot/pilot.yaml"
PLAN="pilot/shard_plan.parquet"

green() { printf "\033[32m%s\033[0m\n" "$1"; }
red()   { printf "\033[31m%s\033[0m\n" "$1"; }
step()  { printf "\n\033[1m== %s\033[0m\n" "$1"; }

die() { red "FAILED: $1"; exit 1; }

# ---------------------------------------------------------------- preflight
check_prereqs() {
  step "Checking prerequisites"

  command -v modal >/dev/null || die "modal not installed — run: pip install modal && modal setup"
  green "  modal $(modal --version 2>&1 | sed 's/.*version: //')"

  python3 -c "from huggingface_hub import whoami; print('  HF user:', whoami()['name'])" \
    || die "HF token invalid — run: hf auth login --force"

  modal secret list 2>/dev/null | grep -q huggingface \
    || die "Modal secret 'huggingface' missing — create it at modal.com/secrets with key HF_TOKEN"
  green "  modal secret 'huggingface' present"

  for f in "$CONFIG" "$PLAN" pilot/shard_plan.hash; do
    [ -f "$f" ] || die "missing $f — rebuild with cli.py build-manifest + plan"
  done
  green "  pilot artifacts present"

  if [ "$REFS_SOURCE" = "vivos" ]; then
    [ -d "$VIVOS" ] || die "VIVOS refs missing — run: python3 cli.py --config $CONFIG build-refs --dest pilot/refs_vivos"
    green "  refs pool: vivos ($(ls "$VIVOS"/*.wav 2>/dev/null | wc -l | tr -d ' ') wav files)"
  else
    [ -d "$VISEC" ] || die "ViSEC reference audio not found at $VISEC"
    green "  refs pool: visec ($(ls "$VISEC"/*.wav 2>/dev/null | wc -l | tr -d ' ') wav files)"
  fi

  # This is the cheap gate that catches a bad token before any GPU is requested.
  python3 cli.py --config "$CONFIG" preflight || die "preflight failed — see message above"
}

# ---------------------------------------------------------------- setup
do_setup() {
  check_prereqs

  step "Creating volumes (idempotent — 'already exists' is fine)"
  for v in meddies-tts-plan visec-refs vivos-refs voxcpm2-weights; do
    if modal volume create "$v" 2>/dev/null; then
      green "  created $v"
    else
      green "  $v already exists"
    fi
  done

  step "Uploading plan, hash and config"
  # --force so re-running after a replan overwrites rather than erroring.
  modal volume put --force meddies-tts-plan "$PLAN"              /shard_plan.parquet
  modal volume put --force meddies-tts-plan pilot/shard_plan.hash /shard_plan.hash
  modal volume put --force meddies-tts-plan "$CONFIG"             /config.yaml
  green "  plan volume ready"

  # Each pool lives on its own Volume, both mounted by app.py, so switching back
  # never re-uploads anything that is already there.
  if [ "$REFS_SOURCE" = "vivos" ]; then
    step "Uploading 65 VIVOS reference wavs (~22 MB, one-time)"
    if modal volume ls vivos-refs /processed_audio_by_id >/dev/null 2>&1; then
      green "  already uploaded — skipping"
    else
      modal volume create vivos-refs 2>/dev/null || true
      modal volume put vivos-refs "$VIVOS" /processed_audio_by_id
      green "  VIVOS references uploaded"
    fi
  else
    step "Uploading 147 ViSEC reference wavs (~54 MB, one-time)"
    if modal volume ls visec-refs /processed_audio_by_id >/dev/null 2>&1; then
      green "  already uploaded — skipping"
    else
      modal volume put visec-refs "$VISEC" /processed_audio_by_id
      green "  references uploaded"
    fi
  fi

  step "Building the image and fetching VoxCPM2 weights"
  echo "  Uses a prebuilt flash-attn wheel pinned to torch 2.8.0+cu128 (see app.py)."
  echo "  Cached after the first build; a rebuild only happens if app.py's image changes."
  modal run app.py::fetch_weights

  green ""
  green "Setup complete. Nothing has been billed for generation yet."
  echo  "Next:  ./pilot/run_pilot.sh generate"
}

# ---------------------------------------------------------------- generate
do_generate() {
  check_prereqs

  step "PAID RUN — 54 utterances, 1 shard, ~\$0.02 of A100 time"
  echo "  Target repo : npat1509/TestSynth  (public)"
  echo "  Refs pool   : $REFS_SOURCE"
  echo "  Plan hash   : $(python3 -c "import json;print(json.load(open('pilot/shard_plan.hash'))['vietnamese'])")"
  echo
  # Confirmation must work without a TTY (this gets driven from tooling that has no
  # interactive terminal), so: --yes skips the prompt, and a non-TTY stdin without
  # --yes refuses rather than hanging forever on `read`.
  if [ "${2:-}" = "--yes" ] || [ "${PILOT_YES:-}" = "1" ]; then
    echo "  proceeding (--yes)"
  elif [ -t 0 ]; then
    read -r -p "  Proceed? [y/N] " reply
    [[ "$reply" =~ ^[Yy]$ ]] || { echo "  aborted"; exit 0; }
  else
    red "  no terminal to confirm on — re-run as: $0 generate --yes"
    exit 2
  fi

  step "Running"
  modal run app.py --config-path "$CONFIG" --plan-path "$PLAN" 2>&1 | tee pilot/run.log

  green ""
  green "Run finished. Transcript saved to pilot/run.log"
  echo  "Verify the published shard with:  ./pilot/run_pilot.sh verify"
}

# ---------------------------------------------------------------- verify
do_verify() {
  step "Verifying the published shard (read-only, no cost)"
  python3 - <<'PY'
from huggingface_hub import HfApi
api = HfApi()
files = [f for f in api.list_repo_files("npat1509/TestSynth", repo_type="dataset")
         if f.endswith(".parquet")]
if not files:
    print("  no parquet shards published yet"); raise SystemExit(1)
print("  shards on the Hub:")
for f in files: print("   ", f)

import pyarrow.parquet as pq, io, soundfile as sf
p = api.hf_hub_download("npat1509/TestSynth", files[0], repo_type="dataset")
t = pq.read_table(p)
print(f"\n  rows: {t.num_rows}  columns: {len(t.column_names)}")
md = t.schema.metadata or {}
print("  huggingface Audio metadata preserved:", b"huggingface" in md)
print("  plan_hash embedded                  :", md.get(b"plan_hash", b"MISSING").decode()[:40])
a = t.column("audio").to_pylist()[0]
d, sr = sf.read(io.BytesIO(a["bytes"]), dtype="float32")
print(f"  first clip: {sr} Hz, {len(d)/sr:.2f}s, path={a['path']}")
print(f"  text_spoken: {t.column('text_spoken').to_pylist()[0][:80]}...")
secs = sum(t.column("duration_s").to_pylist())
chars = sum(len(x) for x in t.column("text_spoken").to_pylist())
print(f"\n  MEASURED chars/sec = {chars/secs:.2f}   (config assumes 14.0)")
print( "  ^ this is the number the pilot exists to find — put it in config.yaml")
PY
}

case "${1:-}" in
  setup)    do_setup ;;
  generate) do_generate "$@" ;;   # forward args so do_generate can see --yes
  verify)   do_verify ;;
  *)        echo "usage: $0 {setup|generate|verify}"; exit 2 ;;
esac
