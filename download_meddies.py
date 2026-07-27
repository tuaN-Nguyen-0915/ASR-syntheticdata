import argparse
import sys
from pathlib import Path

from datasets import load_dataset

from meddies.pipeline import STATUS_WRITTEN, MeddiesProcessor


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Download and restructure Meddies consultation transcripts."
    )
    parser.add_argument(
        "--configs", nargs="+", default=["vietnamese", "english"]
    )
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--output", type=Path, default=Path("output"))
    return parser


def _validate_config_name(config: str) -> None:
    if not config or "/" in config or "\\" in config or config in (".", ".."):
        raise ValueError(
            f"invalid --configs value {config!r}: must be a plain dataset "
            "config name, not a path"
        )


def format_tree(root: Path) -> str:
    lines = [root.name]
    for path in sorted(root.rglob("*")):
        depth = len(path.relative_to(root).parts)
        lines.append("  " * depth + path.name)
    return "\n".join(lines)


def run(configs: list[str], limit: int, output_root: Path) -> dict:
    configs = list(dict.fromkeys(configs))  # de-dupe, preserve order
    for config in configs:
        _validate_config_name(config)

    output_root.mkdir(parents=True, exist_ok=True)
    log_path = output_root / "skipped_rows.log"
    processor = MeddiesProcessor(output_root)
    summary: dict = {}
    refused_configs: list[str] = []
    log_file = None

    def log_fn(line: str, counts: dict) -> None:
        nonlocal log_file
        if log_file is None:
            log_file = log_path.open("a", encoding="utf-8")
        log_file.write(line + "\n")
        if "\tWARNING\t" in line:
            counts["warnings"] += 1

    try:
        for config in configs:
            config_dir = output_root / config
            if config_dir.exists() and any(
                p.is_dir() for p in config_dir.iterdir()
            ):
                print(
                    f"Error: {config_dir} already contains data; refusing to "
                    "reprocess (would duplicate conversations). Remove it or "
                    "use a different --output to proceed.",
                    file=sys.stderr,
                )
                refused_configs.append(config)
                summary[config] = {"processed": 0, "skipped": 0, "warnings": 0}
                continue

            counts = {"processed": 0, "skipped": 0, "warnings": 0}

            dataset = load_dataset(
                "Meddies/meddies-consultant", config, streaming=False
            )["train"]
            n = min(limit, len(dataset))
            for row in dataset.select(range(n)):
                status = processor.process_row(
                    dict(row), config, lambda line, c=counts: log_fn(line, c)
                )
                if status == STATUS_WRITTEN:
                    counts["processed"] += 1
                else:
                    counts["skipped"] += 1
            summary[config] = counts
    finally:
        if log_file is not None:
            log_file.close()

    summary["first_written_conv_dir"] = processor.first_written_conv_dir
    summary["refused_configs"] = refused_configs
    return summary


def main() -> None:
    args = build_arg_parser().parse_args()
    summary = run(args.configs, args.limit, args.output)
    total_processed = 0
    total_skipped = 0
    for config in dict.fromkeys(args.configs):
        stats = summary[config]
        total_processed += stats["processed"]
        total_skipped += stats["skipped"]
        print(
            f"{config}: processed {stats['processed']} rows, "
            f"skipped {stats['skipped']}, warnings {stats['warnings']}"
        )
    print(f"Total conversations written: {total_processed}")
    print(f"Output written to: {args.output.resolve()}")

    if total_skipped or any(summary[c]["warnings"] for c in dict.fromkeys(args.configs)):
        print(f"See {args.output / 'skipped_rows.log'} for skip/warning details.")

    refused_configs = summary.get("refused_configs", [])
    if refused_configs:
        print(
            "\nRefused to reprocess (output already contains data): "
            + ", ".join(refused_configs)
        )

    first_conv_dir = summary["first_written_conv_dir"]
    if first_conv_dir is not None:
        print(f"\nSpot-check — first conversation written ({first_conv_dir}):")
        print(format_tree(first_conv_dir))
    else:
        print("\nNo conversations were written.")


if __name__ == "__main__":
    main()
