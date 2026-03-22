# akk2eng

**Akkadian → English** machine translation for the Kaggle competition  
[Deep Past Initiative — Machine Translation](https://www.kaggle.com/competitions/deep-past-initiative-machine-translation/).

**M00** delivered a valid dummy submission pipeline. **M01** adds a **fine-tuned `google-t5/t5-small`** baseline (train locally, infer locally or on Kaggle). See `docs/akk2eng.md` for milestone status.

## Requirements

- Python **3.10** (see `pyproject.toml` upper bound)
- `pip` + venv (recommended)
- **M01-A (local):** NVIDIA driver + **CUDA-enabled PyTorch** matching your GPU (native **Windows** or **WSL2**; Docker not required). Install wheels from [pytorch.org](https://pytorch.org/get-started/locally/) if the default `pip` build is CPU-only.
- **NumPy:** the project pins **`numpy` 1.26.x** (`numpy>=1.26,<2`) so PyTorch’s dynamo stack (used by `transformers` / `accelerate`) does not break with NumPy 2.x.

## Setup

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
# source .venv/bin/activate

pip install -e ".[dev,kaggle]"
# M01 requires torch + transformers (declared in pyproject.toml).
```

The **`kaggle`** extra installs the [Kaggle API CLI](https://github.com/Kaggle/kaggle-api) for downloading competition data. Omit it if you only use notebooks on Kaggle.com.

## GPU bring-up (M01-A)

**Substrate validation** (CUDA + FP32 + Transformers + tiny train). **Not run in CI.** Requires a **CUDA PyTorch** wheel ([pytorch.org](https://pytorch.org/get-started/locally/)).

1. Bring-up (fails hard if CUDA is missing, the install is CPU-only, or the GPU arch is unsupported):

```bash
python -m akk2eng.tools.gpu_bringup
```

2. CUDA training smoke:

```bash
python -m akk2eng.pipeline.train --device cuda --fp32 --max-samples 50 --epochs 1 --logging-steps 5
```

3. In another terminal during training, verify GPU use:

```bash
nvidia-smi
```

4. Hash the checkpoint directory:

```bash
python -m akk2eng.tools.checkpoint_hash outputs/m01_t5
```

Record outputs in `docs/milestones/M01/M01_run1.md` for audit. Full training + checkpoint + inference audit: `docs/milestones/M01/M01_run2.md`.

### RTX 5090 / Blackwell local setup

Blackwell GPUs (compute capability `sm_120`, e.g. RTX 5090) require a **PyTorch build with CUDA 12.8+ support**. Older stable wheels (e.g. `2.5.1+cu124`) only ship kernels up to `sm_90` and will fail at the first CUDA tensor op. `gpu_bringup` detects this mismatch and prints an actionable error before the crash.

**Dual torch track:** `pyproject.toml` requires `torch>=2.4` with no upper bound so CI (CPU wheel from PyPI) and Blackwell (CUDA 12.8+ wheel) both resolve cleanly. On a **Blackwell workstation**, install the CUDA 12.8 index wheel **after** project install:

```powershell
# 1. Activate the project venv
Set-Location C:\coding\akk2eng
.\.venv\Scripts\Activate.ps1

# 2. Install project deps
pip install -e ".[dev]"

# 3. Replace torch with a Blackwell-capable build
pip uninstall -y torch
pip install torch --index-url https://download.pytorch.org/whl/cu128

# 4. Verify arch support
python -c "import torch; print(torch.__version__, torch.version.cuda, torch.cuda.get_arch_list())"

# 5. Run M01-A
python -m akk2eng.tools.gpu_bringup
python -m akk2eng.pipeline.train --device cuda --fp32 --max-samples 50 --epochs 1 --logging-steps 5
python -m akk2eng.tools.checkpoint_hash outputs/m01_t5
```

Adjust the **`--index-url`** to match the latest CUDA 12.8 wheel available at [pytorch.org/get-started/locally](https://pytorch.org/get-started/locally/). The repo's `pyproject.toml` no longer caps torch, so this install will not produce a pip version-conflict warning.

On **WSL2**, use the equivalent **Linux** CUDA 12.8 wheel inside the WSL venv.

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
- Model: `outputs/m01_t5/` if present (must contain `config.json` from training); otherwise **base** `google-t5/t5-small` is loaded for smoke tests.

On **WSL2**, install the **Linux** CUDA wheel inside the WSL venv; confirm `nvidia-smi` before M01-A.

**Train (local, M01-B full):** see `docs/milestones/M01/M01B_plan.md` and `M01B_toolcalls.md`.

```bash
python -m akk2eng.pipeline.train --train-csv data/train.csv --output-dir outputs/m01_t5
```

**Tiny training smoke (CPU fallback / laptops):**

```bash
python -m akk2eng.pipeline.train --max-samples 50 --epochs 1 --device cpu --fp32 --logging-steps 10
```

**`--device`:** `auto` (default), `cpu`, `cuda`. **`--fp32`:** conservative float32 (recommended on **Blackwell / new GPUs**).

**M04 — sentence alignment (optional training corpus):**

```bash
# Build aligned_train_sentences.csv + alignment_report.json (gitignored under data/derived/)
python -m akk2eng.pipeline.align

# Phase A data audit only → outputs/alignment/baseline_alignment_audit.json
python -m akk2eng.pipeline.align --audit-only

# Mixed corpus: full train.csv + aligned rows → data/derived/alignment/mixed_train.csv
python -m akk2eng.pipeline.mix_train

# Leak-safe alignment (train split only + dev overlap check; requires data/splits/*.csv)
python -m akk2eng.pipeline.align --split-safe
```

**M05 — alignment expansion (split-safe augmented sentence CSV):**

```bash
# Build augmented_train_sentences.csv + augmentation_report.json (gitignored under data/derived/augmentation/)
python -m akk2eng.pipeline.augment --split-safe
```

**M06 — precision-preserving selection (gated Policy A / B CSVs):**

```bash
# Requires split-safe augmented_train_sentences.csv + data/splits/dev_split.csv
python -m akk2eng.pipeline.select_train
```

Writes `data/derived/selection/strict_plus_highconf_cap50*.csv` + JSON reports (gitignored). Local **3-run GPU** matrix: **`docs/milestones/M06/M06_local_gpu_execution.md`**.

**M07 — confidence_v2 expansion selection (cap6 / cap10):**

```bash
# Requires split-safe augmented CSV, M06 Policy A baseline, and dev_split for overlap check
python -m akk2eng.pipeline.select_confident_train
```

Writes `data/derived/confidence/scored_expansion_pool.csv`, `strict_plus_confv2_cap{6,10}.csv`, and JSON reports (gitignored). GPU matrix: **`docs/milestones/M07/M07_local_gpu_execution.md`**.

Milestone-grade **3-epoch GPU** control + augmented train and dev eval (CUDA required): see **`docs/milestones/M05/M05_local_gpu_execution.md`**.

**M04 — continue fine-tuning from `outputs/m01_t5`:**

```bash
# Experiment 1 — aligned sentence pairs only (~262 rows typical)
python -m akk2eng.pipeline.train \
  --train-csv data/derived/alignment/aligned_train_sentences.csv \
  --resume-model-dir outputs/m01_t5 \
  --output-dir outputs/m04_t5_aligned \
  --device cuda --fp32

# Experiment 2 — mixed (document + aligned); co-primary with Exp 1 for M04
python -m akk2eng.pipeline.train \
  --train-csv data/derived/alignment/mixed_train.csv \
  --resume-model-dir outputs/m01_t5 \
  --output-dir outputs/m04_t5_mixed \
  --device cuda --fp32
```

**Multi-file training CSV (concatenate in order):**

```bash
python -m akk2eng.pipeline.train \
  --train-csv data/part_a.csv --train-csv data/part_b.csv \
  --resume-model-dir outputs/m01_t5 --output-dir outputs/custom_run
```

**Checkpoint hash manifest** (repeat runs / audit):

```bash
python -m akk2eng.tools.checkpoint_hash outputs/m01_t5
python -m akk2eng.tools.checkpoint_hash outputs/m01_t5 --combined-only
```

**Validate (90/10 split, sample rows):**

```bash
python -m akk2eng.pipeline.validate --train-csv data/train.csv --model-dir outputs/m01_t5
```

**Dev eval (M02-A — fixed split, chrF + BLEU, artifacts):**

```bash
python -m akk2eng.pipeline.eval --train-csv data/train.csv --model-dir outputs/m01_t5
```

Writes `data/splits/train_split.csv` and `data/splits/dev_split.csv` once (reuse thereafter), then `outputs/eval/predictions_dev.csv`, `metrics.json`, `eval_summary.txt`, plus a snapshot under `outputs/experiments/exp_<UTC>/`. Regenerate splits from a new `train.csv` with `--force-splits`.

By default, **M02-D lexicon post-processing** runs on predictions (`USE_LEXICON` in `config.py`). Disable with `python -m akk2eng.pipeline.eval --no-lexicon` (or `--lexicon-csv` / `--lexicon-max-entries` for A/B).

**Dev error buckets (M02-B — from `outputs/eval/predictions_dev.csv`):**

```bash
python -m akk2eng.pipeline.analyze_errors
```

Writes `outputs/analysis/error_buckets.json` and `outputs/analysis/bucket_examples.txt`.

Override paths:

```bash
python -m akk2eng.pipeline.run --test-csv path/to/test.csv --output path/to/submission.csv
python -m akk2eng.pipeline.run --model-dir outputs/m01_t5 --quiet
```

## Kaggle

Use the self-contained notebook:

- `kaggle/akk2eng_m01_submission.ipynb` (includes **M02-C** `repetition_penalty` / `no_repeat_ngram_size` on `generate()`, aligned with local `config.py`)

**Step-by-step (M01-C):** `docs/milestones/M01/M01C_checklist.md` (zip `outputs/m01_t5/`, upload as a dataset or Models asset, set paths, run all cells, submit).

**Validated path reference (as-run on Kaggle):** `docs/akk2eng-m01c-submission.ipynb`. Canonical template: `kaggle/akk2eng_m01_submission.ipynb` (set `MODEL_INPUT` to your mount).

Add the notebook as a Kaggle Notebook, attach the **competition** dataset and (recommended) a **second dataset** with your fine-tuned folder so `MODEL_INPUT` resolves to a path containing `config.json`. Run all cells; output is `/kaggle/working/submission.csv`. Adjust `INPUT_DIR` / `MODEL_INPUT` if slug names differ.

## Tests

```bash
pytest
```

## Docs

- Project intent: `docs/moonshot.md`
- Source of truth (schema, milestones): `docs/akk2eng.md`
- M00 plan: `docs/milestones/M00/M00_plan.md`
- M01 plan: `docs/milestones/M01/M01_plan.md`
- M01 audit / summary: `docs/milestones/M01/M01_audit.md`, `docs/milestones/M01/M01_summary.md`
- M02 plan: `docs/milestones/M02/M02_plan.md`
- M02 closeout (summary / audit, tag `v0.0.5-m02`): `docs/milestones/M02/M02_summary.md`, `docs/milestones/M02/M02_audit.md`
- M03 plan (normalization engine): `docs/milestones/M03/M03_plan.md`
- M01 GPU substrate run log: `docs/milestones/M01/M01_run1.md`
- M01 full training run log: `docs/milestones/M01/M01_run2.md`
- M01-C Kaggle checklist: `docs/milestones/M01/M01C_checklist.md`
- M01-C submission run log: `docs/milestones/M01/M01_run3.md`
- M01-C validated notebook (paths as-run): `docs/akk2eng-m01c-submission.ipynb`

## License

See `LICENSE`.
