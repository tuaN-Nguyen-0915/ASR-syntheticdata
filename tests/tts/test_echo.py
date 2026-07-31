"""The corpus quotes the assistant's turn inside user.txt; it must not be spoken."""

import pytest

from meddies_tts.echo import MIN_ECHO_CHARS, strip_assistant_echo

_ASSISTANT = (
    "Cảm ơn anh Tài đã chia sẻ. Tôi hiểu anh đang lo lắng về kết quả AMH thấp "
    "và ảnh hưởng đến kế hoạch sinh con của hai vợ chồng."
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
    half = _ASSISTANT[: len(_ASSISTANT) // 2]
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
    before = "Tôi xin phép hỏi lại về điều bác sĩ vừa nói ở trên với tôi hôm nay nhé."
    assert len(before) > MIN_ECHO_CHARS
    user = f"{before} > {_ASSISTANT} {_REPLY}"
    out = strip_assistant_echo(user, _ASSISTANT)
    assert before in out and _REPLY in out
    assert _ASSISTANT not in out


def test_empty_inputs_are_returned_unchanged():
    assert strip_assistant_echo("", _ASSISTANT) == ""
    assert strip_assistant_echo(_REPLY, "") == _REPLY
