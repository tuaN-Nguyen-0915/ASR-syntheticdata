#!/usr/bin/env bash
#
# Run the pilot against ONE VIVOS reference-duration variant, end to end.
#
#   ./pilot/sweep_refs.sh 15
#
# Everything except the reference audio is held fixed: seeds derive from
# seed_salt + audio_path + chunk index, and speaker assignment samples the pool in
# id order (every variant carries the same 65 ids in the same order). So runs
# differ ONLY in reference duration, which is what makes the comparison valid.
#
# Each run is a paid GPU generation (~$0.03). Audio lands in pilot/audio_ref<N>/.
#
set -euo pipefail
cd "$(dirname "$0")/.."

SECONDS_VARIANT="${1:-}"
case "$SECONDS_VARIANT" in
  5|10|15|20|30) ;;
  *) echo "usage: $0 {5|10|15|20|30}"; exit 2 ;;
esac

green() { printf "\033[32m%s\033[0m\n" "$1"; }
step()  { printf "\n\033[1m== %s\033[0m\n" "$1"; }

DEST="pilot/refs_vivos${SECONDS_VARIANT}"
AUDIO="pilot/audio_ref${SECONDS_VARIANT}"

step "1/6  Building the ${SECONDS_VARIANT}s reference pool"
if [ -d "$DEST/processed_audio_by_id" ]; then
  green "  already built — reusing $DEST"
else
  python3 cli.py --config pilot/pilot.yaml build-refs \
    --dest "$DEST" --target-seconds "$SECONDS_VARIANT"
fi

step "2/6  Pointing pilot.yaml at the ${SECONDS_VARIANT}s variant"
# Edited via yaml round-trip rather than sed so a malformed config fails loudly here
# instead of surfacing as a mysterious container error later.
python3 - "$SECONDS_VARIANT" <<'PY'
import sys, re, pathlib
n = sys.argv[1]
p = pathlib.Path("pilot/pilot.yaml"); s = p.read_text()
s = re.sub(r'^  dir: ".*"(.*)$', f'  dir: "/refs/vivos/v{n}"\\1', s, count=1, flags=re.M)
s = re.sub(r'^  target_seconds: \d+$', f'  target_seconds: {n}', s, count=1, flags=re.M)
p.write_text(s)
import yaml
refs = yaml.safe_load(s)["refs"]
assert refs["target_seconds"] == int(n), refs
assert refs["dir"].endswith(f"/v{n}"), refs
print(f"  refs.dir={refs['dir']}  refs.target_seconds={refs['target_seconds']}")
PY

step "3/6  Uploading the variant (skipped if already on the Volume)"
if modal volume ls vivos-refs "/v${SECONDS_VARIANT}/processed_audio_by_id" >/dev/null 2>&1; then
  green "  /v${SECONDS_VARIANT} already uploaded"
else
  modal volume put vivos-refs "$DEST/processed_audio_by_id" \
    "/v${SECONDS_VARIANT}/processed_audio_by_id"
fi

step "4/6  Replanning"
# target_seconds is part of the plan hash, so each variant gets a distinct hash and
# the container cannot silently reuse another variant's plan.
python3 cli.py --config pilot/pilot.yaml plan \
  --manifest pilot/manifest.parquet \
  --visec "$DEST/processed_audio_by_id/metadata.csv" \
  --out pilot/shard_plan.parquet --rejects pilot/rejects.jsonl

step "5/6  Clearing the target repo and running (PAID)"
# The published shard path is the same for every variant, so the previous run must
# be removed or remaining_targets reports "nothing to do".
python3 - <<'PY'
from huggingface_hub import HfApi
api = HfApi()
for f in sorted(api.list_repo_files("npat1509/TestSynth", repo_type="dataset")):
    if f != ".gitattributes":
        api.delete_file(path_in_repo=f, repo_id="npat1509/TestSynth",
                        repo_type="dataset", commit_message=f"sweep: clear {f}")
        print("  deleted", f)
PY
./pilot/run_pilot.sh setup   >/dev/null
./pilot/run_pilot.sh generate --yes 2>&1 | grep -E '^ready:|"shard_id"|^done:'

step "6/6  Extracting audio to $AUDIO/"
python3 - "$SECONDS_VARIANT" <<'PY'
import sys, pathlib, shutil
import pyarrow.parquet as pq
from huggingface_hub import HfApi
n = sys.argv[1]
t = pq.read_table(HfApi().hf_hub_download(
    "npat1509/TestSynth", "data/vietnamese/train-00000-of-00001.parquet",
    repo_type="dataset"))
out = pathlib.Path(f"pilot/audio_ref{n}")
if out.exists(): shutil.rmtree(out)
out.mkdir(parents=True)
for r in t.to_pylist():
    f = out / r["audio"]["path"]; f.parent.mkdir(parents=True, exist_ok=True)
    f.write_bytes(r["audio"]["bytes"])
print(f"  wrote {t.num_rows} files")
PY

green ""
green "Variant ${SECONDS_VARIANT}s done -> $AUDIO/"
