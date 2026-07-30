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


def test_default_budget_is_a_fixed_character_count():
    from meddies_tts.config import TextConfig

    # 12 s at 14 chars/sec
    assert TextConfig().chunk_chars == 130
    assert TextConfig(chunk_max_chars=260).chunk_chars == 260
    # The hard cap is the budget plus the tolerated overshoot.
    assert TextConfig(chunk_max_chars=130, chunk_overflow_chars=14).chunk_hard_cap == 144


# ---------------------------------------------------------------- overflow tolerance
def test_sentence_within_tolerance_is_absorbed_not_split_off():
    """A sentence that overshoots by <= overflow_chars joins the current chunk.

    Opening a new chunk costs a join: 250 ms of inserted silence plus an
    independent generation with its own seed. Not worth paying for 9 characters.
    """
    # 124 + space + 18 = 143, inside the 144 hard cap -> one chunk
    chunks = chunk_text("a" * 123 + ". " + "b" * 17 + ".", 130, 14)
    assert len(chunks) == 1
    assert len(chunks[0]) == 143


def test_sentence_past_the_tolerance_starts_a_new_chunk():
    """Past the hard cap the sentence must stay whole and begin the next chunk."""
    chunks = chunk_text("a" * 123 + ". " + "b" * 40 + ".", 130, 14)
    assert len(chunks) == 2
    assert chunks[0] == "a" * 123 + "."
    assert chunks[1] == "b" * 40 + "."


def test_zero_tolerance_reproduces_a_strict_budget():
    """overflow_chars=0 must behave exactly like a hard limit."""
    chunks = chunk_text("a" * 100 + ". " + "b" * 40 + ".", 130, 0)
    assert len(chunks) == 2


def test_tolerance_default_is_zero_so_callers_must_opt_in():
    """A caller that forgets to pass the tolerance gets the strict budget, not a surprise."""
    strict = chunk_text("a" * 123 + ". " + "b" * 17 + ".", 130)
    assert len(strict) == 2


def test_whole_sentences_are_preferred_over_filling_the_budget():
    """Three short sentences pack together; the fourth would bust the cap."""
    s = "Em chào bác sĩ."          # 15
    chunks = chunk_text(" ".join([s] * 12), 130, 14)
    # every chunk ends at a sentence boundary, none exceeds the hard cap
    assert all(c.endswith(".") for c in chunks)
    assert all(len(c) <= 144 for c in chunks)


def test_oversized_sentence_still_falls_back_to_clause_then_whitespace():
    """The tolerance must not swallow the tier-2/tier-3 fallback."""
    long_sentence = ", ".join(["phần " + "z" * 30] * 6) + "."
    assert len(long_sentence) > 144
    chunks = chunk_text(long_sentence, 130, 14)
    assert len(chunks) > 1
    assert all(len(c) <= 144 for c in chunks)


def test_a_single_word_longer_than_the_cap_is_emitted_not_mangled():
    """Cutting mid-word would make the model pronounce fragments."""
    word = "w" * 200
    assert chunk_text(word + ".", 130, 14) == [word + "."]
