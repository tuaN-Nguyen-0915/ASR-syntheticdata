def pair_turns(messages: list[dict]) -> list[tuple[dict, dict | None]]:
    for i, msg in enumerate(messages):
        expected_role = "assistant" if i % 2 == 0 else "user"
        if msg.get("role") != expected_role:
            raise ValueError(
                f"role mismatch at index {i}: expected '{expected_role}', "
                f"got '{msg.get('role')}'"
            )

    pairs: list[tuple[dict, dict | None]] = []
    i = 0
    while i < len(messages):
        assistant_msg = messages[i]
        user_msg = messages[i + 1] if i + 1 < len(messages) else None
        pairs.append((assistant_msg, user_msg))
        i += 2
    return pairs
