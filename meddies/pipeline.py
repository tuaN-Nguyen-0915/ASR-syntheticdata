from pathlib import Path
from typing import Callable

from .pairing import pair_turns
from .slugify import slugify_disease
from .writer import get_next_conv_number, write_conversation, write_disease_name_file


class MeddiesProcessor:
    def __init__(self, output_root: Path):
        self.output_root = output_root
        self._conv_counters: dict[tuple[str, str], int] = {}
        self.first_written_conv_dir: Path | None = None

    def process_row(
        self, row: dict, config: str, log_fn: Callable[[str], None]
    ) -> str:
        row_id = row.get("id", "<unknown>")

        try:
            pairs = pair_turns(row["messages"])

            original_disease_name = row.get("target_disease") or ""
            disease_slug = slugify_disease(original_disease_name)
            disease_dir = self.output_root / config / disease_slug
            write_disease_name_file(disease_dir, original_disease_name)

            counter_key = (config, disease_slug)
            if counter_key not in self._conv_counters:
                self._conv_counters[counter_key] = get_next_conv_number(disease_dir)
            conv_number = self._conv_counters[counter_key]
            self._conv_counters[counter_key] += 1

            conv_dir, warnings = write_conversation(disease_dir, conv_number, pairs)
        except (ValueError, KeyError, TypeError, AttributeError) as exc:
            log_fn(f"{config}\t{row_id}\tSKIPPED\t{exc}")
            return "skipped"

        if self.first_written_conv_dir is None:
            self.first_written_conv_dir = conv_dir
        for warning in warnings:
            log_fn(f"{config}\t{row_id}\tWARNING\t{warning}")
        return "written"
