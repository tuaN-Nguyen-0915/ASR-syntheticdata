from pathlib import Path

from .think_strip import strip_think_block


def get_next_conv_number(disease_dir: Path) -> int:
    """Next unused conv_NNNN number for disease_dir, based on the highest existing suffix (not a count, so non-contiguous folders don't collide)."""
    if not disease_dir.exists():
        return 1
    existing_numbers = [
        int(p.name.removeprefix("conv_"))
        for p in disease_dir.iterdir()
        if p.is_dir()
        and p.name.startswith("conv_")
        and p.name.removeprefix("conv_").isdigit()
    ]
    return max(existing_numbers, default=0) + 1


def write_disease_name_file(disease_dir: Path, original_name: str) -> None:
    """Records original_name in disease_dir/_disease_name.txt, one line per distinct name (idempotent — a name already present is not duplicated)."""
    disease_dir.mkdir(parents=True, exist_ok=True)
    name_file = disease_dir / "_disease_name.txt"
    if not name_file.exists():
        name_file.write_text(original_name, encoding="utf-8")
        return

    existing_names = name_file.read_text(encoding="utf-8").splitlines()
    if original_name in existing_names:
        return

    with name_file.open("a", encoding="utf-8") as f:
        f.write("\n" + original_name)


def write_conversation(
    disease_dir: Path,
    conv_number: int,
    pairs: list[tuple[dict, dict | None]],
) -> tuple[Path, list[str]]:
    """Writes each (assistant, user) pair to disease_dir/conv_NNNN/TurnM/{assistant.txt,user.txt} (user.txt omitted for a trailing unpaired assistant turn). Returns the conv dir and any think-tag warnings."""
    conv_dir = disease_dir / f"conv_{conv_number:04d}"
    warnings: list[str] = []

    for turn_index, (assistant_msg, user_msg) in enumerate(pairs, start=1):
        turn_dir = conv_dir / f"Turn{turn_index}"
        turn_dir.mkdir(parents=True, exist_ok=True)

        cleaned, warning = strip_think_block(assistant_msg["content"])
        (turn_dir / "assistant.txt").write_text(cleaned, encoding="utf-8")
        if warning:
            warnings.append(f"Turn{turn_index}: {warning}")

        if user_msg is not None:
            (turn_dir / "user.txt").write_text(
                user_msg["content"].strip(), encoding="utf-8"
            )

    return conv_dir, warnings
