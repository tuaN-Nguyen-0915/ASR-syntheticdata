# tests/tts/test_hub.py
import tempfile
from pathlib import Path

import pyarrow as pa
import pytest
from huggingface_hub.errors import EntryNotFoundError

from meddies_tts.hub import (
    HubError,
    PlanDriftError,
    check_plan_drift,
    list_repo_paths,
    plan_hash_path,
    plan_path,
    preflight,
    read_text,
    remaining_targets,
    shard_targets,
    upload_bytes,
)
from meddies_tts.plan import PLAN_SCHEMA


_UNSET = object()  # distinguishes "whoami not passed" from an explicit whoami=None (invalid token)
_PROBE_PATH = ".meddies_tts_preflight"  # kept in sync with meddies_tts.hub._PROBE_PATH


class FakeApi:
    def __init__(self, files=(), writable=True, exists=True, whoami=_UNSET,
                 delete_ok=True, remote_files=None, download_error=None):
        self.files = list(files)
        self._writable = writable
        self._exists = exists
        self._whoami = {"name": "tester"} if whoami is _UNSET else whoami
        self._delete_ok = delete_ok
        self._remote_files = dict(remote_files) if remote_files else {}
        self._download_error = download_error
        self.created = []
        self.uploaded = []
        self.deleted = []

    def whoami(self):
        if self._whoami is None:
            raise RuntimeError("invalid token")
        return self._whoami

    def repo_exists(self, repo_id, repo_type=None):
        return self._exists

    def create_repo(self, repo_id, repo_type=None, private=False, exist_ok=True):
        self.created.append((repo_id, repo_type, private))
        self._exists = True

    def list_repo_files(self, repo_id, repo_type=None):
        if not self._exists:
            raise RuntimeError("repo not found")
        return list(self.files)

    def upload_file(self, path_or_fileobj=None, path_in_repo=None, repo_id=None,
                    repo_type=None, revision=None):
        if not self._writable:
            raise RuntimeError("403 Forbidden: write access required")
        self.uploaded.append(path_in_repo)
        self.files.append(path_in_repo)

    def delete_file(self, path_in_repo=None, repo_id=None, repo_type=None, revision=None):
        if not self._delete_ok:
            raise RuntimeError("500 Internal Server Error: delete failed")
        self.deleted.append(path_in_repo)
        if path_in_repo in self.files:
            self.files.remove(path_in_repo)

    def hf_hub_download(self, repo_id, filename, repo_type=None):
        if self._download_error is not None:
            raise self._download_error
        if filename not in self._remote_files:
            raise EntryNotFoundError(f"{filename} not found in {repo_id}")
        # Real hf_hub_download returns a local cache path; mimic that by writing the
        # configured content to a temp file so read_text's Path(...).read_text() works.
        fd, path = tempfile.mkstemp(suffix=".txt")
        Path(path).write_text(self._remote_files[filename], encoding="utf-8")
        return path


def _plan(entries):
    """Build a minimal PLAN_SCHEMA table, one row per (config, shard_id) pair."""
    rows = []
    for config, sid in entries:
        rows.append(
            {
                "config": config, "disease_slug": "d", "disease_name": "D",
                "conv_id": "conv_0001", "turn": 1, "role": "user",
                "text_raw": "x", "text_spoken": "x", "speaker_id": 0,
                "speaker_emotions": "neutral", "speaker_unique_source_s": 1.0,
                "shard_id": sid, "audio_path": f"{config}/d/{sid}/Turn1/user.flac",
            }
        )
    columns = {name: [r[name] for r in rows] for name in PLAN_SCHEMA.names}
    return pa.Table.from_pydict(columns, schema=PLAN_SCHEMA)


def test_plan_paths_are_namespaced_by_config():
    assert plan_path("vietnamese") == "plan/shard_plan-vietnamese.parquet"
    assert plan_hash_path("vietnamese") == "plan/plan_hash-vietnamese.txt"


def test_preflight_passes_on_a_writable_existing_repo():
    api = FakeApi()
    preflight(api, "Meddies/SynthAudio")
    assert api.uploaded and api.deleted


def test_preflight_creates_a_missing_repo():
    api = FakeApi(exists=False)
    preflight(api, "Meddies/SynthAudio", private=False)
    assert api.created == [("Meddies/SynthAudio", "dataset", False)]


def test_preflight_rejects_an_invalid_token():
    with pytest.raises(HubError, match="token"):
        preflight(FakeApi(whoami=None), "Meddies/SynthAudio")


def test_preflight_rejects_a_read_only_token():
    with pytest.raises(HubError, match="write"):
        preflight(FakeApi(writable=False), "Meddies/SynthAudio")


def test_preflight_cleans_up_its_probe_file():
    api = FakeApi()
    preflight(api, "Meddies/SynthAudio")
    assert api.files == []


def test_preflight_warns_instead_of_raising_when_cleanup_fails(capsys):
    # Write access was already proven by the successful upload, so a failing delete
    # must not blow up the whole preflight — but it must be visible, since it leaves
    # a stray probe file behind on the repo.
    api = FakeApi(delete_ok=False)
    preflight(api, "Meddies/SynthAudio")  # must not raise
    assert _PROBE_PATH in api.files
    assert "could not delete" in capsys.readouterr().out


def test_list_repo_paths_returns_a_set():
    assert list_repo_paths(FakeApi(files=["a", "b"]), "r") == {"a", "b"}


