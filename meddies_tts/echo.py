"""Remove the assistant turn that the corpus copies into user.txt.

Many user.txt files quote the assistant's whole message back before the patient's
actual reply:

    (internal_reasoning) ... </internal_reasoning>
    > **Bác sĩ Meddies**: <the entire assistant turn, verbatim>
    Tôi đi khám ở bệnh viện phụ sản gần nhà, ...

Synthesizing that unedited puts the doctor's words in the patient's voice.
Measured over 19,709 turn pairs: 2.26% are ENTIRELY the echo with no reply at
all, and a further 0.42% are echo followed by a real reply.

Matching is done on a canonical form -- letters, digits and single spaces -- for
two reasons. The corpus is stored as one long line, so line-anchored markdown
rules barely fire and stray '>' and '*' survive into the text. And the two files
are normalized by DIFFERENT speakers' dialects, so "0.8" becomes "không phẩy tám"
in one and could differ in the other; comparing before verbalization sidesteps it.
"""

from __future__ import annotations

import re

from meddies_tts.textprep import strip_markup, strip_reasoning

_NOISE = re.compile(r"[^0-9a-zà-ỹA-ZÀ-Ỹ\s]+")
_SPACES = re.compile(r"\s+")

# Below this many characters, a "match" is likely an ordinary shared phrase
# (a greeting, the clinic name) rather than a quoted turn.
MIN_ECHO_CHARS = 40


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


def strip_assistant_echo(user_text: str, assistant_text: str) -> str:
    """Drop the quoted assistant turn from a user utterance.

    Returns whatever the patient actually said. If the utterance is nothing but
    the echo, returns "" -- the caller rejects it rather than synthesizing the
    doctor's words in the patient's voice.
    """
    if not user_text or not assistant_text:
        return user_text

    canon_user, index = _canonical(user_text)
    canon_assistant, _ = _canonical(assistant_text)
    if len(canon_assistant) < MIN_ECHO_CHARS or len(canon_user) < MIN_ECHO_CHARS:
        return user_text

    at = canon_user.find(canon_assistant)
    if at >= 0:
        end = at + len(canon_assistant)
    else:
        # Partial quote: keep the longest prefix of the assistant turn that is
        # present. Binary search rather than scanning every length.
        lo, hi, best = MIN_ECHO_CHARS, len(canon_assistant), 0
        while lo <= hi:
            mid = (lo + hi) // 2
            if canon_assistant[:mid] in canon_user:
                best, lo = mid, mid + 1
            else:
                hi = mid - 1
        if best < MIN_ECHO_CHARS:
            return user_text
        at = canon_user.find(canon_assistant[:best])
        end = at + best

    # Map the canonical end position back into the original string.
    tail = user_text[index[end]:] if end < len(index) else ""
    head = user_text[:index[at]] if at < len(index) else ""
    # Text before the quote is the reasoning block plus the speaker label the
    # corpus writes ("> **Bác sĩ Meddies**: "), neither of which the patient says.
    # The reasoning is stripped downstream anyway, so judge the head by what would
    # SURVIVE that -- otherwise a long reasoning block makes a bare label look like
    # real content and it gets spoken.
    if len(_canonical(strip_markup(strip_reasoning(head)))[0]) < MIN_ECHO_CHARS:
        head = ""
    return _SPACES.sub(" ", f"{head} {tail}").strip()
