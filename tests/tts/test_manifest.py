import pyarrow as pa

from meddies_tts.manifest import (
    MANIFEST_SCHEMA,
    build_manifest,
    read_manifest,
    write_manifest,
)


def _tree(root):
    """Build a miniature output_full/ tree: 2 diseases, 2 convs, 2 turns."""
    for disease, name in (("ap_xe_hau_mon", "Áp xe hậu môn"), ("suy_gan", "Suy gan")):
        ddir = root / "vietnamese" / disease
        ddir.mkdir(parents=True)
        (ddir / "_disease_name.txt").write_text(name, encoding="utf-8")
        for conv in ("conv_0001", "conv_0002"):
            for turn in (1, 2):
                tdir = ddir / conv / f"Turn{turn}"
                tdir.mkdir(parents=True)
                (tdir / "user.txt").write_text(f"{disease} u{turn}", encoding="utf-8")
                (tdir / "assistant.txt").write_text(f"{disease} a{turn}", encoding="utf-8")
    return root


def test_builds_one_row_per_utterance(tmp_path):
    table = build_manifest(_tree(tmp_path), ["vietnamese"])
    assert table.num_rows == 2 * 2 * 2 * 2  # disease x conv x turn x role


def test_schema_matches(tmp_path):
    table = build_manifest(_tree(tmp_path), ["vietnamese"])
    assert table.schema.equals(MANIFEST_SCHEMA)


def test_carries_unslugified_disease_name(tmp_path):
    table = build_manifest(_tree(tmp_path), ["vietnamese"])
    names = set(table.column("disease_name").to_pylist())
    assert names == {"Áp xe hậu môn", "Suy gan"}


def test_rows_are_deterministically_ordered(tmp_path):
    first = build_manifest(_tree(tmp_path), ["vietnamese"]).to_pylist()
    second = build_manifest(tmp_path, ["vietnamese"]).to_pylist()
    assert first == second
    keys = [(r["disease_slug"], r["conv_id"], r["turn"], r["role"]) for r in first]
    assert keys == sorted(keys)


def test_turn_parsed_as_int_and_text_preserved(tmp_path):
    rows = build_manifest(_tree(tmp_path), ["vietnamese"]).to_pylist()
    row = next(r for r in rows if r["disease_slug"] == "suy_gan"
               and r["conv_id"] == "conv_0002" and r["turn"] == 2 and r["role"] == "user")
    assert row["text_raw"] == "suy_gan u2"


def test_missing_disease_name_file_falls_back_to_slug(tmp_path):
    _tree(tmp_path)
    (tmp_path / "vietnamese" / "suy_gan" / "_disease_name.txt").unlink()
    rows = build_manifest(tmp_path, ["vietnamese"]).to_pylist()
    assert {r["disease_name"] for r in rows if r["disease_slug"] == "suy_gan"} == {"suy_gan"}


def test_turn_missing_one_role_still_emits_the_other(tmp_path):
    _tree(tmp_path)
    (tmp_path / "vietnamese" / "suy_gan" / "conv_0001" / "Turn2" / "assistant.txt").unlink()
    rows = build_manifest(tmp_path, ["vietnamese"]).to_pylist()
    turn = [r for r in rows if r["disease_slug"] == "suy_gan"
            and r["conv_id"] == "conv_0001" and r["turn"] == 2]
    assert [r["role"] for r in turn] == ["user"]


def test_absent_config_directory_is_skipped(tmp_path):
    table = build_manifest(_tree(tmp_path), ["vietnamese", "english"])
    assert set(table.column("config").to_pylist()) == {"vietnamese"}


def test_write_then_read_round_trips(tmp_path):
    table = build_manifest(_tree(tmp_path), ["vietnamese"])
    path = tmp_path / "manifest.parquet"
    write_manifest(table, path)
    assert read_manifest(path).to_pylist() == table.to_pylist()
