# cli.py
"""Local, GPU-free commands for the Meddies TTS pipeline."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pyarrow.parquet as pq

from meddies_tts.config import ConfigError, load_config
from meddies_tts.hub import (
    HubError,
    PlanDriftError,
    check_plan_drift,
    list_repo_paths,
    preflight,
    remaining_targets,
    shard_targets,
)
from meddies_tts.manifest import build_manifest, read_manifest, write_manifest
from meddies_tts.plan import (
    build_plan,
    compute_plan_hash,
    read_plan,
    shard_totals,
    write_plan,
)
from meddies_tts.qc import DEFAULT_CHARS_PER_SEC
from meddies_tts.speakers import load_pool

# Modal A100-40GB, USD/sec, verified against modal.com/pricing
_A100_USD_PER_SEC = 0.000583
# Aggregate realtime multiple at concurrency 48 on one GPU (spec §1, Estimated outputs)
_AGGREGATE_SPEEDUP = 70.0
# 16 kHz 16-bit FLAC, bytes per second of audio (spec §6)
_FLAC_BYTES_PER_SEC = 19_000

# Exit codes: ConfigError is a distinct case (2) from every other failure so a
# wrapper script can tell "fix your config" from "something at runtime broke".
# Drift gets its own code (3) because it is a deliberate, designed refusal
# (see meddies_tts.hub.check_plan_drift), not an accident -- a caller should be
# able to distinguish "the plan changed under you" from a generic error.
_EXIT_CONFIG_ERROR = 2
_EXIT_PLAN_DRIFT = 3
_EXIT_ERROR = 1


def _build_parser() -> argparse.ArgumentParser:
    """Build the top-level argument parser with all subcommands attached."""
    parser = argparse.ArgumentParser(prog="cli.py", description=__doc__)
    parser.add_argument("--config", default="config.yaml", help="path to config.yaml")
    parser.add_argument("--hf-repo", default=None, help="override hf.repo_id")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("build-manifest", help="flatten output_full/ into manifest.parquet")
    p.add_argument("--output-root", required=True)
    p.add_argument("--out", required=True)

    p = sub.add_parser("plan", help="normalize, reject, assign speakers, pack shards")
    p.add_argument("--manifest", required=True)
    p.add_argument("--visec", required=True, help="path to ViSEC metadata.csv")
    p.add_argument("--out", required=True)
    p.add_argument("--rejects", required=True)

    p = sub.add_parser("preflight", help="verify HF token, repo and write access")

    p = sub.add_parser("estimate", help="project GPU-hours, cost and storage")
    p.add_argument("--plan", required=True)
    p.add_argument("--chars-per-sec", type=float, default=DEFAULT_CHARS_PER_SEC)

    p = sub.add_parser("status", help="report done/remaining shards against the Hub")
    p.add_argument("--plan", required=True)

    p = sub.add_parser("show-config", help="print the resolved configuration")

    p = sub.add_parser("materialize-tree", help="rebuild the output_full tree from a shard")
    p.add_argument("--shard", required=True)
    p.add_argument("--dest", required=True)

    return parser


def _cmd_build_manifest(args, cfg) -> int:
    """Flatten output_full/ into a manifest.parquet (Stage 0)."""
    table = build_manifest(Path(args.output_root), cfg.run.configs)
    write_manifest(table, Path(args.out))
    print(f"manifest: {table.num_rows:,} utterances -> {args.out}")
    return 0


def _cmd_plan(args, cfg) -> int:
    """Normalize, reject, assign speakers and pack shards (Stage 1)."""
    manifest = read_manifest(Path(args.manifest))
    pool = load_pool(Path(args.visec))
    plan, rejects = build_plan(manifest, cfg, pool)

    write_plan(plan, Path(args.out))
    with Path(args.rejects).open("w", encoding="utf-8") as handle:
        for record in rejects:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    plan_hash = compute_plan_hash(plan, cfg)
    Path(args.out).with_suffix(".hash").write_text(plan_hash, encoding="utf-8")
    print(
        f"plan: {plan.num_rows:,} utterances, {sum(shard_totals(plan).values())} shards, "
        f"{len(rejects):,} rejected -> {args.out} (hash {plan_hash})"
    )
    return 0


def _cmd_preflight(args, cfg) -> int:
    """Verify the HF token, repo existence and write access before any GPU is requested."""
    from huggingface_hub import HfApi  # imported lazily so `estimate` stays offline-safe

    preflight(HfApi(), cfg.hf.repo_id, cfg.hf.private)
    print(f"preflight OK: {cfg.hf.repo_id} is writable")
    return 0


def _cmd_estimate(args, cfg) -> int:
    """Project GPU-hours, USD cost and storage for a plan, offline."""
    plan = read_plan(Path(args.plan))
    chars = sum(len(text) for text in plan.column("text_spoken").to_pylist())
    audio_sec = chars / args.chars_per_sec
    gpu_sec = audio_sec / _AGGREGATE_SPEEDUP
    print(f"utterances : {plan.num_rows:,}")
    print(f"shards     : {sum(shard_totals(plan).values()):,}")
    print(f"audio      : {audio_sec / 3600:,.1f} h  (at {args.chars_per_sec} chars/sec)")
    print(f"GPU-hours  : {gpu_sec / 3600:,.1f}")
    print(f"cost       : {gpu_sec * _A100_USD_PER_SEC:,.2f} USD  (A100-40GB)")
    print(f"storage    : {audio_sec * _FLAC_BYTES_PER_SEC / 1e9:,.1f} GB  (16 kHz FLAC)")
    return 0


def _cmd_status(args, cfg) -> int:
    """Report done/remaining shards against the Hub, refusing on plan drift."""
    from huggingface_hub import HfApi  # imported lazily so `estimate` stays offline-safe

    plan = read_plan(Path(args.plan))
    local_hash = Path(args.plan).with_suffix(".hash").read_text(encoding="utf-8").strip()
    api = HfApi()
    for config in cfg.run.configs:
        check_plan_drift(api, cfg.hf.repo_id, config, local_hash)
    existing = list_repo_paths(api, cfg.hf.repo_id)
    total = len(shard_targets(plan))
    remaining = remaining_targets(plan, existing)
    print(f"plan hash : {local_hash}")
    print(f"shards    : {total}")
    print(f"done      : {total - len(remaining)}")
    print(f"remaining : {len(remaining)}")
    return 0


def _cmd_show_config(args, cfg) -> int:
    """Print the resolved configuration (post --hf-repo override) as JSON."""
    print(json.dumps({"repo_id": cfg.hf.repo_id, "configs": list(cfg.run.configs)}, indent=2))
    return 0


def _resolve_inside(dest: Path, dest_resolved: Path, rel_path: str) -> Path:
    """Resolve rel_path against dest, raising if it is absolute or escapes dest.

    A shard is untrusted input by construction -- it can come straight from
    the Hub -- so audio.path must never be trusted to stay inside dest.
    pathlib silently drops the left operand when joined with an absolute
    path (Path("/a/dest") / "/etc/x" == Path("/etc/x")), so an absolute path
    is rejected outright before any join happens.
    """
    if Path(rel_path).is_absolute():
        raise ValueError(f"shard is malformed: audio.path is absolute: {rel_path!r}")
    target = (dest / rel_path).resolve()
    if not target.is_relative_to(dest_resolved):
        raise ValueError(f"shard is malformed: audio.path escapes --dest: {rel_path!r}")
    return target


def _cmd_materialize_tree(args, cfg) -> int:
    """Rebuild the output_full-shaped tree from a shard's embedded audio.path fields."""
    table = pq.read_table(Path(args.shard))
    dest = Path(args.dest)
    # resolve(strict=False): dest need not exist yet, this only normalizes the path.
    dest_resolved = dest.resolve()
    written = 0
    for record in table.column("audio").to_pylist():
        target = _resolve_inside(dest, dest_resolved, record["path"])
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(record["bytes"])
        written += 1
    print(f"materialized {written} files under {dest}")
    return 0


