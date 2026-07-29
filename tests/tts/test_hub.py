# tests/tts/test_hub.py
import pyarrow as pa
import pytest

from meddies_tts.hub import (
    HubError,
    PlanDriftError,
    check_plan_drift,
    list_repo_paths,
    plan_hash_path,
    plan_path,
    preflight,
    remaining_targets,
    shard_targets,
    upload_bytes,
)
from meddies_tts.plan import PLAN_SCHEMA


_UNSET = object()  # distinguishes "whoami not passed" from an explicit whoami=None (invalid token)


class FakeApi:
    def __init__(self, files=(), writable=True, exists=True, whoami=_UNSET):
        self.files = list(files)
        self._writable = writable
        self._exists = exists
        self._whoami = {"name": "tester"} if whoami is _UNSET else whoami
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
        self.deleted.append(path_in_repo)
        if path_in_repo in self.files:
            self.files.remove(path_in_repo)

    def hf_hub_download(self, repo_id, filename, repo_type=None):
        raise NotImplementedError


def _plan(shard_ids):
    rows = []
    for sid in shard_ids:
        rows.append(
            {
                "config": "vietnamese", "disease_slug": "d", "disease_name": "D",
                "conv_id": "conv_0001", "turn": 1, "role": "user",
                "text_raw": "x", "text_spoken": "x", "speaker_id": 0,
                "speaker_emotions": "neutral", "speaker_unique_source_s": 1.0,
                "shard_id": sid, "audio_path": f"vietnamese/d/{sid}/Turn1/user.flac",
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


def test_list_repo_paths_returns_a_set():
    assert list_repo_paths(FakeApi(files=["a", "b"]), "r") == {"a", "b"}


def test_shard_targets_pairs_ids_with_hf_paths():
    targets = shard_targets(_plan(["vi-00000", "vi-00001"]))
    assert targets == [
        ("vi-00000", "data/vietnamese/train-00000-of-00002.parquet"),
        ("vi-00001", "data/vietnamese/train-00001-of-00002.parquet"),
    ]


def test_remaining_targets_excludes_uploaded_shards():
    plan = _plan(["vi-00000", "vi-00001", "vi-00002"])
    existing = {"data/vietnamese/train-00001-of-00003.parquet"}
    assert [sid for sid, _ in remaining_targets(plan, existing)] == ["vi-00000", "vi-00002"]


def test_remaining_targets_is_empty_when_all_present():
    plan = _plan(["vi-00000"])
    existing = {"data/vietnamese/train-00000-of-00001.parquet"}
    assert remaining_targets(plan, existing) == []


def test_remaining_targets_ignores_unrelated_repo_files():
    plan = _plan(["vi-00000"])
    assert len(remaining_targets(plan, {"README.md", "plan/x.parquet"})) == 1


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


def test_upload_bytes_writes_to_the_given_path():
    api = FakeApi()
    upload_bytes(api, "r", b"data", "plan/plan_hash-vietnamese.txt")
    assert api.uploaded == ["plan/plan_hash-vietnamese.txt"]
