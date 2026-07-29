import io

import pyarrow.parquet as pq
import pytest
import soundfile as sf
from datasets import Audio, load_dataset

from meddies_tts.audio import to_flac_bytes
from meddies_tts.writer import FEATURES, build_row, write_shard
import numpy as np


def _plan_row():
    return {
        "config": "vietnamese",
        "disease_slug": "ap_xe_hau_mon",
        "disease_name": "Áp xe hậu môn",
        "conv_id": "conv_0001",
        "turn": 1,
        "role": "user",
        "text_raw": "**Sốt cao (>38.5°C)**",
        "text_spoken": "Sốt cao trên ba mươi tám phẩy năm độ C",
        "speaker_id": "73",
        "speaker_source": "visec",
        "speaker_gender": "",
        "speaker_emotions": "angry|happy|neutral|sad",
        "speaker_unique_source_s": 412.7,
        "shard_id": "vi-00000",
        "audio_path": "vietnamese/ap_xe_hau_mon/conv_0001/Turn1/user.flac",
    }


def _flac(seconds=1.0, sample_rate=16000):
    t = np.linspace(0, seconds, int(seconds * sample_rate), endpoint=False)
    return to_flac_bytes((0.3 * np.sin(2 * np.pi * 220 * t)).astype(np.float32), sample_rate)


def test_features_declare_16k_audio():
    assert FEATURES["audio"].sampling_rate == 16000


def test_build_row_has_every_declared_column():
    row = build_row(_plan_row(), _flac(), 1.0, 1, 12345, "nanovllm-0.1")
    assert set(row) == set(FEATURES)


def test_build_row_keeps_both_text_columns():
    row = build_row(_plan_row(), _flac(), 1.0, 1, 12345, "nanovllm-0.1")
    assert row["text_raw"] == "**Sốt cao (>38.5°C)**"
    assert row["text_spoken"].startswith("Sốt cao trên")


def test_build_row_sets_audio_path_to_the_tree_path():
    row = build_row(_plan_row(), _flac(), 1.0, 1, 12345, "nanovllm-0.1")
    assert row["audio"]["path"] == "vietnamese/ap_xe_hau_mon/conv_0001/Turn1/user.flac"


def test_build_row_carries_provenance():
    row = build_row(_plan_row(), _flac(), 2.5, 3, 999, "nanovllm-0.1")
    assert row["duration_s"] == 2.5
    assert row["n_chunks"] == 3
    assert row["seed"] == 999
    assert row["engine_version"] == "nanovllm-0.1"


def test_build_row_drops_planning_only_columns():
    row = build_row(_plan_row(), _flac(), 1.0, 1, 1, "v")
    assert "shard_id" not in row
    assert "audio_path" not in row


def test_write_shard_creates_a_readable_parquet(tmp_path):
    rows = [build_row(_plan_row(), _flac(), 1.0, 1, 1, "v")]
    path = tmp_path / "train-00000-of-00001.parquet"
    write_shard(rows, path, "abc123", "{}")
    assert pq.read_table(path).num_rows == 1


def test_write_shard_embeds_plan_hash_in_metadata(tmp_path):
    path = tmp_path / "shard.parquet"
    write_shard([build_row(_plan_row(), _flac(), 1.0, 1, 1, "v")], path, "abc123", '{"a":1}')
    metadata = pq.read_table(path).schema.metadata
    assert metadata[b"plan_hash"] == b"abc123"
    assert metadata[b"config_json"] == b'{"a":1}'


def test_shard_reloads_with_audio_typing_and_valid_flac(tmp_path):
    # Deliberately avoids `datasets`' decode path: decoding an Audio feature
    # requires torchcodec, a consumer-side dependency this writer-only pipeline
    # does not need in order to produce a correctly typed, valid artifact. Instead
    # this verifies the two things that actually matter at write time: the schema
    # metadata round-trips into a real Audio feature type, and the raw bytes it
    # points at are genuinely decodable 16 kHz audio (checked directly via
    # soundfile, already a dependency).
    path = tmp_path / "train-00000-of-00001.parquet"
    write_shard([build_row(_plan_row(), _flac(2.0), 2.0, 1, 1, "v")], path, "h", "{}")

    # The falsifiable core: reloading via `datasets` must reconstruct the Audio
    # feature type from schema metadata alone -- no decode stack involved.
    ds = load_dataset("parquet", data_files=str(path), split="train")
    assert isinstance(ds.features["audio"], Audio)
    assert ds.features["audio"].sampling_rate == 16000

    # Indexing a row would trigger audio decode, so read the raw struct via
    # pyarrow instead and decode the FLAC bytes ourselves with soundfile.
    row = pq.read_table(path).to_pylist()[0]
    assert row["audio"]["path"] == "vietnamese/ap_xe_hau_mon/conv_0001/Turn1/user.flac"
    with sf.SoundFile(io.BytesIO(row["audio"]["bytes"])) as handle:
        assert handle.samplerate == 16000
        assert handle.frames == 32000

    assert row["text_raw"] == "**Sốt cao (>38.5°C)**"
    assert row["text_spoken"].startswith("Sốt cao trên")
    assert row["text_raw"] != row["text_spoken"]


def test_written_audio_bytes_are_flac(tmp_path):
    path = tmp_path / "shard.parquet"
    write_shard([build_row(_plan_row(), _flac(), 1.0, 1, 1, "v")], path, "h", "{}")
    raw = pq.read_table(path).column("audio").to_pylist()[0]["bytes"]
    with sf.SoundFile(io.BytesIO(raw)) as handle:
        assert handle.format == "FLAC"


def test_empty_row_list_raises(tmp_path):
    with pytest.raises(ValueError, match="no rows"):
        write_shard([], tmp_path / "shard.parquet", "h", "{}")


def test_row_missing_a_declared_key_raises(tmp_path):
    row = build_row(_plan_row(), _flac(), 1.0, 1, 1, "v")
    del row["disease_name"]
    with pytest.raises(ValueError, match="disease_name"):
        write_shard([row], tmp_path / "shard.parquet", "h", "{}")


def test_row_with_an_extra_key_raises(tmp_path):
    row = build_row(_plan_row(), _flac(), 1.0, 1, 1, "v")
    row["unexpected_column"] = "surprise"
    with pytest.raises(ValueError, match="unexpected_column"):
        write_shard([row], tmp_path / "shard.parquet", "h", "{}")
