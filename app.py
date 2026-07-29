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
    async def run_shard(self, shard_id: str, repo_path: str) -> dict:
        """Synthesize one shard, write it to Parquet, upload it, then delete the local copy."""
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

    for config in cfg.run.configs:
        upload_bytes(api, cfg.hf.repo_id, plan_hash.encode(), plan_hash_path(config))

    print(f"dispatching {len(targets)} shard(s) to {cfg.run.gpu}")
    synth = Synthesizer()
    total_audio = 0.0
    for outcome in synth.run_shard.starmap(targets):
        total_audio += outcome.get("audio_seconds") or 0.0
        print(json.dumps(outcome, ensure_ascii=False))
    print(f"done: {total_audio / 3600:.2f} h of audio generated")
