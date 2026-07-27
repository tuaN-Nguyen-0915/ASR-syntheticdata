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


def test_format_tree_lists_files_under_directory(tmp_path):
    conv_dir = tmp_path / "conv_0001"
    (conv_dir / "Turn1").mkdir(parents=True)
    (conv_dir / "Turn1" / "assistant.txt").write_text("hi", encoding="utf-8")

    tree = download_meddies.format_tree(conv_dir)

    assert "Turn1" in tree
    assert "assistant.txt" in tree


def test_build_arg_parser_defaults():
    parser = download_meddies.build_arg_parser()
    args = parser.parse_args([])
    assert args.configs == ["vietnamese", "english"]
    assert args.limit == 100
    assert str(args.output) == "output"
