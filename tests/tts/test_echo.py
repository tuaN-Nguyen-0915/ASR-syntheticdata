"""The corpus quotes the assistant's turn inside user.txt; it must not be spoken."""

import pytest

from meddies_tts.echo import MIN_ECHO_CHARS, strip_assistant_echo

# Fixtures must exceed MIN_ECHO_CHARS in CANONICAL length, so they are drawn at
# realistic turn length rather than trimmed to a line.
_ASSISTANT = (
    "Cảm ơn anh Tài đã chia sẻ. Tôi hiểu anh đang lo lắng về kết quả AMH thấp "
    "và ảnh hưởng đến kế hoạch sinh con của hai vợ chồng. Anh có thể cho tôi biết "
    "kết quả AMH cụ thể là bao nhiêu không? Và bác sĩ đã tư vấn gì thêm cho anh "
    "khi khám lần đó?"
)
_OTHER_ASSISTANT = (
    "Về chế độ dinh dưỡng, anh nên bổ sung kẽm và vitamin E hàng ngày, hạn chế "
    "rượu bia và thuốc lá, ngủ đủ giấc và tập thể dục đều đặn mỗi tuần để cải "
    "thiện chất lượng tinh trùng trong ba tháng tới."
)
_REPLY = (
    "Tôi đi khám ở bệnh viện phụ sản gần nhà, bác sĩ bảo chỉ số AMH của tôi là 0.8 ng/ml."
)


def test_strips_a_verbatim_quote_and_keeps_the_reply():
    user = f"> **Bác sĩ Meddies**: {_ASSISTANT} {_REPLY}"
    assert strip_assistant_echo(user, _ASSISTANT) == _REPLY


def test_returns_empty_when_the_utterance_is_only_the_echo():
    """2.26% of user turns are nothing but the quote — those must be rejectable."""
    user = f"> **Bác sĩ Meddies**: {_ASSISTANT}"
    assert strip_assistant_echo(user, _ASSISTANT) == ""


def test_matches_through_markup_the_single_line_corpus_leaves_behind():
    """The corpus is stored as one line, so '>' and '**' survive markup stripping.

    Matching therefore runs on a canonical letters/digits form; a verbatim
    comparison would miss every real case.
    """
    quoted = _ASSISTANT.replace(". ", ". > > ").replace("Tôi", "**Tôi**")
    user = f"> **Bác sĩ Meddies**: {quoted} {_REPLY}"
    assert strip_assistant_echo(user, _ASSISTANT) == _REPLY


def test_matches_despite_a_partial_quote():
    """Some turns quote only the opening of the assistant message."""
    # Must still exceed MIN_ECHO_CHARS; a shorter partial is deliberately ignored.
    half = _ASSISTANT[: int(len(_ASSISTANT) * 0.8)]
    user = f"> {half} {_REPLY}"
    assert strip_assistant_echo(user, _ASSISTANT) == _REPLY


def test_leaves_a_clean_user_turn_untouched():
    assert strip_assistant_echo(_REPLY, _ASSISTANT) == _REPLY


def test_does_not_strip_on_a_short_shared_phrase():
    """A shared greeting is not a quoted turn; stripping on it would eat real speech."""
    user = "Chào bác sĩ. Tôi bị đau bụng ba ngày nay và sốt cao liên tục không giảm."
    assert strip_assistant_echo(user, "Chào bác sĩ.") == user


def test_keeps_substantial_text_that_precedes_the_quote():
    """Only a bare speaker label is dropped from the head, not real content."""
    before = (
        "Tôi xin phép hỏi lại về điều bác sĩ vừa nói ở trên với tôi hôm nay nhé, "
        "vì tôi nghe chưa rõ lắm và muốn ghi lại cho vợ tôi cùng biết để tiện theo "
        "dõi tình hình sức khoẻ của tôi trong thời gian sắp tới ạ."
    )
    assert len(before) > MIN_ECHO_CHARS
    user = f"{before} > {_ASSISTANT} {_REPLY}"
    out = strip_assistant_echo(user, _ASSISTANT)
    assert before in out and _REPLY in out
    assert _ASSISTANT not in out


