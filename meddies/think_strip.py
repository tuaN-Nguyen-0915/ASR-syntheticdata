import re

_THINK_BLOCK_RE = re.compile(r"<think>.*?</think>", re.DOTALL)
_OPEN_TAG = "<think>"
_CLOSE_TAG = "</think>"


def strip_think_block(content: str) -> tuple[str, str | None]:
    if _OPEN_TAG not in content:
        return content.strip(), None
    if _CLOSE_TAG not in content:
        return content, "unclosed think tag"
    cleaned = _THINK_BLOCK_RE.sub("", content, count=1).strip()
    return cleaned, None
