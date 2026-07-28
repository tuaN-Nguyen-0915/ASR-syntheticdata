# tests/tts/test_textprep.py
import pytest

from meddies_tts.textprep import (
    EnglishNormalizer,
    VietnameseNormalizer,
    get_normalizer,
    strip_markup,
)

_VN = VietnameseNormalizer()


def test_strips_bold_markers_keeping_content():
    assert strip_markup("**Về tình trạng của em**: ổn") == "Về tình trạng của em: ổn"


def test_strips_bullet_hyphens():
    assert strip_markup("- Apxe hậu môn\n- Búi trĩ sa") == "Apxe hậu môn Búi trĩ sa"


def test_strips_numbered_list_markers():
    assert strip_markup("1. Đầu tiên\n2. Sau đó") == "Đầu tiên Sau đó"


def test_collapses_whitespace_and_newlines():
    assert strip_markup("a  b\n\n\tc") == "a b c"


def test_keeps_digits_and_units_for_the_normalizer():
    assert strip_markup("**Sốt cao (>38.5°C)**") == "Sốt cao (>38.5°C)"


def test_empty_input_returns_empty():
    assert strip_markup("") == ""
    assert _VN.normalize("") == ""


def test_comparator_and_decimal_and_degrees():
    assert _VN.normalize("Sốt cao (>38.5°C) thì đi khám.") == (
        "Sốt cao (trên ba mươi tám phẩy năm độ C) thì đi khám."
    )


def test_hotline_is_read_digit_by_digit():
    assert _VN.normalize("hoặc gọi 115 nếu cần") == "hoặc gọi một một năm nếu cần"


def test_range_and_fraction():
    assert _VN.normalize("Mức độ đau 6-7/10, kéo dài 10-15 phút.") == (
        "Mức độ đau sáu đến bảy trên mười, kéo dài mười đến mười lăm phút."
    )


def test_dosage_with_units_and_period():
    assert _VN.normalize("Metformin 1000mg/ngày (2 viên 500mg).") == (
        "Metformin một nghìn mi-li-gam mỗi ngày (hai viên năm trăm mi-li-gam)."
    )


def test_percentage():
    assert _VN.normalize("(20% Drysol)") == "(hai mươi phần trăm Drysol)"


def test_blood_pressure_keeps_its_trailing_unit():
    assert _VN.normalize("Huyết áp là 140/90 mmHg.") == (
        "Huyết áp là một trăm bốn mươi trên chín mươi mi-li-mét thuỷ ngân."
    )


def test_latin_drug_names_pass_through_untouched():
    assert "Amlodipine" in _VN.normalize("dùng Amlodipine 5mg")


def test_text_without_digits_is_only_markup_stripped():
    assert _VN.normalize("**Xin chào bác sĩ.**") == "Xin chào bác sĩ."


def test_no_digits_remain_after_normalization():
    text = "Uống 625mg, 3 lần mỗi ngày trong 7-10 ngày, sốt >38.5°C, 140/90 mmHg, 20%."
    assert not any(ch.isdigit() for ch in _VN.normalize(text))


def test_output_has_no_double_spaces():
    assert "  " not in _VN.normalize("Nhiệt độ 37,2 độ, mạch 80 lần mỗi phút.")


def test_english_normalizer_verbalizes_integers():
    assert EnglishNormalizer().normalize("call 115 now") == "call one hundred and fifteen now"


def test_english_normalizer_strips_markup_first():
    assert EnglishNormalizer().normalize("**take 2 pills**") == "take two pills"


def test_get_normalizer_selects_by_config():
    assert isinstance(get_normalizer("vietnamese"), VietnameseNormalizer)
    assert isinstance(get_normalizer("english"), EnglishNormalizer)


def test_get_normalizer_rejects_unknown_config():
    with pytest.raises(ValueError, match="klingon"):
        get_normalizer("klingon")


# --- leaked reasoning blocks (2.77% of utterances) ---------------------------

def test_strips_a_closed_reasoning_block():
    assert _VN.normalize(
        "<thinking> **Giai đoạn**: Phase 4 - Closing. </thinking> Không có gì thưa Bác."
    ) == "Không có gì thưa Bác."


def test_strips_the_literal_think_block():
    assert _VN.normalize("<think>lý luận</think>Chào bác sĩ.") == "Chào bác sĩ."


def test_strips_malformed_reasoning_tags():
    assert _VN.normalize(
        '<internal_reasoning] ồn ào </internal_reasoning" Xin chào ạ.'
    ) == "Xin chào ạ."


def test_unclosed_open_tag_keeps_the_text():
    # Never delete content we cannot prove is reasoning.
    assert "Chào bác" in _VN.normalize("<think>lý luận chưa đóng Chào bác.")


def test_text_without_tags_is_untouched_by_reasoning_stripping():
    assert _VN.normalize("Câu bình thường.") == "Câu bình thường."


