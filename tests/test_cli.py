import pytest
from datasets import Dataset

import download_meddies


def _fake_row(row_id, disease, messages=None):
    return {
        "id": row_id,
        "subset": "vietnamese",
        "messages": messages
        if messages is not None
        else [
            {"role": "assistant", "content": "Hello"},
            {"role": "user", "content": "Hi"},
        ],
        "target_disease": disease,
        "turns_count": 2,
        "patient_persona": "unused",
    }


def test_run_processes_rows_up_to_limit_and_writes_output(tmp_path, monkeypatch):
    fake_dataset = Dataset.from_list(
        [_fake_row(f"row-{i}", "Bong gân cổ chân") for i in range(5)]
    )

    def fake_load_dataset(repo_id, config_name, streaming=False):
        assert repo_id == "Meddies/meddies-consultant"
        return {"train": fake_dataset}

    monkeypatch.setattr(download_meddies, "load_dataset", fake_load_dataset)

    summary = download_meddies.run(
        configs=["vietnamese"], limit=3, output_root=tmp_path
    )

    assert summary["vietnamese"] == {"processed": 3, "skipped": 0, "warnings": 0}
    disease_dir = tmp_path / "vietnamese" / "bong_gan_co_chan"
    assert (disease_dir / "conv_0001").exists()
    assert (disease_dir / "conv_0003").exists()
    assert not (disease_dir / "conv_0004").exists()
    assert summary["first_written_conv_dir"] == disease_dir / "conv_0001"


def test_run_limit_larger_than_dataset_processes_all_rows(tmp_path, monkeypatch):
    fake_dataset = Dataset.from_list(
        [_fake_row(f"row-{i}", "Bong gân cổ chân") for i in range(2)]
    )

    def fake_load_dataset(repo_id, config_name, streaming=False):
        return {"train": fake_dataset}

    monkeypatch.setattr(download_meddies, "load_dataset", fake_load_dataset)

    summary = download_meddies.run(
        configs=["vietnamese"], limit=100, output_root=tmp_path
    )

    assert summary["vietnamese"] == {"processed": 2, "skipped": 0, "warnings": 0}


def test_run_counts_skipped_and_warning_rows(tmp_path, monkeypatch):
    good_row = _fake_row("row-good", "Bong gân cổ chân")
    skipped_row = _fake_row(
        "row-skip",
        "Bong gân cổ chân",
        messages=[
            {"role": "user", "content": "u1"},
            {"role": "assistant", "content": "a1"},
        ],
    )
    warning_row = _fake_row(
        "row-warn",
        "Bong gân cổ chân",
        messages=[
            {"role": "assistant", "content": "<think>never closes"},
            {"role": "user", "content": "u1"},
        ],
    )
    fake_dataset = Dataset.from_list([good_row, skipped_row, warning_row])

    def fake_load_dataset(repo_id, config_name, streaming=False):
        return {"train": fake_dataset}

    monkeypatch.setattr(download_meddies, "load_dataset", fake_load_dataset)

    summary = download_meddies.run(
        configs=["vietnamese"], limit=3, output_root=tmp_path
    )

    assert summary["vietnamese"] == {"processed": 2, "skipped": 1, "warnings": 1}
    assert (tmp_path / "skipped_rows.log").exists()


def test_run_processes_multiple_configs_independently(tmp_path, monkeypatch):
    dataset_a = Dataset.from_list([_fake_row("row-a1", "Bong gân cổ chân")])
    dataset_b = Dataset.from_list(
        [
            _fake_row("row-b1", "Bong gân cổ chân"),
            _fake_row("row-b2", "Bong gân cổ chân"),
        ]
    )
    datasets_by_config = {"config_a": dataset_a, "config_b": dataset_b}

    def fake_load_dataset(repo_id, config_name, streaming=False):
        assert repo_id == "Meddies/meddies-consultant"
        return {"train": datasets_by_config[config_name]}

    monkeypatch.setattr(download_meddies, "load_dataset", fake_load_dataset)

    summary = download_meddies.run(
        configs=["config_a", "config_b"], limit=10, output_root=tmp_path
    )

    assert summary["config_a"] == {"processed": 1, "skipped": 0, "warnings": 0}
    assert summary["config_b"] == {"processed": 2, "skipped": 0, "warnings": 0}

    disease_slug = "bong_gan_co_chan"
    disease_dir_a = tmp_path / "config_a" / disease_slug
    disease_dir_b = tmp_path / "config_b" / disease_slug
    assert (disease_dir_a / "conv_0001").exists()
    assert (disease_dir_b / "conv_0001").exists()
    assert (disease_dir_b / "conv_0002").exists()

    # The counter must not leak across configs: config_b's first conv is
    # still conv_0001, not conv_0002 continuing from config_a.
    assert summary["first_written_conv_dir"] == disease_dir_a / "conv_0001"


