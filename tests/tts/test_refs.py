"""Reference-pool interchangeability: both corpora must load through one path."""

import csv

import pytest

from meddies_tts.config import ConfigError, RefsConfig
from meddies_tts.refs import _COLUMNS, build_vivos_refs
from meddies_tts.speakers import load_pool

# ViSEC as it actually ships: no gender, no transcript column at all.
_VISEC_CSV = """speaker_id,output_path,duration_seconds,clip_count,emotions,unique_source_duration_seconds
0,processed_audio_by_id/speaker_000.wav,12.968,8,angry|happy|neutral|sad,3951.683
2,processed_audio_by_id/speaker_002.wav,12.8,9,angry|neutral,67.904
10,processed_audio_by_id/speaker_010.wav,11.9,6,neutral,2.0
"""

# VIVOS as build_vivos_refs writes it: string ids, gender and transcript present,
# emotions empty because read speech carries no emotion labels.
_VIVOS_CSV = """speaker_id,output_path,duration_seconds,clip_count,emotions,unique_source_duration_seconds,gender,transcript
VIVOSDEV01,processed_audio_by_id/VIVOSDEV01.wav,10.972,2,,10.972,m,XIN CHÀO
VIVOSDEV02,processed_audio_by_id/VIVOSDEV02.wav,11.400,3,,11.400,f,CẢM ƠN
"""


def _pool_dir(tmp_path, body, names):
    root = tmp_path / "refs"
    audio = root / "processed_audio_by_id"
    audio.mkdir(parents=True)
    (audio / "metadata.csv").write_text(body, encoding="utf-8")
    for name in names:
        (audio / name).write_bytes(b"RIFF")
    return audio / "metadata.csv"


def test_visec_csv_still_loads_unchanged(tmp_path):
    """Switching back must not require touching the existing ViSEC directory."""
    pool = load_pool(_pool_dir(tmp_path, _VISEC_CSV,
                               ["speaker_000.wav", "speaker_002.wav", "speaker_010.wav"]))
    assert [s.speaker_id for s in pool] == ["0", "2", "10"]
    assert pool[0].emotions == "angry|happy|neutral|sad"
    assert pool[0].unique_source_s == pytest.approx(3951.683)
    # Absent columns are empty, never fabricated.
    assert pool[0].gender == ""
    assert pool[0].transcript == ""


def test_vivos_csv_loads_through_the_same_function(tmp_path):
    pool = load_pool(_pool_dir(tmp_path, _VIVOS_CSV,
                               ["VIVOSDEV01.wav", "VIVOSDEV02.wav"]))
    assert [s.speaker_id for s in pool] == ["VIVOSDEV01", "VIVOSDEV02"]
    assert pool[0].gender == "m"
    assert pool[0].transcript == "XIN CHÀO"
    assert pool[0].emotions == ""
    # VIVOS retains whole utterances, so its duration IS unique material.
    assert pool[0].unique_source_s == pytest.approx(10.972)


def test_numeric_ids_sort_numerically_not_lexically(tmp_path):
    """Lexical sort would order 0, 10, 2 and silently reshuffle the ViSEC pool.

    Speaker assignment samples from this list by index, so a reordering would
    change which voice every conversation gets without any config change.
    """
    pool = load_pool(_pool_dir(tmp_path, _VISEC_CSV,
                               ["speaker_000.wav", "speaker_002.wav", "speaker_010.wav"]))
    assert [s.speaker_id for s in pool] == ["0", "2", "10"]


def test_allow_filter_matches_on_string_ids(tmp_path):
    pool = load_pool(_pool_dir(tmp_path, _VISEC_CSV,
                               ["speaker_000.wav", "speaker_002.wav", "speaker_010.wav"]),
                     allow={"0", "10"})
    assert [s.speaker_id for s in pool] == ["0", "10"]


def test_refs_config_rejects_an_unknown_source():
    with pytest.raises(ConfigError, match="refs.source"):
        RefsConfig(source="librispeech")


def test_refs_config_defaults_to_visec():
    """The default must keep existing configs working without a refs: section."""
    assert RefsConfig().source == "visec"
    assert RefsConfig().dir == "/refs/visec"