def test_empty_inputs_are_returned_unchanged():
    assert strip_assistant_echo("", _ASSISTANT) == ""
    assert strip_assistant_echo(_REPLY, "") == _REPLY
    assert strip_assistant_echo(_REPLY, []) == _REPLY


# --- matching across the whole conversation, not just the sibling turn --------

def test_finds_a_quote_from_a_different_turn():
    """1.68 of 3.60 percentage points of contamination come from another turn.

    Comparing only against the same-turn assistant sibling misses nearly half of
    the problem, so the caller passes every assistant turn in the conversation.
    """
    user = f"> **Bác sĩ Meddies**: {_OTHER_ASSISTANT} {_REPLY}"
    assert strip_assistant_echo(user, [_ASSISTANT, _OTHER_ASSISTANT]) == _REPLY


def test_picks_the_longest_match_when_several_turns_overlap():
    """A contaminated file often shares a greeting with several turns.

    Stripping on the first match rather than the longest would leave most of the
    quoted turn in place.
    """
    user = f"{_ASSISTANT} {_OTHER_ASSISTANT} {_REPLY}"
    out = strip_assistant_echo(user, [_ASSISTANT, _OTHER_ASSISTANT])
    assert _OTHER_ASSISTANT not in out


def test_a_short_match_below_the_floor_is_left_alone():
    """The 40-150 char valley is ~50/50 contaminated vs genuine patient speech.

    Sampled cases include real patient turns a LATER assistant message quotes
    back verbatim, at 100% coverage -- structurally identical to contamination.
    Stripping there would delete real speech, so the floor deliberately excludes it.
    """
    short_patient_turn = "Em chào bác sĩ ạ. Dạo gần đây em có hiện tượng ra máu khi xuất tinh."
    assistant_quoting_them = (
        f"Cảm ơn em đã chia sẻ. Em nói rằng: {short_patient_turn} "
        "Tôi hiểu điều này khiến em hoang mang, và tôi sẽ giải thích rõ nguyên nhân."
    )
    assert strip_assistant_echo(short_patient_turn, [assistant_quoting_them]) == short_patient_turn


def test_a_single_string_is_still_accepted():
    user = f"> {_ASSISTANT} {_REPLY}"
    assert strip_assistant_echo(user, _ASSISTANT) == _REPLY


# --- plan-level behaviour: detect and reject, do not repair -------------------

def test_build_plan_cleans_a_quoted_turn_without_dropping_the_utterance():
    """Conversations must stay whole: clean the echo, keep the pair."""
    import pyarrow as pa

    from meddies_tts.plan import build_plan
    from tests.tts.test_plan import _cfg, _pool, _NORMALIZERS

    assistant = (
        "Cảm ơn anh đã chia sẻ. Tôi hiểu anh đang lo lắng về kết quả xét nghiệm "
        "và ảnh hưởng của nó đến kế hoạch điều trị sắp tới của gia đình mình. "
        "Anh có thể cho tôi biết chỉ số cụ thể là bao nhiêu không ạ?"
    )
    manifest = pa.Table.from_pylist([
        {"config": "vietnamese", "disease_slug": "d", "disease_name": "D",
         "conv_id": "conv_0001", "turn": 1, "role": "assistant", "text_raw": assistant},
        {"config": "vietnamese", "disease_slug": "d", "disease_name": "D",
         "conv_id": "conv_0001", "turn": 1, "role": "user",
         "text_raw": f"> **Bác sĩ Meddies**: {assistant} Chỉ số của tôi là 0.8 ạ."},
    ])
    plan, rejects = build_plan(manifest, _cfg(), _pool(), _NORMALIZERS)

    assert sorted(plan.column("role").to_pylist()) == ["assistant", "user"], (
        "both halves of the turn must survive"
    )
    assert rejects == []
    user_row = next(r for r in plan.to_pylist() if r["role"] == "user")
    assert "Chỉ số của tôi" in user_row["text_spoken"]
    assert "Cảm ơn anh đã chia sẻ" not in user_row["text_spoken"], "echo not removed"


