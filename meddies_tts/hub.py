# meddies_tts/hub.py
from __future__ import annotations

import io
from pathlib import Path

import pyarrow as pa

from meddies_tts.plan import shard_repo_path, shard_totals

_REPO_TYPE = "dataset"
_PROBE_PATH = ".meddies_tts_preflight"


class HubError(RuntimeError):
    """Raised when the Hub is unusable for this run."""


class PlanDriftError(RuntimeError):
    """Raised when the local plan disagrees with what produced the published shards."""


def plan_path(config: str) -> str:
    """Repo path where a config's shard plan (the full row-level table) is published."""
    return f"plan/shard_plan-{config}.parquet"


def plan_hash_path(config: str) -> str:
    """Repo path where a config's plan hash is published, for drift detection."""
    return f"plan/plan_hash-{config}.txt"


def preflight(api, repo_id: str, private: bool = False) -> None:
    """Verify token, repo and write access before any GPU is requested."""
    try:
        api.whoami()
    except Exception as error:  # noqa: BLE001
        raise HubError(
            f"Hugging Face token is missing or invalid ({error}). Check the Modal "
            "Secret named by hf.token_secret."
        ) from error

    if not api.repo_exists(repo_id, repo_type=_REPO_TYPE):
        try:
            api.create_repo(repo_id, repo_type=_REPO_TYPE, private=private, exist_ok=True)
        except Exception as error:  # noqa: BLE001
            raise HubError(f"cannot create dataset repo {repo_id!r}: {error}") from error

    # A token can carry a "write" scope yet still be rejected by the repo (wrong org,
    # revoked collaborator access, etc). The only way to know it truly works is to
    # perform a real upload and clean it up again, rather than trust the scope claim.
    try:
        api.upload_file(
            path_or_fileobj=io.BytesIO(b"preflight"),
            path_in_repo=_PROBE_PATH,
            repo_id=repo_id,
            repo_type=_REPO_TYPE,
        )
    except Exception as error:  # noqa: BLE001
        raise HubError(
            f"token lacks write access to {repo_id!r}: {error}. A read-scoped token "
            "would only fail after a shard had already been generated."
        ) from error

    # Cleanup failing is not fatal — the upload above already proved write access —
    # but it must not leak a raw exception past the HubError contract (callers in
    # Tasks 14/16 catch HubError specifically), so failure is swallowed and surfaced
    # as a visible warning instead of a stray, invisible probe file on the repo.
    try:
        api.delete_file(path_in_repo=_PROBE_PATH, repo_id=repo_id, repo_type=_REPO_TYPE)
    except Exception as error:  # noqa: BLE001
        print(f"warning: could not delete preflight probe {_PROBE_PATH!r} from {repo_id!r}: {error}")

    list_repo_paths(api, repo_id)


def list_repo_paths(api, repo_id: str) -> set[str]:
    """One call, not one per shard — this is what resumption diffs against."""
    try:
        return set(api.list_repo_files(repo_id, repo_type=_REPO_TYPE))
    except Exception as error:  # noqa: BLE001
        raise HubError(f"cannot list files in {repo_id!r}: {error}") from error


def shard_targets(plan: pa.Table) -> list[tuple[str, str]]:
    """Every (shard_id, repo_path) the plan expects, in shard order."""
    totals = shard_totals(plan)
    seen: dict[str, str] = {}
    for config, sid in zip(
        plan.column("config").to_pylist(), plan.column("shard_id").to_pylist()
    ):
        if sid in seen:
            continue
        index = int(sid.split("-")[1])
        seen[sid] = shard_repo_path(config, index, totals[config])
    return [(sid, seen[sid]) for sid in sorted(seen)]


def remaining_targets(plan: pa.Table, existing: set[str]) -> list[tuple[str, str]]:
    """Shard targets not yet present on the Hub, i.e. what a resumed run still owes."""
    return [(sid, path) for sid, path in shard_targets(plan) if path not in existing]


def _unreadable_message(repo_id: str, path_in_repo: str, error: Exception) -> str:
    return (
        f"could not read {path_in_repo!r} from {repo_id!r}: {error}. Drift status is "
        "unknown, so the run refuses rather than silently proceeding."
    )


def read_text(api, repo_id: str, path_in_repo: str) -> str | None:
    """Fetch a small text file from the repo; None means confirmed absent, not "unknown"."""
    # Imported lazily so callers that only need the pure planning helpers never pay
    # for importing huggingface_hub.
    from huggingface_hub.errors import EntryNotFoundError, HfHubHTTPError, RepositoryNotFoundError

    try:
        local = api.hf_hub_download(repo_id, path_in_repo, repo_type=_REPO_TYPE)
    # A 404 is the only case that means "no published hash yet, first run" and may
    # be treated as absent. Anything else (a network blip, a 5xx, ...) must NOT be
    # folded into that same None, or a transient failure would silently disable
    # drift detection and let a resumed run dispatch against a drifted plan.
    except (EntryNotFoundError, RepositoryNotFoundError):
        return None
    except HfHubHTTPError as error:
        if getattr(error.response, "status_code", None) == 404:
            return None
        raise HubError(_unreadable_message(repo_id, path_in_repo, error)) from error
    except Exception as error:  # noqa: BLE001 - not a confirmed absence, so don't guess
        raise HubError(_unreadable_message(repo_id, path_in_repo, error)) from error
    return Path(local).read_text(encoding="utf-8").strip()


def check_plan_drift(api, repo_id: str, config: str, local_hash: str) -> None:
    """Refuse to dispatch when the local plan differs from the published one."""
    remote = read_text(api, repo_id, plan_hash_path(config))
    if remote is None or remote == local_hash:
        return
    raise PlanDriftError(
        f"plan hash mismatch for config {config!r}: published shards were produced by "
        f"plan {remote}, local plan is {local_hash}. Re-planning changed the work "
        "partition; dispatching now would write incompatible shards alongside the old "
        "ones. Restore the published plan, or start a fresh repo."
    )


def upload_bytes(api, repo_id: str, data: bytes, path_in_repo: str) -> None:
    """Upload an in-memory byte string to a repo path."""
    api.upload_file(
        path_or_fileobj=io.BytesIO(data),
        path_in_repo=path_in_repo,
        repo_id=repo_id,
        repo_type=_REPO_TYPE,
    )


def upload_path(api, repo_id: str, local_path: Path, path_in_repo: str) -> None:
    """Upload a local file to a repo path."""
    api.upload_file(
        path_or_fileobj=str(local_path),
        path_in_repo=path_in_repo,
        repo_id=repo_id,
        repo_type=_REPO_TYPE,
    )
