import re
import unicodedata

_DD_TRANSLATION = str.maketrans({"đ": "d", "Đ": "D"})


def slugify_disease(name: str | None) -> str:
    if not name or not name.strip():
        return "unknown_disease"
    dd_transliterated = name.translate(_DD_TRANSLATION)
    normalized = unicodedata.normalize("NFKD", dd_transliterated)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
    lowered = ascii_only.lower()
    slug = re.sub(r"[^a-z0-9]+", "_", lowered).strip("_")
    return slug if slug else "unknown_disease"