# --- units and identifiers ---------------------------------------------------

def test_expanded_units_are_verbalized():
    assert _VN.normalize("vitamin 400mcg") == "vitamin bốn trăm mi-crô-gam"
    assert _VN.normalize("khám lúc 8h") == "khám lúc tám giờ"
    assert _VN.normalize("cao 170cm") == "cao một trăm bảy mươi xen-ti-mét"


def test_word_per_period_slash():
    assert _VN.normalize("30 phút/ngày, 2 lần/tuần") == (
        "ba mươi phút mỗi ngày, hai lần mỗi tuần"
    )


def test_non_period_slash_becomes_a_space_not_moi():
    # 'anh/chị' occurs 9,760 times; 'anh mỗi chị' would be nonsense.
    assert _VN.normalize("Anh/chị ở quận/huyện nào?") == "Anh chị ở quận huyện nào?"


@pytest.mark.parametrize("ident", ["B12", "T4", "HbA1c", "N95", "SpO2", "COVID-19"])
def test_alphanumeric_identifiers_are_never_verbalized(ident):
    assert ident in _VN.normalize(f"xét nghiệm {ident} bình thường")


def test_identifier_protection_does_not_block_neighbouring_numbers():
    assert _VN.normalize("SpO2 95%") == "SpO2 chín mươi lăm phần trăm"


# --- Fix round 1: dotted-thousands currency, height, dosing shorthand, ------
# --- extra units, and Roman-numeral grading ----------------------------------

def test_dotted_thousands_currency():
    assert _VN.normalize("Giá 500.000 đồng một lần.") == (
        "Giá năm trăm nghìn đồng một lần."
    )


def test_dotted_thousands_range_with_glued_currency_symbol():
    assert _VN.normalize("Chi phí khoảng 100.000-300.000đ.") == (
        "Chi phí khoảng một trăm nghìn đến ba trăm nghìn đồng."
    )


def test_dotted_thousands_million_with_glued_currency_symbol():
    assert _VN.normalize("1.500.000đ") == "một triệu năm trăm nghìn đồng"


def test_dotted_thousands_is_not_confused_with_a_real_decimal():
    # "38.5" (1 digit after the dot) must still read as a decimal, not thousands.
    assert _VN.normalize("Sốt 38.5 độ") == "Sốt ba mươi tám phẩy năm độ"


def test_height_notation_reads_suffix_digit_by_digit():
    assert _VN.normalize("Cao 1m72, nặng 65kg.") == (
        "Cao một mét bảy hai, nặng sáu mươi lăm ki-lô-gam."
    )


def test_square_meters_is_not_mistaken_for_height_notation():
    assert _VN.normalize("Diện tích tổn thương 20m2.") == (
        "Diện tích tổn thương hai mươi mét vuông."
    )


def test_dosing_shorthand_x_times_per_period():
    assert _VN.normalize("Uống x2/ngày.") == "Uống hai lần mỗi ngày."


@pytest.mark.parametrize(
    "text,expected",
    [
        ("Diện tích 5m2", "Diện tích năm mét vuông"),
        ("vết loét 5cm2", "vết loét năm xen-ti-mét vuông"),
        ("Glucose 5mmol", "Glucose năm mi-li-mol"),
        ("dùng 2mol", "dùng hai mol"),
        ("bước sóng 400nm", "bước sóng bốn trăm na-nô-mét"),
    ],
)
def test_extra_units(text, expected):
    assert _VN.normalize(text) == expected


@pytest.mark.parametrize(
    "text,expected",
    [
        ("độ I", "độ một"),
        ("độ III", "độ ba"),
        ("giai đoạn II", "giai đoạn hai"),
        ("type I", "type một"),
    ],
)
def test_roman_numeral_severity_grading(text, expected):
    assert _VN.normalize(text) == expected


def test_bare_roman_numeral_without_a_grading_word_is_left_alone():
    # No "độ"/"giai đoạn"/"type"/"nhóm"/"cấp"/"mức" in front -- far more likely
    # to be an abbreviation or list marker than a severity grade.
    assert _VN.normalize("Chương trình X thành công.") == "Chương trình X thành công."


# --- fraction/decimal rules must not eat the space when no unit follows ------
# Found while testing Fix 1: "\s*(unit)?" outside the optional group still
# consumes the space even when the unit itself doesn't match, gluing the next
# word on ("37,2 độ" -> "...haiđộ"). Pre-existing in the original decimal and
# bare-fraction rules; fixed by moving "\s*" inside the optional group.

def test_decimal_without_a_trailing_unit_keeps_its_following_space():
    assert _VN.normalize("Sốt 38.5 độ") == "Sốt ba mươi tám phẩy năm độ"


def test_fraction_without_a_trailing_unit_keeps_its_following_space():
    assert _VN.normalize("Tỷ lệ 6/10 vậy đó.") == "Tỷ lệ sáu trên mười vậy đó."
