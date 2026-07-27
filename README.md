# ASR-syntheticdata

Downloads the [`Meddies/meddies-consultant`](https://huggingface.co/datasets/Meddies/meddies-consultant) Hugging Face dataset (Vietnamese-first synthetic medical consultations) and restructures each conversation into per-turn text files, organized by disease.

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
python download_meddies.py --configs vietnamese english --limit 100 --output output/
```

- `--configs` — space-separated dataset configs to process (default: `vietnamese english`)
- `--limit` — rows per config (default: `100`)
- `--output` — output directory (default: `output/`)

Non-streaming download is used deliberately: the dataset is cached locally on first run, so re-running after a crash or bug fix reads from disk instead of re-fetching over the network.

## Output layout

```
output/
  <config>/                      # "vietnamese" or "english"
    <disease_slug>/
      _disease_name.txt          # original, un-slugified disease name(s) — one per line if a slug collision occurs
      conv_0001/
        Turn1/
          assistant.txt          # spoken reply only — <think> reasoning blocks are stripped
          user.txt
        Turn2/
          ...
      conv_0002/
        ...
  skipped_rows.log                # rows skipped (malformed data) or written with a warning (e.g. unclosed <think> tag)
```

Running the CLI again against an `--output` directory that already has data for a config is refused (not silently duplicated) — remove the existing output or point `--output` elsewhere to reprocess.

## Development

```bash
pytest -v
```

Design spec and implementation plan for this pipeline are under `docs/superpowers/specs/` and `docs/superpowers/plans/`.
