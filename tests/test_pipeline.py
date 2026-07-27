from meddies.pipeline import MeddiesProcessor


def _row(row_id, messages, target_disease="Bong gân cổ chân"):
    return {
        "id": row_id,
        "messages": messages,
        "target_disease": target_disease,
        "turns_count": len(messages),
        "patient_persona": "unused",
    }


def _msg(role, content):
    return {"role": role, "content": content}


def test_process_row_writes_conversation_and_disease_name_file(tmp_path):
    processor = MeddiesProcessor(tmp_path)
    logs = []
    row = _row("row-1", [_msg("assistant", "Hello"), _msg("user", "Hi")])

    status = processor.process_row(row, "vietnamese", logs.append)

    disease_dir = tmp_path / "vietnamese" / "bong_gan_co_chan"
    assert status == "written"
    assert (disease_dir / "_disease_name.txt").read_text(encoding="utf-8") == "Bong gân cổ chân"
    assert (disease_dir / "conv_0001" / "Turn1" / "assistant.txt").read_text(
        encoding="utf-8"
    ) == "Hello"
    assert logs == []


def test_process_row_increments_conv_number_per_disease(tmp_path):
    processor = MeddiesProcessor(tmp_path)
    logs = []
    row1 = _row("row-1", [_msg("assistant", "a1"), _msg("user", "u1")])
    row2 = _row("row-2", [_msg("assistant", "a2"), _msg("user", "u2")])

    processor.process_row(row1, "vietnamese", logs.append)
    processor.process_row(row2, "vietnamese", logs.append)

    disease_dir = tmp_path / "vietnamese" / "bong_gan_co_chan"
    assert (disease_dir / "conv_0001").exists()
    assert (disease_dir / "conv_0002").exists()


def test_process_row_skips_and_logs_invalid_role_order(tmp_path):
    processor = MeddiesProcessor(tmp_path)
    logs = []
    row = _row("row-bad", [_msg("user", "u1"), _msg("assistant", "a1")])

    status = processor.process_row(row, "vietnamese", logs.append)

    assert status == "skipped"
    assert not (tmp_path / "vietnamese").exists()
    assert len(logs) == 1
    assert "row-bad" in logs[0]
    assert "SKIPPED" in logs[0]


def test_first_written_conv_dir_is_set_once_and_not_overwritten(tmp_path):
    processor = MeddiesProcessor(tmp_path)
    logs = []
    row1 = _row("row-1", [_msg("assistant", "a1"), _msg("user", "u1")])
    row2 = _row("row-2", [_msg("assistant", "a2"), _msg("user", "u2")])

    assert processor.first_written_conv_dir is None

    processor.process_row(row1, "vietnamese", logs.append)
    first_dir = processor.first_written_conv_dir
    assert first_dir == tmp_path / "vietnamese" / "bong_gan_co_chan" / "conv_0001"

    processor.process_row(row2, "vietnamese", logs.append)
    assert processor.first_written_conv_dir == first_dir


def test_process_row_logs_think_tag_warning_without_skipping(tmp_path):
    processor = MeddiesProcessor(tmp_path)
    logs = []
    row = _row(
        "row-warn",
        [_msg("assistant", "<think>never closes"), _msg("user", "u1")],
    )

    status = processor.process_row(row, "vietnamese", logs.append)

    disease_dir = tmp_path / "vietnamese" / "bong_gan_co_chan"
    assert status == "written"
    assert (disease_dir / "conv_0001" / "Turn1" / "assistant.txt").exists()
    assert len(logs) == 1
    assert "row-warn" in logs[0]
    assert "WARNING" in logs[0]