def test_run_refuses_to_reprocess_config_with_existing_data(
    tmp_path, monkeypatch, capsys
):
    call_count = {"n": 0}
    fake_dataset = Dataset.from_list([_fake_row("row-1", "Bong gân cổ chân")])

    def fake_load_dataset(repo_id, config_name, streaming=False):
        call_count["n"] += 1
        return {"train": fake_dataset}

    monkeypatch.setattr(download_meddies, "load_dataset", fake_load_dataset)

    download_meddies.run(configs=["vietnamese"], limit=10, output_root=tmp_path)
    disease_dir = tmp_path / "vietnamese" / "bong_gan_co_chan"
    assert (disease_dir / "conv_0001").exists()
    assert call_count["n"] == 1

    summary = download_meddies.run(
        configs=["vietnamese"], limit=10, output_root=tmp_path
    )

    # No second call to load_dataset, and no new conversation created.
    assert call_count["n"] == 1
    assert not (disease_dir / "conv_0002").exists()
    assert summary["vietnamese"] == {"processed": 0, "skipped": 0, "warnings": 0}
    assert summary["refused_configs"] == ["vietnamese"]

    captured = capsys.readouterr()
    assert "already contains data" in captured.err


def test_run_with_no_configs_writes_nothing(tmp_path):
    summary = download_meddies.run(configs=[], limit=10, output_root=tmp_path)

    assert summary["first_written_conv_dir"] is None
    assert summary["refused_configs"] == []


def test_run_deduplicates_repeated_config_names(tmp_path, monkeypatch):
    call_count = {"n": 0}
    fake_dataset = Dataset.from_list([_fake_row("row-1", "Bong gân cổ chân")])

    def fake_load_dataset(repo_id, config_name, streaming=False):
        call_count["n"] += 1
        return {"train": fake_dataset}

    monkeypatch.setattr(download_meddies, "load_dataset", fake_load_dataset)

    summary = download_meddies.run(
        configs=["vietnamese", "vietnamese"], limit=10, output_root=tmp_path
    )

    assert call_count["n"] == 1
    assert list(summary.keys()) == ["vietnamese", "first_written_conv_dir", "refused_configs"]


def test_run_rejects_config_name_containing_path_separator(tmp_path):
    with pytest.raises(ValueError, match="invalid --configs"):
        download_meddies.run(configs=["../escape"], limit=10, output_root=tmp_path)


def test_format_tree_lists_files_under_directory(tmp_path):
    conv_dir = tmp_path / "conv_0001"
    (conv_dir / "Turn1").mkdir(parents=True)
    (conv_dir / "Turn1" / "assistant.txt").write_text("hi", encoding="utf-8")

    tree = download_meddies.format_tree(conv_dir)
    lines = tree.splitlines()

    assert lines[0] == "conv_0001"
    assert lines[1] == "  Turn1"
    assert lines[2] == "    assistant.txt"


def test_run_limit_zero_processes_every_row(tmp_path, monkeypatch):
    fake_dataset = Dataset.from_list(
        [_fake_row(f"row-{i}", "Bong gân cổ chân") for i in range(12)]
    )

    def fake_load_dataset(repo_id, config_name, streaming=False):
        return {"train": fake_dataset}

    monkeypatch.setattr(download_meddies, "load_dataset", fake_load_dataset)

    summary = download_meddies.run(
        configs=["vietnamese"], limit=0, output_root=tmp_path
    )

    assert summary["vietnamese"] == {"processed": 12, "skipped": 0, "warnings": 0}


def test_run_prints_progress_every_5000_rows(tmp_path, monkeypatch, capsys):
    fake_dataset = Dataset.from_list(
        [_fake_row(f"row-{i}", "Bong gân cổ chân") for i in range(10001)]
    )

    def fake_load_dataset(repo_id, config_name, streaming=False):
        return {"train": fake_dataset}

    monkeypatch.setattr(download_meddies, "load_dataset", fake_load_dataset)

    download_meddies.run(configs=["vietnamese"], limit=10001, output_root=tmp_path)

    captured = capsys.readouterr()
    assert "vietnamese: 5000/10001 rows iterated" in captured.out
    assert "vietnamese: 10000/10001 rows iterated" in captured.out
    # No boundary at 10001 itself — only exact multiples of 5000 fire.
    assert "vietnamese: 10001/10001 rows iterated" not in captured.out


def test_build_arg_parser_defaults():
    parser = download_meddies.build_arg_parser()
    args = parser.parse_args([])
    assert args.configs == ["vietnamese", "english"]
    assert args.limit == 100
    assert str(args.output) == "output"