def test_shard_targets_pairs_ids_with_hf_paths():
    targets = shard_targets(_plan([("vietnamese", "vi-00000"), ("vietnamese", "vi-00001")]))
    assert targets == [
        ("vi-00000", "data/vietnamese/train-00000-of-00002.parquet"),
        ("vi-00001", "data/vietnamese/train-00001-of-00002.parquet"),
    ]


def test_shard_targets_dedupes_rows_sharing_a_shard_id():
    # A real plan has many rows (one per utterance turn) per shard; shard_targets
    # must collapse them to one (shard_id, path) pair, not one per row.
    plan = _plan(
        [
            ("vietnamese", "vi-00000"),
            ("vietnamese", "vi-00000"),
            ("vietnamese", "vi-00000"),
            ("vietnamese", "vi-00001"),
        ]
    )
    targets = shard_targets(plan)
    assert targets == [
        ("vi-00000", "data/vietnamese/train-00000-of-00002.parquet"),
        ("vi-00001", "data/vietnamese/train-00001-of-00002.parquet"),
    ]


def test_shard_targets_numbers_each_config_independently():
    # vietnamese and english must each get their own shard count and their own
    # -of-NNNNN total; mixing them would cross-contaminate the two languages.
    plan = _plan(
        [
            ("vietnamese", "vi-00000"),
            ("vietnamese", "vi-00001"),
            ("english", "en-00000"),
        ]
    )
    assert shard_targets(plan) == [
        ("en-00000", "data/english/train-00000-of-00001.parquet"),
        ("vi-00000", "data/vietnamese/train-00000-of-00002.parquet"),
        ("vi-00001", "data/vietnamese/train-00001-of-00002.parquet"),
    ]


def test_remaining_targets_excludes_uploaded_shards():
    plan = _plan([("vietnamese", "vi-00000"), ("vietnamese", "vi-00001"), ("vietnamese", "vi-00002")])
    existing = {"data/vietnamese/train-00001-of-00003.parquet"}
    assert [sid for sid, _ in remaining_targets(plan, existing)] == ["vi-00000", "vi-00002"]


def test_remaining_targets_is_empty_when_all_present():
    plan = _plan([("vietnamese", "vi-00000")])
    existing = {"data/vietnamese/train-00000-of-00001.parquet"}
    assert remaining_targets(plan, existing) == []


def test_remaining_targets_ignores_unrelated_repo_files():
    plan = _plan([("vietnamese", "vi-00000")])
    assert len(remaining_targets(plan, {"README.md", "plan/x.parquet"})) == 1


def test_remaining_targets_on_a_mixed_plan_returns_the_right_subset():
    plan = _plan(
        [
            ("vietnamese", "vi-00000"),
            ("vietnamese", "vi-00001"),
            ("english", "en-00000"),
        ]
    )
    existing = {"data/vietnamese/train-00000-of-00002.parquet"}  # only vi-00000 published
    assert [sid for sid, _ in remaining_targets(plan, existing)] == ["en-00000", "vi-00001"]


def test_read_text_returns_the_remote_content():
    api = FakeApi(remote_files={plan_hash_path("vietnamese"): "abc123"})
    assert read_text(api, "r", plan_hash_path("vietnamese")) == "abc123"


def test_read_text_returns_none_for_a_confirmed_missing_file():
    # No remote_files configured, so hf_hub_download raises EntryNotFoundError (a
    # real 404) -- the one case that legitimately means "no hash published yet".
    assert read_text(FakeApi(), "r", plan_hash_path("vietnamese")) is None


def test_read_text_raises_hub_error_on_a_transient_failure():
    # A connection error is not a confirmed absence -- collapsing it to None would
    # silently disable drift detection on exactly the kind of blip a long-running,
    # resumed-months-later job is likely to hit.
    api = FakeApi(download_error=ConnectionError("transient 503"))
    with pytest.raises(HubError, match="unknown"):
        read_text(api, "r", plan_hash_path("vietnamese"))


def test_check_plan_drift_passes_when_hashes_match(monkeypatch):
    api = FakeApi(files=[plan_hash_path("vietnamese")])
    monkeypatch.setattr("meddies_tts.hub.read_text", lambda *a, **k: "abc123")
    check_plan_drift(api, "r", "vietnamese", "abc123")


def test_check_plan_drift_passes_when_no_remote_hash(monkeypatch):
    monkeypatch.setattr("meddies_tts.hub.read_text", lambda *a, **k: None)
    check_plan_drift(FakeApi(), "r", "vietnamese", "abc123")


def test_check_plan_drift_raises_on_mismatch(monkeypatch):
    monkeypatch.setattr("meddies_tts.hub.read_text", lambda *a, **k: "OLDHASH")
    with pytest.raises(PlanDriftError, match="OLDHASH"):
        check_plan_drift(FakeApi(), "r", "vietnamese", "NEWHASH")


def test_check_plan_drift_raises_on_mismatch_without_monkeypatching_read_text():
    # Exercises the real read_text -> check_plan_drift path end to end, unlike every
    # other drift test above, which replaces read_text with a stub.
    api = FakeApi(remote_files={plan_hash_path("vietnamese"): "OLDHASH"})
    with pytest.raises(PlanDriftError, match="OLDHASH"):
        check_plan_drift(api, "r", "vietnamese", "NEWHASH")


def test_upload_bytes_writes_to_the_given_path():
    api = FakeApi()
    upload_bytes(api, "r", b"data", "plan/plan_hash-vietnamese.txt")
    assert api.uploaded == ["plan/plan_hash-vietnamese.txt"]
