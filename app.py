"""Modal application: one container per shard, generate -> parquet -> HF -> delete."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import modal

# Circuit breaker (Fix C4): if this many shards are dispatched FIRST and every one
# comes back non-"ok", the run is almost certainly systematically broken (e.g. a
# mis-set calibration value), not unlucky -- abort rather than keep burning GPU
# budget on the remaining shards. 5 is small enough to fail fast, large enough
# not to trip on a couple of genuinely bad shards in an otherwise healthy run.
_CIRCUIT_BREAKER_SHARDS = 5

APP_NAME = "meddies-tts"
MODEL_REPO = "openbmb/VoxCPM2"
MODEL_DIR = "/weights/VoxCPM2"
PLAN_DIR = "/plan"
# Both reference pools mount side by side and cfg.refs.dir selects one at
# runtime. Mounting both costs nothing when unused and means switching pools
# never requires re-uploading 50+ MB of WAVs to get back to where you were.
REFS_ROOT = "/refs"
# Modal needs the GPU tier at decoration time (see @app.cls below), before
# config.yaml is even loaded -- that only happens inside @modal.enter(), on the
# GPU container itself. So the allocation is sourced from the environment, not
# from cfg.run.gpu, and this constant is the SINGLE source of truth: it's what
# gets requested, what's embedded in shard provenance, and what's printed at
# dispatch. Two sources of truth here would let an operator who edits
# config.yaml but forgets MEDDIES_GPU publish a dataset whose own audit trail
# names the wrong hardware.
_GPU = os.environ.get("MEDDIES_GPU", "A100-40GB")

# Prebuilt flash-attn wheel. Every component of this filename is a compatibility
# constraint: cp311 must match add_python, torch2.8 must match the torch pin, cu12
# must match the CUDA base, and cxx11abiTRUE must match how that torch was built.
# Change any one of them and this must change too.
_FLASH_ATTN_WHEEL = (
    "https://github.com/Dao-AILab/flash-attention/releases/download/v2.8.3.post1/"
    "flash_attn-2.8.3.post1+cu12torch2.8cxx11abiTRUE-cp311-cp311-linux_x86_64.whl"
)

# Install order here is load-bearing and was established by a failed build, not by
# guesswork. nano-vllm-voxcpm declares `flash_attn` as a dependency, and flash-attn's
# setup.py imports torch to compute its own build requirements. So installing
# requirements-gpu.txt in one pass makes pip try to build flash_attn under build
# isolation before torch exists -> "ModuleNotFoundError: No module named 'torch'".
# Each pip_install below is therefore a separate layer, in dependency order.
image = (
    # A CUDA "devel" base is required, not debian_slim: flash-attn compiles CUDA
    # kernels from source under --no-build-isolation, which needs nvcc and a C/C++
    # toolchain that debian_slim's minimal apt set does not provide. 12.9.0 matches
    # a production Modal image known to build torch/flash-attn successfully, and
    # pairs with the cu128 wheels below.
    modal.Image.from_registry("nvidia/cuda:12.9.0-devel-ubuntu22.04", add_python="3.11")
    # CUDA base images ship their own ENTRYPOINT, which can interfere with how
    # Modal starts the container process. Clearing it is a known-safe pattern
    # from a working production Modal setup on the same kind of CUDA devel base.
    .entrypoint([])
    # build-essential because the CUDA devel image ships nvcc but NO C++ host
    # compiler -- an hour-long flash-attn build died on "clang++ not found".
    # flash-attn now comes from a prebuilt wheel, but anything else that needs
    # to compile a C extension would hit the same wall.
    .apt_install("git", "ffmpeg", "build-essential")
    # 1. torch alone, first, pinned to a build compiled for the SAME CUDA as the
    #    base image. This must use index_url, not extra_index_url: extra_index_url
    #    is additive, so PyPI still wins and supplies a torch compiled for CUDA
    #    13.0, which then fails flash-attn's build with
    #    "detected CUDA version (12.9) mismatches ... PyTorch (13.0)".
    #    extra_index_url then points back at PyPI so torch's own pure-Python
    #    dependencies (sympy, networkx, filelock, ...) still resolve.
    #    cu128 wheels pair with the 12.9 base; nano-vllm-voxcpm needs
    #    torch!=2.6.*,>=2.5.0, and cu124 tops out at 2.6.0, so cu128 is required. Pinned to 2.8.0
    #    because that is the torch version the prebuilt flash-attn wheel below
    #    was compiled against -- they must match exactly.
    .pip_install(
        # The whole torch family must come from ONE CUDA index and be version-matched.
        # Installed separately, pip takes torchaudio/torchcodec from PyPI, which now
        # ships CUDA-13 builds -- they import fine until a compiled op loads, then
        # fail with "libcudart.so.13: cannot open shared object file".
        "torch==2.8.0",
        "torchaudio==2.8.0",
        "torchcodec==0.7.0",
        index_url="https://download.pytorch.org/whl/cu128",
        extra_index_url="https://pypi.org/simple",
    )
    # 2. flash-attn from a PREBUILT wheel, not from source.
    #    Building it from source took over an hour and then failed at link time with
    #    "command 'clang++' failed: No such file or directory" -- the CUDA devel image
    #    ships nvcc but no C++ host compiler. Rather than add build-essential and pay
    #    the compile cost on every cache miss, use the wheel upstream already built.
    #    The wheel encodes cp311 + torch2.8 + cu12 + a C++ ABI flag, and ALL of those
    #    must match this image: hence add_python="3.11" and torch pinned to 2.8.0.
    #    Installed BEFORE nano-vllm-voxcpm so its flash_attn dependency is already
    #    satisfied and never triggers a source build.
    .pip_install(_FLASH_ATTN_WHEEL)
    # Fail fast if the ABI flag is wrong: a mismatch shows up as an ImportError on
    # the compiled extension. Catching it here costs seconds; catching it at run
    # time costs a container boot on a paid GPU.
    .run_commands("python -c 'import flash_attn; print(\"flash_attn\", flash_attn.__version__)'")
    # 3. the CPU-side dependencies shared with local development
    .pip_install_from_requirements("requirements.txt")
    # 4. finally the GPU stack, whose heavy build-time dependencies now all exist
    .pip_install_from_requirements("requirements-gpu.txt")
    # Import the whole GPU stack at BUILD time. nano-vllm-voxcpm pulls torchaudio
    # and torchcodec from PyPI with no torch pin, so pip is free to install versions
    # compiled against a different torch than the one pinned above -- a mismatch that
    # only shows up when a compiled extension is imported. Catching that here costs
    # seconds on a builder; catching it in @modal.enter() costs a boot on a paid GPU.
    .run_commands(
        "python -c 'import torch, torchaudio, torchcodec, flash_attn, nanovllm_voxcpm; "
        "print(\"stack OK torch\", torch.__version__, \"cuda\", torch.version.cuda)'"
    )
    .env({"HF_HUB_ENABLE_HF_TRANSFER": "1"})
    .add_local_python_source("meddies_tts")
)

app = modal.App(APP_NAME)
weights_vol = modal.Volume.from_name("voxcpm2-weights", create_if_missing=True)
plan_vol = modal.Volume.from_name("meddies-tts-plan", create_if_missing=True)
visec_vol = modal.Volume.from_name("visec-refs", create_if_missing=True)
vivos_vol = modal.Volume.from_name("vivos-refs", create_if_missing=True)
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
    volumes={"/weights": weights_vol, PLAN_DIR: plan_vol,
             f"{REFS_ROOT}/visec": visec_vol, f"{REFS_ROOT}/vivos": vivos_vol},
    secrets=[hf_secret],
    timeout=7200,
    max_containers=20,
    # Precautionary bound, not a measured one: @modal.enter() below loads a 2B
    # model AND runs 147 encode_reference calls before the container is ready,
    # well beyond a default startup budget. The pilot should record actual boot
    # time on real hardware so this can be tightened.
    startup_timeout=20 * 60,
    # Keeps a container warm between shards so consecutive shards reuse one
    # already-loaded engine instead of reloading the 2B model and re-encoding
    # all 147 references from scratch (~12 min/shard means a 15-min idle window
    # comfortably covers the gap to the next shard). This is what makes the
    # shard-as-unit-of-work amortization in @modal.enter() actually pay off
    # across MULTIPLE shards on one container, not just within one.
    scaledown_window=15 * 60,
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
        from meddies_tts.hub import preflight
        from meddies_tts.plan import read_plan
        from meddies_tts.speakers import load_pool

        self.cfg = load_config(Path(f"{PLAN_DIR}/config.yaml"))
        self.plan = read_plan(Path(f"{PLAN_DIR}/shard_plan.parquet"))
        # {config: hash} — one hash per config (Fix I2), not one for the whole plan
        # file, so an unrelated config's shards can never trip drift detection here.
        self.plan_hashes = json.loads(Path(f"{PLAN_DIR}/shard_plan.hash").read_text())
        self.api = HfApi()

        # Prove THIS container's token can actually write, before spending any GPU.
        # main()'s preflight runs on the dispatching machine with the developer's own
        # token; the container authenticates with the Modal Secret instead, so the two
        # can disagree -- and did: a local "preflight OK" was followed by a 401 that
        # discarded a fully generated shard, because upload only happens after run().
        # Running it here, before the engine load, turns that into a boot-time failure.
        preflight(self.api, self.cfg.hf.repo_id, self.cfg.hf.private)

        # Load the engine ONCE per container — this is what makes the shard-as-work-unit
        # design pay for itself across ~1,500 utterances.
        self.engine = await VoxCPMEngine.create(MODEL_DIR, self.cfg.engine)

        # Encode all 147 references ONCE, not per utterance.
        pool = load_pool(Path(self.cfg.refs.dir) / "processed_audio_by_id" / "metadata.csv")
        self.refs = {
            speaker.speaker_id: await self.engine.encode_reference(
                Path(speaker.wav_path).read_bytes()
            )
            for speaker in pool
        }
        print(f"ready: engine={self.engine.version} refs={len(self.refs)} "
              f"source={self.cfg.refs.source} sample_rate={self.engine.sample_rate}")

    @modal.exit()
    async def shutdown(self) -> None:
        """Release the engine's GPU resources when the container is torn down.

        engine.close() existed but was never called anywhere -- dead code that
        left the underlying nano-vllm-voxcpm server process (and its GPU
        memory) alive until the container itself was killed. Guarded on both
        sides: getattr in case @modal.enter() failed before self.engine was
        ever assigned, and the try/except because a teardown-path failure here
        must never mask whatever error (if any) actually ended the container.
        """
        engine = getattr(self, "engine", None)
        if engine is None:
            return
        try:
            await engine.close()
        except Exception as error:  # noqa: BLE001 - teardown must not raise
            print(f"warning: engine.close() failed during shutdown: {error}")

    @modal.method()
    async def run_shard(self, shard_id: str, repo_path: str, expected_plan_hash: str) -> dict:
        """Synthesize one shard, write it to Parquet, upload it, then delete the local copy.

        Never raises: main()'s dispatch loop uses Modal's .starmap over every target
        shard, and a bare exception here (Modal's default is return_exceptions=False)
        would silently abort every not-yet-dispatched shard rather than just this one.
        Every failure mode below degrades to a returned "status": "error" outcome.
        """
        import time

        import pyarrow.compute as pc

        from meddies_tts.hub import upload_path
        from meddies_tts.runner import run_shard as run
        from meddies_tts.writer import write_shard

        try:
            config = repo_path.split("/")[1]  # "data/<config>/train-...parquet"
            local_hash = self.plan_hashes.get(config)
            # Guards against a stale Modal Volume: the plan this container loaded at
            # boot (local_hash, for THIS shard's config) must match the hash main()
            # dispatched against, or rows would be written under a shard/path
            # partition that no longer matches what's actually on the volume, with
            # no error anywhere else.
            if expected_plan_hash != local_hash:
                return {
                    "shard_id": shard_id,
                    "status": "error",
                    "error": (
                        f"plan hash mismatch for config {config!r}: "
                        f"dispatcher={expected_plan_hash} volume={local_hash}"
                    ),
                }

            started = time.time()
            # Filter the Arrow table BEFORE materializing to Python dicts: to_pylist()
            # on the full ~711k-row plan costs ~4.3s and +1.7GB RSS per call, x473 shard
            # dispatches, if done first. pc.equal + .filter narrows to this shard's
            # ~1,500 rows in Arrow (~0.02s) before the (much cheaper) per-row conversion.
            mask = pc.equal(self.plan.column("shard_id"), shard_id)
            rows = self.plan.filter(mask).to_pylist()
            # cfg.text.chars_per_sec is what the Task 17 pilot calibrates -- without
            # threading it through here, QC silently falls back to runner's hardcoded
            # DEFAULT_CHARS_PER_SEC (14.0) for every verdict, regardless of config.yaml.
            built, result = await run(
                shard_id, rows, self.engine, self.refs, self.cfg,
                chars_per_sec=self.cfg.text.chars_per_sec,
            )
            if not built:
                return {"shard_id": shard_id, "status": "empty", "failed": result.n_failed}

            local = Path(f"/tmp/{shard_id}.parquet")
            try:
                # Everything that determines what this shard's audio actually
                # sounds/reads like, plus what hardware made it and the plan hash
                # that pins the work identity -- without seed_salt here the
                # published "seed" column is unreproducible from the shard alone.
                provenance = json.dumps({
                    "gpu": _GPU,
                    "seed_salt": self.cfg.speaker.seed_salt,
                    "refs_source": self.cfg.refs.source,
                    "refs_target_seconds": self.cfg.refs.target_seconds,
                    "speaker_policy": self.cfg.speaker.policy,
                    "text_chunk_max_chars": self.cfg.text.chunk_max_chars,
                    "text_chunk_overflow_chars": self.cfg.text.chunk_overflow_chars,
                    "text_chars_per_sec": self.cfg.text.chars_per_sec,
                    "text_silence_ms": self.cfg.text.silence_ms,
                    "engine_cfg_value": self.cfg.engine.cfg_value,
                    "engine_temperature": self.cfg.engine.temperature,
                    "engine_inference_timesteps": self.cfg.engine.inference_timesteps,
                    "plan_hash": local_hash,
                })
                write_shard(built, local, local_hash, provenance)
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
    # {config: hash} — see plan.compute_plan_hash's docstring for why this is
    # per-config rather than one hash for the whole plan file.
    hashes = json.loads(Path(plan_path).with_suffix(".hash").read_text(encoding="utf-8"))

    api = HfApi()
    preflight(api, cfg.hf.repo_id, cfg.hf.private)          # fails in seconds, not dollars
    for config in cfg.run.configs:
        check_plan_drift(api, cfg.hf.repo_id, config, hashes[config])

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
    # Each call also carries the dispatcher's hash for THAT shard's config, so the
    # container can refuse (see Synthesizer.run_shard) rather than silently
    # synthesize against a plan that disagrees with what's on the Modal Volume.
    calls = [(shard_id, repo_path, hashes[repo_path.split("/")[1]]) for shard_id, repo_path in targets]
    total_audio = 0.0
    # The plan hash is published to the Hub only after a config's FIRST shard actually
    # lands "ok" -- not up front. Publishing before any shard exists would leave
    # provenance for zero data if the run died on shard one, and a later legitimate
    # re-plan would then trip PlanDriftError against a hash that never produced anything.
    hash_published: set[str] = set()
    # ok/empty/error counts across the whole run (Fix C4) -- printed in the final
    # summary and what decides the process exit code, so a systematically failing
    # run can never again print "0.00 h generated" and exit 0.
    counts: dict[str, int] = {}

    def _dispatch(batch: list[tuple[str, str, str]]) -> list[dict]:
        """Run one batch of shards through Modal, printing/accounting each outcome."""
        nonlocal total_audio
        results = []
        for (shard_id, repo_path, _), outcome in zip(
            batch, synth.run_shard.starmap(batch, return_exceptions=True)
        ):
            if isinstance(outcome, Exception):
                # Modal itself failed to deliver a result (e.g. a container crash),
                # rather than the application-level failure Synthesizer.run_shard
                # already converts to a "status": "error" dict. Either way, one
                # shard's failure must not stop the rest of the dispatch loop.
                outcome = {
                    "shard_id": shard_id,
                    "status": "error",
                    "error": f"{type(outcome).__name__}: {outcome}",
                }
            status = outcome.get("status", "error")
            counts[status] = counts.get(status, 0) + 1
            if status == "ok":
                config = repo_path.split("/")[1]  # "data/<config>/train-...parquet"
                if config not in hash_published:
                    upload_bytes(api, cfg.hf.repo_id, hashes[config].encode(), plan_hash_path(config))
                    hash_published.add(config)
            total_audio += outcome.get("audio_seconds") or 0.0
            print(json.dumps(outcome, ensure_ascii=False))
            results.append(outcome)
        return results

    first_batch, rest = calls[:_CIRCUIT_BREAKER_SHARDS], calls[_CIRCUIT_BREAKER_SHARDS:]
    first_results = _dispatch(first_batch)
    # Only trip early if there was actually a full batch to judge AND more work
    # left to protect -- a short run (fewer than the threshold, or nothing left
    # after the first batch) falls through to the aggregate exit-code check below.
    if (
        rest
        and len(first_results) >= _CIRCUIT_BREAKER_SHARDS
        and all(r.get("status") != "ok" for r in first_results)
    ):
        print(
            f"aborting: the first {len(first_results)} dispatched shard(s) all "
            f"failed -- nothing is succeeding, refusing to burn the remaining "
            f"{len(rest)} shard(s)' GPU budget",
            file=sys.stderr,
        )
        sys.exit(1)
    if rest:
        _dispatch(rest)

    total = sum(counts.values())
    summary = " ".join(f"{status}={n}" for status, n in sorted(counts.items()))
    print(f"done: {total_audio / 3600:.2f} h of audio generated | {total} shard(s): {summary}")
    if counts.get("ok", 0) != total:
        sys.exit(1)
