# akk2eng

**Akkadian → English** machine translation for the Kaggle competition  
[Deep Past Initiative — Machine Translation](https://www.kaggle.com/competitions/deep-past-initiative-machine-translation/).

This repository is **M00**: a minimal, deterministic stub pipeline that produces a valid `submission.csv` so you can iterate on Kaggle quickly. It is **not** a competitive model yet.

## Requirements

- Python **3.10**
- `pip` + venv (recommended)

## Setup

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
# source .venv/bin/activate

pip install -e ".[dev,kaggle]"
```

The **`kaggle`** extra installs the [Kaggle API CLI](https://github.com/Kaggle/kaggle-api) for downloading competition data. Omit it if you only use notebooks on Kaggle.com.

## Download competition data (Kaggle CLI)

The competition bundle is **not** in this repo. Use the [Kaggle API](https://github.com/Kaggle/kaggle-api) after you **accept the competition rules** on the website.

1. **API credentials**  
   Kaggle → Account → **Create New API Token** → save `kaggle.json` to:
   - Windows: `%USERPROFILE%\.kaggle\kaggle.json`
   - Linux/macOS: `~/.kaggle/kaggle.json`

2. **Install CLI** (once), from the repo root with venv active:

```bash
pip install -e ".[kaggle]"
# or if the project is already installed: pip install kaggle
```

3. **Download** (from anywhere; `-p data` puts the zip under `data/`):

```bash
mkdir data
kaggle competitions download -c deep-past-initiative-machine-translation -p data
```

4. **Unzip** the archive in `data/` so **`data/test.csv`** exists at the path the local pipeline expects (if the zip contains a subfolder, move the CSVs up into `data/` or pass `--test-csv` to the nested path).

**Do not commit** downloaded files — `data/` is gitignored.

> **`docs/kaggledocs/`** holds copies of rules / dataset notes / lexicon snippets for documentation only. For training and submission, use the **official download** above — not the lexicon CSV as `test.csv`.

## Local run

1. Ensure `data/test.csv` is present (see **Download competition data** above).

2. From the **repository root**:

```bash
python -m akk2eng.pipeline.run
# or (equivalent):
python -m akk2eng.run_local
```

Defaults:

- Input: `data/test.csv`
- Output: `outputs/submission.csv`

Override paths:

```bash
python -m akk2eng.pipeline.run --test-csv path/to/test.csv --output path/to/submission.csv
```

## Kaggle

Use the self-contained notebook:

- `kaggle/akk2eng_m00_submission.ipynb`

Add it as a Kaggle Notebook, attach the competition dataset, and run all cells. It writes `/kaggle/working/submission.csv`. If the input folder name differs on Kaggle, edit `INPUT_DIR` in the first code cell.

## Tests

```bash
pytest
```

## Docs

- Project intent: `docs/moonshot.md`
- Source of truth (schema, milestones): `docs/akk2eng.md`
- M00 plan: `docs/milestones/M00/M00_plan.md`

## License

See `LICENSE`.
