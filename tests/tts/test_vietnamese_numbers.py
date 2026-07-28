# tests/tts/test_vietnamese_numbers.py
import pytest

from meddies_tts.vietnamese_numbers import (
    NORTHERN,
    SOUTHERN,
    decimal_to_words,
    dialect_from_seed,
    digits_to_words,
    number_to_words,
)


@pytest.mark.parametrize(
    "n,expected",
    [
        (0, "không"), (1, "một"), (4, "bốn"), (5, "năm"), (9, "chín"),
        (10, "mười"), (11, "mười một"), (14, "mười bốn"), (15, "mười lăm"),
        (19, "mười chín"), (20, "hai mươi"), (21, "hai mươi mốt"),
        (24, "hai mươi tư"), (25, "hai mươi lăm"), (31, "ba mươi mốt"),
        (44, "bốn mươi tư"), (45, "bốn mươi lăm"), (55, "năm mươi lăm"),
        (90, "chín mươi"), (99, "chín mươi chín"),
        (100, "một trăm"), (101, "một trăm linh một"), (105, "một trăm linh năm"),
        (110, "một trăm mười"), (115, "một trăm mười lăm"),
        (140, "một trăm bốn mươi"), (155, "một trăm năm mươi lăm"),
        (500, "năm trăm"), (625, "sáu trăm hai mươi lăm"),
        (999, "chín trăm chín mươi chín"),
        (1000, "một nghìn"), (1005, "một nghìn không trăm linh năm"),
        (1050, "một nghìn không trăm năm mươi"), (1500, "một nghìn năm trăm"),
        (2024, "hai nghìn không trăm hai mươi tư"),
        (10_000, "mười nghìn"), (100_000, "một trăm nghìn"),
        (1_000_000, "một triệu"), (1_500_000, "một triệu năm trăm nghìn"),
        (2_000_000_000, "hai tỷ"),
    ],
)
def test_number_to_words(n, expected):
    assert number_to_words(n) == expected


@pytest.mark.parametrize(
    "text,expected",
    [
        ("38.5", "ba mươi tám phẩy năm"),
        ("37,2", "ba mươi bảy phẩy hai"),
        ("62,5", "sáu mươi hai phẩy năm"),
        ("0.5", "không phẩy năm"),
        ("1.25", "một phẩy hai năm"),
    ],
)
def test_decimal_to_words(text, expected):
    assert decimal_to_words(text) == expected


@pytest.mark.parametrize(
    "text,expected",
    [("115", "một một năm"), ("113", "một một ba"), ("911", "chín một một")],
)
def test_digits_to_words(text, expected):
    assert digits_to_words(text) == expected


def test_negative_numbers():
    assert number_to_words(-5) == "âm năm"


# --- per-speaker dialect -----------------------------------------------------

@pytest.mark.parametrize(
    "n,expected",
    [
        (101, "một trăm lẻ một"),
        (1000, "một ngàn"),
        (1005, "một ngàn không trăm lẻ năm"),
        (1_500_000, "một triệu năm trăm ngàn"),
    ],
)
def test_southern_dialect(n, expected):
    assert number_to_words(n, SOUTHERN) == expected


def test_four_follows_the_dialect():
    from dataclasses import replace

    assert number_to_words(24, replace(NORTHERN, four="tư")) == "hai mươi tư"
    assert number_to_words(24, replace(NORTHERN, four="bốn")) == "hai mươi bốn"


def test_fourteen_is_bon_regardless_of_dialect():
    from dataclasses import replace

    assert number_to_words(14, replace(NORTHERN, four="tư")) == "mười bốn"
    assert number_to_words(14, replace(NORTHERN, four="bốn")) == "mười bốn"


def test_dialect_from_seed_is_deterministic():
    assert dialect_from_seed(12345) == dialect_from_seed(12345)


def test_dialect_from_seed_never_mixes_registers():
    # "linh" must always travel with "nghìn", "lẻ" with "ngàn".
    for seed in range(500):
        d = dialect_from_seed(seed)
        assert (d.zero_filler == "linh") == (d.thousand == "nghìn")


def test_dialect_from_seed_produces_both_registers():
    assert {dialect_from_seed(s).thousand for s in range(200)} == {"nghìn", "ngàn"}


def test_dialect_from_seed_randomizes_four_independently():
    combos = {(dialect_from_seed(s).thousand, dialect_from_seed(s).four)
              for s in range(300)}
    assert len(combos) == 4


def test_decimal_uses_dialect_for_the_whole_part():
    assert decimal_to_words("101.5", SOUTHERN) == "một trăm lẻ một phẩy năm"