def test_build_vivos_refs_writes_the_layout_load_pool_reads(tmp_path, monkeypatch):
    """build_vivos_refs output must be loadable by load_pool with no adapter."""
    import pyarrow as pa

    rows = [
        {"audio": {"bytes": b"RIFFfake", "path": "VIVOSDEV01_10s.wav"},
         "speaker_id": "VIVOSDEV01", "target_seconds": 10, "actual_seconds": 10.9,
         "source_clip_ids": "A_1 A_2", "gender": "m", "transcript": "XIN CHÀO"},
        # A different variant of the same speaker, which must be filtered out so
        # each speaker contributes exactly one reference.
        {"audio": {"bytes": b"RIFFother", "path": "VIVOSDEV01_30s.wav"},
         "speaker_id": "VIVOSDEV01", "target_seconds": 30, "actual_seconds": 29.5,
         "source_clip_ids": "A_1 A_2 A_3", "gender": "m", "transcript": "DÀI HƠN"},
    ]
    monkeypatch.setattr("pyarrow.parquet.read_table",
                        lambda *a, **k: pa.Table.from_pylist(rows))
    monkeypatch.setattr("huggingface_hub.hf_hub_download", lambda *a, **k: "/unused")

    assert build_vivos_refs(tmp_path, target_seconds=10) == 1

    csv_path = tmp_path / "processed_audio_by_id" / "metadata.csv"
    written = list(csv.DictReader(csv_path.open(encoding="utf-8")))
    assert [r["speaker_id"] for r in written] == ["VIVOSDEV01"]
    assert list(written[0]) == list(_COLUMNS)
    # The 10s variant's bytes, not the 30s one's.
    assert (tmp_path / "processed_audio_by_id" / "VIVOSDEV01.wav").read_bytes() == b"RIFFfake"

    pool = load_pool(csv_path)
    assert pool[0].speaker_id == "VIVOSDEV01"
    assert pool[0].transcript == "XIN CHÀO"


def test_build_vivos_refs_rejects_a_variant_that_does_not_exist(tmp_path, monkeypatch):
    """A typo'd target_seconds must fail loudly, not silently write an empty pool."""
    import pyarrow as pa

    rows = [{"audio": {"bytes": b"R", "path": "x.wav"}, "speaker_id": "S1",
             "target_seconds": 10, "actual_seconds": 10.0, "source_clip_ids": "a",
             "gender": "m", "transcript": "t"}]
    monkeypatch.setattr("pyarrow.parquet.read_table",
                        lambda *a, **k: pa.Table.from_pylist(rows))
    monkeypatch.setattr("huggingface_hub.hf_hub_download", lambda *a, **k: "/unused")

    with pytest.raises(ValueError, match=r"available: \[10\]"):
        build_vivos_refs(tmp_path, target_seconds=25)


def test_build_refs_is_reachable_from_the_cli(tmp_path, monkeypatch, capsys):
    """Registering the parser is not enough — cli.py dispatches through a dict.

    The first version of this command added an argparse subparser with
    set_defaults(func=...), which the dict-based dispatcher ignores entirely:
    `cli.py build-refs` died with KeyError instead of running.
    """
    import cli

    cfg_path = tmp_path / "c.yaml"
    cfg_path.write_text(
        'hf:\n  repo_id: "x/y"\nrefs:\n  source: "vivos"\n  target_seconds: 10\n',
        encoding="utf-8")
    called = {}

    def fake_build(dest, seconds):
        called["args"] = (dest, seconds)
        return 65

    monkeypatch.setattr("meddies_tts.refs.build_vivos_refs", fake_build)

    rc = cli.main(["--config", str(cfg_path), "build-refs", "--dest", str(tmp_path / "out")])
    assert rc == 0
    assert called["args"][1] == 10
    assert "65" in capsys.readouterr().out


def test_build_refs_on_visec_explains_that_nothing_is_needed(tmp_path, capsys):
    """ViSEC already ships in the target layout; say so rather than no-op silently."""
    import cli

    cfg_path = tmp_path / "c.yaml"
    cfg_path.write_text('hf:\n  repo_id: "x/y"\nrefs:\n  source: "visec"\n', encoding="utf-8")
    rc = cli.main(["--config", str(cfg_path), "build-refs", "--dest", str(tmp_path / "out")])
    assert rc == 0
    assert "nothing to build" in capsys.readouterr().out