def test_a_pure_echo_utterance_falls_back_to_its_original_text():
    """When stripping leaves nothing there is no text to speak.

    Dropping would break the pair, so the original is kept instead -- knowingly
    bad audio rather than a hole in the conversation.
    """
    import pyarrow as pa

    from meddies_tts.plan import build_plan
    from tests.tts.test_plan import _cfg, _pool, _NORMALIZERS

    assistant = (
        "Cảm ơn anh đã chia sẻ. Tôi hiểu anh đang lo lắng về kết quả xét nghiệm "
        "và ảnh hưởng của nó đến kế hoạch điều trị sắp tới của gia đình mình. "
        "Anh có thể cho tôi biết chỉ số cụ thể là bao nhiêu không ạ?"
    )
    manifest = pa.Table.from_pylist([
        {"config": "vietnamese", "disease_slug": "d", "disease_name": "D",
         "conv_id": "conv_0001", "turn": 1, "role": "assistant", "text_raw": assistant},
        # Nothing but the quote — no patient reply at all.
        {"config": "vietnamese", "disease_slug": "d", "disease_name": "D",
         "conv_id": "conv_0001", "turn": 1, "role": "user",
         "text_raw": f"> **Bác sĩ Meddies**: {assistant}"},
    ])
    plan, rejects = build_plan(manifest, _cfg(), _pool(), _NORMALIZERS)
    assert sorted(plan.column("role").to_pylist()) == ["assistant", "user"]
    assert rejects == []


def test_build_plan_keeps_a_clean_user_turn():
    import pyarrow as pa

    from meddies_tts.plan import build_plan
    from tests.tts.test_plan import _cfg, _pool, _NORMALIZERS

    manifest = pa.Table.from_pylist([
        {"config": "vietnamese", "disease_slug": "d", "disease_name": "D",
         "conv_id": "conv_0001", "turn": 1, "role": "assistant",
         "text_raw": "Chào anh, anh thấy trong người thế nào ạ?"},
        {"config": "vietnamese", "disease_slug": "d", "disease_name": "D",
         "conv_id": "conv_0001", "turn": 1, "role": "user",
         "text_raw": "Tôi bị đau bụng ba ngày nay, kèm theo sốt nhẹ về chiều."},
    ])
    plan, rejects = build_plan(manifest, _cfg(), _pool(), _NORMALIZERS)
    assert sorted(plan.column("role").to_pylist()) == ["assistant", "user"]
    assert rejects == []


def test_a_divergence_mid_quote_does_not_leave_an_orphaned_fragment():
    """A prefix match stops at the FIRST character where the two copies differ.

    Real case (amh_thap/conv_0001/Turn4): the cut landed mid-question and left
    ~250 chars of the doctor still attached to the front of the "reply". The tail
    anchor finds where the quote actually ends so the whole thing goes.
    """
    assistant = (
        "Cảm ơn anh đã chia sẻ chi tiết về tình trạng của mình trong thời gian qua. "
        "Tôi hiểu anh đang rất lo lắng và phân vân giữa nhiều lựa chọn khác nhau. "
        "Hai vợ chồng anh đã sẵn sàng về tài chính và tâm lý cho phương án này chưa? "
        "Đây là chi phí không nhỏ và cần sự chuẩn bị kỹ lưỡng từ cả hai phía."
    )
    # The quote diverges partway through ("rất lo lắng" -> "khá lo lắng"), which is
    # exactly what truncates a prefix match.
    quoted = assistant.replace("rất lo lắng", "khá lo lắng")
    reply = "Tôi cảm thấy mệt mỏi kéo dài khoảng ba tháng nay, có giảm ham muốn và khó ngủ."
    out = strip_assistant_echo(f"> **Bác sĩ Meddies**: {quoted} {reply}", [assistant])
    assert out == reply, f"orphaned fragment left behind: {out[:80]!r}"
