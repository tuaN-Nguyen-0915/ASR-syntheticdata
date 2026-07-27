import pytest

from meddies.pairing import pair_turns


def _msg(role, content):
    return {"role": role, "content": content}


def test_pairs_even_length_alternating_conversation():
    messages = [
        _msg("assistant", "a1"), _msg("user", "u1"),
        _msg("assistant", "a2"), _msg("user", "u2"),
    ]
    pairs = pair_turns(messages)
    assert pairs == [
        (messages[0], messages[1]),
        (messages[2], messages[3]),
    ]


def test_odd_length_conversation_has_trailing_unpaired_assistant():
    messages = [
        _msg("assistant", "a1"), _msg("user", "u1"),
        _msg("assistant", "a2"),
    ]
    pairs = pair_turns(messages)
    assert pairs == [
        (messages[0], messages[1]),
        (messages[2], None),
    ]


def test_empty_messages_returns_empty_list():
    assert pair_turns([]) == []


def test_starting_with_user_raises_value_error():
    messages = [_msg("user", "u1"), _msg("assistant", "a1")]
    with pytest.raises(ValueError, match="index 0"):
        pair_turns(messages)


def test_two_assistants_in_a_row_raises_value_error():
    messages = [
        _msg("assistant", "a1"), _msg("assistant", "a2"), _msg("user", "u1"),
    ]
    with pytest.raises(ValueError, match="index 1"):
        pair_turns(messages)


def test_single_message_conversation_has_trailing_unpaired_assistant():
    messages = [_msg("assistant", "a1")]
    assert pair_turns(messages) == [(messages[0], None)]


def test_role_violation_in_the_middle_of_a_long_conversation_raises():
    messages = [
        _msg("assistant", "a1"), _msg("user", "u1"),
        _msg("assistant", "a2"), _msg("user", "u2"),
        _msg("user", "u3"), _msg("assistant", "a3"),
    ]
    with pytest.raises(ValueError, match="index 4"):
        pair_turns(messages)
