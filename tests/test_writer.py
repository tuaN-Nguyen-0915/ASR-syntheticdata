from meddies.writer import (
    get_next_conv_number,
    write_conversation,
    write_disease_name_file,
)


def _msg(role, content):
    return {"role": role, "content": content}


def test_get_next_conv_number_starts_at_one_for_new_dir(tmp_path):
    disease_dir = tmp_path / "some_disease"
    assert get_next_conv_number(disease_dir) == 1


def test_get_next_conv_number_counts_existing_conv_dirs(tmp_path):
    disease_dir = tmp_path / "some_disease"
    (disease_dir / "conv_0001").mkdir(parents=True)
    (disease_dir / "conv_0002").mkdir(parents=True)
    assert get_next_conv_number(disease_dir) == 3


def test_get_next_conv_number_handles_non_contiguous_dirs(tmp_path):
    disease_dir = tmp_path / "some_disease"
    (disease_dir / "conv_0001").mkdir(parents=True)
    (disease_dir / "conv_0003").mkdir(parents=True)
    assert get_next_conv_number(disease_dir) == 4


def test_write_disease_name_file_creates_file_with_name(tmp_path):
    disease_dir = tmp_path / "some_disease"
    write_disease_name_file(disease_dir, "Bong gân cổ chân")
    name_file = disease_dir / "_disease_name.txt"
    assert name_file.read_text(encoding="utf-8") == "Bong gân cổ chân"


def test_write_disease_name_file_is_idempotent_for_same_name(tmp_path):
    disease_dir = tmp_path / "some_disease"
    name_file = disease_dir / "_disease_name.txt"

    write_disease_name_file(disease_dir, "Bong gân cổ chân")
    write_disease_name_file(disease_dir, "Bong gân cổ chân")

    content = name_file.read_text(encoding="utf-8")
    assert content == "Bong gân cổ chân"
    assert content.count("Bong gân cổ chân") == 1


def test_write_disease_name_file_appends_distinct_colliding_name(tmp_path):
    disease_dir = tmp_path / "some_disease"
    name_file = disease_dir / "_disease_name.txt"

    write_disease_name_file(disease_dir, "Đau đầu")
    write_disease_name_file(disease_dir, "Dau dau")

    lines = name_file.read_text(encoding="utf-8").splitlines()
    assert lines == ["Đau đầu", "Dau dau"]


def test_write_conversation_creates_turn_folders_with_files(tmp_path):
    disease_dir = tmp_path / "some_disease"
    pairs = [
        (_msg("assistant", "<think>plan</think> Hello!"), _msg("user", "Hi doctor")),
        (_msg("assistant", "Take care."), None),
    ]

    conv_dir, warnings = write_conversation(disease_dir, 1, pairs)

    assert conv_dir == disease_dir / "conv_0001"
    assert (conv_dir / "Turn1" / "assistant.txt").read_text(encoding="utf-8") == "Hello!"
    assert (conv_dir / "Turn1" / "user.txt").read_text(encoding="utf-8") == "Hi doctor"
    assert (conv_dir / "Turn2" / "assistant.txt").read_text(encoding="utf-8") == "Take care."
    assert not (conv_dir / "Turn2" / "user.txt").exists()
    assert warnings == []


def test_write_conversation_logs_unclosed_think_warning(tmp_path):
    disease_dir = tmp_path / "some_disease"
    pairs = [(_msg("assistant", "<think>never closes"), _msg("user", "Hi"))]

    _, warnings = write_conversation(disease_dir, 1, pairs)

    assert warnings == ["Turn1: unclosed think tag"]
