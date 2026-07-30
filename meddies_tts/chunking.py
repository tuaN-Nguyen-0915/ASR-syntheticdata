from __future__ import annotations

import re

# '!' and '?' are here as a safety net only: clean_punctuation maps them to '.'
# before chunking ever runs, so in practice every boundary is a period. Keeping
# them costs nothing and stops a bypassed preprocessing step from silently
# producing one enormous "sentence".
_SENTENCE = re.compile(r"[^.!?…]+[.!?…]+|[^.!?…]+")
_CLAUSE = re.compile(r"[^,;:]+[,;:]+|[^,;:]+")


def split_sentences(text: str) -> list[str]:
    """Split on sentence terminators, keeping the terminator attached."""
    return [match.strip() for match in _SENTENCE.findall(text) if match.strip()]


def split_clauses(text: str) -> list[str]:
    """Secondary split points: comma, semicolon, colon.

    Only reached by sentences that bust the budget on their own. Measured on the
    corpus at a 130-char budget: 15.6% of sentences are oversized, 92.2% of those
    contain a comma, and only 4.6% have no clause boundary at all and need a
    whitespace cut.
    """
    return [match.strip() for match in _CLAUSE.findall(text) if match.strip()]


def _pack(pieces: list[str], max_chars: int, hard_cap: int) -> list[str]:
    """Join pieces greedily, preferring to keep whole sentences intact.

    Two thresholds, which is the point of this function. A piece is added while the
    result stays within max_chars; if it would overshoot, it is STILL added when the
    overshoot lands inside the tolerance (hard_cap), because starting a new chunk
    over a handful of characters costs a join -- 250 ms of silence plus an
    independent generation -- for no benefit. Past hard_cap the piece starts the
    next chunk, keeping the sentence whole.
    """
    chunks: list[str] = []
    current = ""
    for piece in pieces:
        candidate = f"{current} {piece}".strip() if current else piece
        if current and len(candidate) > hard_cap:
            chunks.append(current)
            current = piece
        else:
            current = candidate
    if current:
        chunks.append(current)
    return chunks


def _hard_split(sentence: str, max_chars: int, hard_cap: int) -> list[str]:
    """One sentence too long to speak in a single generation: clause, then whitespace."""
    by_clause = _pack(split_clauses(sentence), max_chars, hard_cap)
    if all(len(chunk) <= hard_cap for chunk in by_clause):
        return by_clause
    chunks: list[str] = []
    for clause in by_clause:
        if len(clause) <= hard_cap:
            chunks.append(clause)
        else:
            # Word boundaries are the floor: cutting mid-word would make the model
            # pronounce fragments. A single word longer than hard_cap is emitted
            # oversized rather than mangled.
            chunks.extend(_pack(clause.split(), max_chars, hard_cap))
    return chunks


def chunk_text(text: str, max_chars: int, overflow_chars: int = 0) -> list[str]:
    """Merge sentences into chunks of at most max_chars, tolerating a small overshoot.

    Whole sentences come first: a sentence that would push the chunk past the
    tolerance starts the next one instead of being split. Only a sentence that is
    itself over the tolerance gets broken, at clause punctuation and then at
    whitespace.

    max_chars is a fixed character budget, not a duration -- VoxCPM2 degrades past
    roughly 13 s per generation and 130 chars sits comfortably under that for every
    voice pool, where a seconds-derived budget would move with each pool's speech
    rate (measured: 17.42 chars/s on ViSEC vs 15.56 on VIVOS).
    """
    hard_cap = max_chars + max(0, overflow_chars)
    pieces: list[str] = []
    for sentence in split_sentences(text):
        if len(sentence) > hard_cap:
            pieces.extend(_hard_split(sentence, max_chars, hard_cap))
        else:
            pieces.append(sentence)
    return _pack(pieces, max_chars, hard_cap)
