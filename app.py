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
# Modal needs the GPU tier at decoration time (see @app.cls below), before
# config.yaml is even loaded -- that only happens inside @modal.enter(), on the
# GPU container itself. So the allocation is sourced from the environment, not
# from cfg.run.gpu, and this constant is the SINGLE source of truth: it's what
# gets requested, what's embedded in shard provenance, and what's printed at
# dispatch. Two sources of truth here would let an operator who edits
# config.yaml but forgets MEDDIES_GPU publish a dataset whose own audit trail
# names the wrong hardware.
_GPU = os.environ.get("MEDDIES_GPU", "A100-40GB")

image = (
    # A CUDA "devel" base is required, not debian_slim: flash-attn compiles CUDA
    # kernels from source under --no-build-isolation, which needs nvcc and a C/C++
    # toolchain that debian_slim's minimal apt set does not provide.
    modal.Image.from_registry("nvidia/cuda:12.4.1-devel-ubuntu22.04", add_python="3.11")
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
    gpu=_GPU,
    volumes={"/weights": weights_vol, PLAN_DIR: plan_vol, REFS_DIR: refs_vol},
    secrets=[hf_secret],
    timeout=7200,
    max_containers=20,
)
class Synthesizer:
    @modal.enter()
    async def load(self) -> None:
        """Load the engine and encode every reference speaker once per container.

        This runs once when the container boots, not once per utterance. The
        shard (~1,500 utterances) is the unit of work specifically so this
        amortized cost -- engine load plus 147 reference encodings -- only
        happens once per ~1,500 syntheses instead of once each.
        """
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
    async def run_shard(self, shard_id: str, repo_path: str, expected_plan_hash: str) -> dict:
        """Synthesize one shard, write it to Parquet, upload it, then delete the local copy.

        Never raises: main()'s dispatch loop uses Modal's .starmap over every target
        shard, and a bare exception here (Modal's default is return_exceptions=False)
        would silently abort every not-yet-dispatched shard rather than just this one.
        Every failure mode below degrades to a returned "status": "error" outcome.
        """
        import time

        from meddies_tts.hub import upload_path
        from meddies_tts.runner import run_shard as run
        from meddies_tts.writer import write_shard

        try:
            # Guards against a stale Modal Volume: the plan this container loaded at
            # boot (self.plan_hash) must match the plan main() dispatched against, or
            # rows would be written under a shard/path partition that no longer
            # matches what's actually on the volume, with no error anywhere else.
            if expected_plan_hash != self.plan_hash:
                return {
                    "shard_id": shard_id,
                    "status": "error",
                    "error": (
                        f"plan hash mismatch: dispatcher={expected_plan_hash} "
                        f"volume={self.plan_hash}"
                    ),
                }

            started = time.time()
            rows = [r for r in self.plan.to_pylist() if r["shard_id"] == shard_id]
            built, result = await run(shard_id, rows, self.engine, self.refs, self.cfg)
            if not built:
                return {"shard_id": shard_id, "status": "empty", "failed": result.n_failed}

            local = Path(f"/tmp/{shard_id}.parquet")
            try:
                write_shard(built, local, self.plan_hash, json.dumps({"gpu": _GPU}))
                # Atomic by construction: nothing is uploaded until the whole shard is written.
                upload_path(self.api, self.cfg.hf.repo_id, local, repo_path)
            finally:
                # Removed on both the success and failure path -- containers are
                # reused across shards, so a file left behind by a failed upload
                # would leak disk for the rest of that container's life.
                local.unlink(missing_ok=True)

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
        except Exception as error:  # noqa: BLE001 - converted to a result, see docstring
            return {
                "shard_id": shard_id,
                "status": "error",
                "error": f"{type(error).__name__}: {error}",
            }


@app.local_entrypoint()
def main(shards: str = "remaining", config_path: str = "config.yaml",
         plan_path: str = "shard_plan.parquet", limit: int = 0) -> None:
    """Dispatch shards to the GPU: preflight, check drift, diff against what's published."""
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

    # One listing call for the whole repo, diffed locally against every shard the plan
    # expects -- this is what lets "remaining" resume cheaply instead of a per-shard probe.
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

    print(f"dispatching {len(targets)} shard(s) to {_GPU}")
    synth = Synthesizer()
    # Each call also carries the dispatcher's plan_hash, so the container can refuse
    # (see Synthesizer.run_shard) rather than silently synthesize against a plan that
    # disagrees with what's on the Modal Volume.
    calls = [(shard_id, repo_path, plan_hash) for shard_id, repo_path in targets]
    total_audio = 0.0
    # The plan hash is published to the Hub only after a config's FIRST shard actually
    # lands "ok" -- not up front. Publishing before any shard exists would leave
    # provenance for zero data if the run died on shard one, and a later legitimate
    # re-plan would then trip PlanDriftError against a hash that never produced anything.
    hash_published: set[str] = set()
    outcomes = synth.run_shard.starmap(calls, return_exceptions=True)
    for (shard_id, repo_path, _), outcome in zip(calls, outcomes):
        if isinstance(outcome, Exception):
            # Modal itself failed to deliver a result (e.g. a container crash), rather
            # than the application-level failure Synthesizer.run_shard already converts
            # to a "status": "error" dict. Either way, one shard's failure must not stop
            # the rest of the dispatch loop.
            outcome = {
                "shard_id": shard_id,
                "status": "error",
                "error": f"{type(outcome).__name__}: {outcome}",
            }
        if outcome.get("status") == "ok":
            config = repo_path.split("/")[1]  # "data/<config>/train-...parquet"
            if config not in hash_published:
                upload_bytes(api, cfg.hf.repo_id, plan_hash.encode(), plan_hash_path(config))
                hash_published.add(config)
        total_audio += outcome.get("audio_seconds") or 0.0
        print(json.dumps(outcome, ensure_ascii=False))
    print(f"done: {total_audio / 3600:.2f} h of audio generated")
