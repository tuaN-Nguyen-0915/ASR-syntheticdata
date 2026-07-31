"""Remove assistant turns that the corpus copies into user.txt.

The generator frequently writes assistant content into a patient's file:

    (internal_reasoning) ... </internal_reasoning>
    > **Bác sĩ Meddies**: <an entire assistant turn, verbatim>
    Tôi đi khám ở bệnh viện phụ sản gần nhà, ...

Synthesizing that unedited puts the doctor's words in the patient's voice.
Measured over 29,965 user.txt files, comparing each against EVERY assistant turn
in its conversation:

    same-turn assistant       1.92%
    next-turn assistant       1.46%
    distant assistant turn    0.13%
    previous-turn assistant   0.09%
    -------------------------------
                              3.60%

The leak is one-directional. An earlier scan appeared to show assistant.txt
quoting user.txt at 2.04%, but those "user" files were themselves full of
assistant content, so the match was the doctor's own words found twice.

Matching runs on a canonical letters/digits form rather than verbatim text:
the corpus files contain ZERO newlines, so line-anchored markdown rules barely
fire and stray '>' and '**' survive; and user and assistant are normalized under
different speakers' number dialects, so "0.8" verbalizes differently in each.

MIN_ECHO_CHARS is 150 and that floor is load-bearing. The match-length
distribution is bimodal -- a noise spike below 40 chars, a valley from 40 to 150
holding ~160 files, then the real population above 150. Sampling the valley found
it is ~50/50: half are contaminated, half are genuine short patient turns that a
later assistant turn quotes back ("Em chào bác sĩ ạ. Dạo gần đây em có hiện
tượng ra máu khi xuất tinh..." appears in the next assistant message because the
doctor repeats the question). No structural signal separates the two at that
length -- coverage is 100% for both -- so the valley is deliberately left alone.
Keeping a contaminated utterance is recoverable; deleting real speech is not.
"""

from __future__ import annotations

import re

from meddies_tts.textprep import strip_markup, strip_reasoning

_NOISE = re.compile(r"[^0-9a-zà-ỹA-ZÀ-Ỹ\s]+")
_SPACES = re.compile(r"\s+")
# Sentence terminators used to snap a cut forward. '?' and '!' are here because
# the snap runs on RAW text, before clean_punctuation maps them to '.'.
_TERMINATOR = re.compile(r"[.!?…]")

# Floor for treating a match as a quoted turn. See the module docstring: below
# this, contaminated and genuine utterances are indistinguishable.
MIN_ECHO_CHARS = 150


def _canonical(text: str) -> tuple[str, list[int]]:
    """Lowercase letters/digits/spaces, plus a map back to original indices."""
    out: list[str] = []
    index: list[int] = []
    prev_space = True  # leading whitespace is dropped, not preserved
    for i, ch in enumerate(text):
        if ch.isspace():
            if not prev_space:
                out.append(" ")
                index.append(i)
                prev_space = True
            continue
        if _NOISE.match(ch):
            continue
        out.append(ch.lower())
        index.append(i)
        prev_space = False
    return "".join(out), index


# Characters of the quoted turn's TAIL used to locate where the echo ends. Long
# enough to be unique within a conversation, short enough to survive the small
# divergences (typos, stray markup) that truncate a prefix match.
_ANCHOR = 60


def _echo_end_by_suffix(canon_assistant: str, canon_user: str) -> int:
    """Position just past the quoted turn, found from its ending rather than its start.

    A prefix match stops at the FIRST divergence between the two copies, which is
    usually mid-sentence and leaves the rest of the quote sitting in the "reply".
    Anchoring on the tail finds where the quote actually ends, so the whole thing
    is removed. Returns -1 when the tail is not present.
    """
    if len(canon_assistant) < _ANCHOR:
        return -1
    anchor = canon_assistant[-_ANCHOR:]
    at = canon_user.rfind(anchor)
    return at + _ANCHOR if at >= 0 else -1


def _longest_prefix_in(needle: str, haystack: str) -> int:
    """Length of the longest prefix of needle that occurs in haystack."""
    lo, hi, best = MIN_ECHO_CHARS, len(needle), 0
    while lo <= hi:
        mid = (lo + hi) // 2
        if needle[:mid] in haystack:
            best, lo = mid, mid + 1
        else:
            hi = mid - 1
    return best


