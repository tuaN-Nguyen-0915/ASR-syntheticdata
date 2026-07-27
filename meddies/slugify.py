import re
import unicodedata


def slugify_disease(name: str | None) -> str:
    if not name or not name.strip():
        return "unknown_disease"
    normalized = unicodedata.normalize("NFKD", name)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
    lowered = ascii_only.lower()
    slug = re.sub(r"[^a-z0-9]+", "_", lowered).strip("_")
    return slug if slug else "unknown_disease"
