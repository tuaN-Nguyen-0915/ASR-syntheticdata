# tests/tts/test_chunking.py
from meddies_tts.chunking import chunk_text, split_clauses, split_sentences


def test_splits_on_sentence_terminators():
    assert split_sentences("Một. Hai! Ba?") == ["Một.", "Hai!", "Ba?"]


def test_keeps_terminator_attached():
    assert split_sentences("Xin chào bác.")[0].endswith(".")


def test_no_terminator_yields_single_sentence():
    assert split_sentences("không có dấu chấm") == ["không có dấu chấm"]


def test_empty_text_yields_no_sentences():
    assert split_sentences("") == []


def test_short_text_is_one_chunk():
    assert chunk_text("Xin chào bác.", 400) == ["Xin chào bác."]


def test_empty_text_yields_no_chunks():
    assert chunk_text("", 400) == []


def test_whitespace_only_yields_no_chunks():
    assert chunk_text("   \n  ", 400) == []


def test_packs_multiple_sentences_up_to_the_limit():
    text = " ".join(["Câu số một."] * 10)  # 12 chars each incl. space
    chunks = chunk_text(text, 40)
    assert all(len(c) <= 40 for c in chunks)
    assert len(chunks) > 1


def test_no_chunk_exceeds_max_chars():
    text = " ".join(f"Đây là câu số {i}." for i in range(200))
    assert all(len(c) <= 400 for c in chunk_text(text, 400))


def test_single_oversized_sentence_is_hard_split():
    text = "từ " * 500  # one sentence, 1500 chars, no terminator
    chunks = chunk_text(text, 100)
    assert len(chunks) > 1
    assert all(len(c) <= 100 for c in chunks)


def test_single_token_longer_than_limit_is_kept_whole():
    chunks = chunk_text("x" * 250, 100)
    assert chunks == ["x" * 250]


def test_chunks_preserve_all_tokens_in_order():
    text = " ".join(f"từ{i}." for i in range(300))
    assert " ".join(chunk_text(text, 120)).split() == text.split()


def test_no_chunk_is_empty_or_whitespace():
    text = "Một.  Hai.   Ba.    Bốn."
    assert all(c.strip() for c in chunk_text(text, 10))


def test_split_clauses_uses_comma_semicolon_colon():
    assert split_clauses("một, hai; ba: bốn") == ["một,", "hai;", "ba:", "bốn"]


def test_long_sentence_prefers_clause_boundaries_over_whitespace():
    # One sentence, no terminator until the end, but comma-separated.
    sentence = ", ".join(["phần " + "x" * 30 for _ in range(6)]) + "."
    chunks = chunk_text(sentence, 90)
    assert all(len(c) <= 90 for c in chunks)
    # every cut lands right after a comma, never mid-clause
    assert all(c.endswith((",", ".")) for c in chunks[:-1])


def test_falls_back_to_whitespace_when_a_clause_is_still_too_long():
    sentence = "từ " * 200  # no punctuation at all
    chunks = chunk_text(sentence, 60)
    assert len(chunks) > 1
    assert all(len(c) <= 60 for c in chunks)


def test_budget_matches_the_duration_target():
    from meddies_tts.config import TextConfig

    # 12 s at 14 chars/sec
    assert TextConfig().chunk_chars == 168
    assert TextConfig(chunk_target_seconds=13.0, chars_per_sec=20.0).chunk_chars == 260