_COMMANDS = {
    "build-manifest": _cmd_build_manifest,
    "plan": _cmd_plan,
    "preflight": _cmd_preflight,
    "estimate": _cmd_estimate,
    "status": _cmd_status,
    "show-config": _cmd_show_config,
    "materialize-tree": _cmd_materialize_tree,
}


def main(argv: list[str] | None = None) -> int:
    """Entry point: parse args, resolve config, dispatch to the requested subcommand."""
    args = _build_parser().parse_args(argv)
    try:
        cfg = load_config(Path(args.config), {"hf.repo_id": args.hf_repo})
    except ConfigError as error:
        print(f"error: {error}", file=sys.stderr)
        return _EXIT_CONFIG_ERROR

    # Every command below can hit an expected, operator-actionable failure (a
    # missing file, a Hub problem, a malformed shard, drifted state). None of
    # those should surface as a raw traceback -- an operator running `status`
    # against a fresh repo, or a drifted plan, should see a clear refusal.
    try:
        return _COMMANDS[args.command](args, cfg)
    except PlanDriftError as error:
        print(f"error: {error}", file=sys.stderr)
        return _EXIT_PLAN_DRIFT
    except HubError as error:
        print(f"error: {error}", file=sys.stderr)
        return _EXIT_ERROR
    except FileNotFoundError as error:
        missing = error.filename or str(error)
        print(f"error: file not found: {missing}", file=sys.stderr)
        return _EXIT_ERROR
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return _EXIT_ERROR


if __name__ == "__main__":
    raise SystemExit(main())
