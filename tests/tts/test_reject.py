from pathlib import Path

from meddies_tts.config import TextConfig
from meddies_tts.reject import Rejection, check, max_ngram_repeat, type_token_ratio

_CFG = TextConfig()
_FIXTURE = Path(__file__).parent / "fixtures" / "degenerate_vi.txt"


def test_type_token_ratio_all_unique_is_one():
    assert type_token_ratio("a b c d") == 1.0


def test_type_token_ratio_all_identical_is_low():
    assert type_token_ratio("a a a a") == 0.25


def test_type_token_ratio_of_empty_text_is_one():
    assert type_token_ratio("") == 1.0


def test_max_ngram_repeat_counts_repeated_five_grams():
    assert max_ngram_repeat("a b c d e a b c d e a b c d e") == 3


def test_max_ngram_repeat_is_one_when_nothing_repeats():
    assert max_ngram_repeat("a b c d e f g h i j") == 1


def test_max_ngram_repeat_short_text_is_one():
    assert max_ngram_repeat("a b c") == 1


def test_accepts_normal_utterance():
    text = ("Chào bác Meddies ạ. Dạo gần đây tôi có một cái mụn nhọt ở ngay vùng "
            "hậu môn, nó sưng to và rất đau ạ.")
    assert check(text, _CFG) is None


def test_rejects_text_over_max_chars():
    result = check("x" * 3001, _CFG)
    assert isinstance(result, Rejection)
    assert result.reason == "too_long"


def test_length_rule_fires_at_the_boundary():
    assert check("x" * 3000, _CFG) is None
    assert check("x" * 3001, _CFG).reason == "too_long"


def test_rejects_real_degenerate_fixture():
    result = check(_FIXTURE.read_text(encoding="utf-8"), _CFG)
    assert result is not None
    assert result.reason in {"too_long", "degenerate"}


def test_degeneration_rule_fires_independently_of_length():
    # Under 3000 chars, but heavily looping: caught by the degeneracy branch.
    text = ("Tôi cũng không có triệu chứng gì về sức khỏe " * 60)
    cfg = TextConfig(max_chars=100_000)
    result = check(text, cfg)
    assert result is not None
    assert result.reason == "degenerate"


def test_short_repetitive_text_is_not_rejected():
    # Fewer than 200 words, so the degeneracy branch does not apply.
    assert check("a a a a a", _CFG) is None


def test_rejection_detail_is_populated():
    assert check("x" * 4000, _CFG).detail