def strip_assistant_echo(user_text: str, assistant_texts: list[str] | str) -> str:
    """Drop quoted assistant content from a user utterance.

    assistant_texts should be EVERY assistant turn in the conversation, not just
    the same-turn sibling: 1.68 of the 3.60 percentage points of contamination
    come from other turns, mostly the next one. A single string is accepted for
    convenience and treated as a one-element list.

    Returns what the patient actually said, or "" when the utterance is nothing
    but quoted assistant text -- the caller rejects that rather than synthesizing
    the doctor's words in the patient's voice.
    """
    if isinstance(assistant_texts, str):
        assistant_texts = [assistant_texts]
    if not user_text or not assistant_texts:
        return user_text

    # Some files quote more than one turn, so strip repeatedly until nothing
    # above the floor remains. Bounded by the number of candidate turns, and each
    # pass strictly shortens the text, so it always terminates.
    for _ in range(len(assistant_texts)):
        stripped = _strip_once(user_text, assistant_texts)
        if stripped == user_text:
            break
        user_text = stripped
        if not user_text:
            break
    return user_text


# How far past a mid-sentence cut to look for a terminator. Long enough to clear
# the orphaned tail of a quoted question, short enough that a genuine reply
# beginning mid-clause is not discarded.
_SNAP_WINDOW = 400


def _snap_to_sentence(tail: str) -> str:
    """Advance a cut to the next sentence boundary if it landed mid-sentence."""
    stripped = tail.lstrip()
    if not stripped:
        return tail
    # A cut that already sits at a sentence start needs no adjustment. Detected by
    # the remainder beginning with a capital letter, which is what follows a
    # terminator in this corpus.
    if stripped[0].isupper():
        return tail
    match = _TERMINATOR.search(stripped[:_SNAP_WINDOW])
    if not match:
        return tail
    return stripped[match.end():].lstrip()


def _locate_quote(canon_assistant: str, canon_user: str) -> tuple[int, int]:
    """Find where a quoted assistant turn starts and ends inside the user text.

    Anchors on the first and last _ANCHOR characters INDEPENDENTLY rather than
    matching the turn as one block. The two copies routinely diverge somewhere in
    the middle -- a typo, a stray marker -- and a single whole-or-prefix match
    either fails outright or stops at the divergence and leaves the rest of the
    quote sitting at the front of the "reply". Two anchors survive any amount of
    drift between them. Returns (-1, -1) when the turn is not quoted here.
    """
    if len(canon_assistant) < _ANCHOR * 2:
        return -1, -1
    head_at = canon_user.find(canon_assistant[:_ANCHOR])
    if head_at < 0:
        return -1, -1
    tail_at = canon_user.rfind(canon_assistant[-_ANCHOR:])
    if tail_at < head_at:
        # Tail missing or ahead of the head: fall back to the longest prefix, which
        # still handles a quote that was truncated rather than altered.
        length = _longest_prefix_in(canon_assistant, canon_user)
        if length < MIN_ECHO_CHARS:
            return -1, -1
        return head_at, head_at + length
    end = tail_at + _ANCHOR
    if end - head_at < MIN_ECHO_CHARS:
        return -1, -1
    return head_at, end


def _strip_once(user_text: str, assistant_texts: list[str]) -> str:
    """Remove the single longest quoted assistant turn, if one is above the floor."""
    canon_user, index = _canonical(user_text)
    if len(canon_user) < MIN_ECHO_CHARS:
        return user_text

    # Take the LONGEST span across all turns. A contaminated file often shares a
    # short greeting with several turns; the longest identifies the real source.
    best_at, best_end = -1, -1
    for assistant_text in assistant_texts:
        canon_assistant, _ = _canonical(assistant_text)
        if len(canon_assistant) < MIN_ECHO_CHARS:
            continue
        at, end = _locate_quote(canon_assistant, canon_user)
        if at >= 0 and end - at > best_end - best_at:
            best_at, best_end = at, end

    if best_at < 0:
        return user_text

    tail = user_text[index[best_end]:] if best_end < len(index) else ""
    # The span can still end mid-sentence when the tail anchor lands inside one;
    # snapping forward drops the leftover fragment.
    tail = _snap_to_sentence(tail)
    head = user_text[:index[best_at]] if best_at < len(index) else ""
    # Text before the quote is the reasoning block plus the speaker label the
    # corpus writes ("> **Bác sĩ Meddies**: "), neither of which the patient says.
    # Judge it by what would SURVIVE reasoning-stripping downstream, or a long
    # reasoning block makes a bare label look like real content and it gets spoken.
    if len(_canonical(strip_markup(strip_reasoning(head)))[0]) < MIN_ECHO_CHARS:
        head = ""
    return _SPACES.sub(" ", f"{head} {tail}").strip()
