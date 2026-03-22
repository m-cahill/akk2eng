# M04 Run 3 — Phase D training & dev eval (aligned vs mixed)

**Date:** 2026-03-22  
**Baseline (locked):** chrF **≈ 39.8601**, BLEU **≈ 43.03** on frozen dev (`outputs/m01_t5`, repo-default decode / lex / norm v2) — see [M04_run1_baseline_and_data_audit.md](M04_run1_baseline_and_data_audit.md).

## Step 1 — Mixed dataset

**Command:** `python -m akk2eng.pipeline.mix_train`

**Outputs (gitignored):**

* `data/derived/alignment/mixed_train.csv`
* `data/derived/alignment/mixed_train_stats.json`

**Composition (this workspace):**

| Metric | Value |
|--------|------:|
| Document rows (`train.csv`) | 1561 |
| Aligned sentence rows | 262 |
| **Total** | **1823** |
| `aligned_fraction_of_total` | **0.1437** (~14.4%) |
| `aligned_to_document_ratio` | **0.1678** |

**Construction:** full document-level CSV **first**, then aligned rows sorted by `sentence_id` (deterministic).

## Step 2 — Training (continuation from `outputs/m01_t5`)

**Hardware note:** runs below used **`--device auto` → CPU** on the agent machine (no CUDA in this session). **Re-run on RTX 5090 with `--device cuda --fp32` for production comparison.**

**Training hyperparameters (both experiments):**

| Setting | Value |
|---------|--------|
| `epochs` | **1** *(abbreviated run; default in repo is 3 — re-run with `epochs=3` for full M04 comparison)* |
| `batch_size` | 4 |
| `learning_rate` | 3e-4 |
| `resume_model_dir` | `outputs/m01_t5` |

### Experiment 1 — aligned-only

```text
python -m akk2eng.pipeline.train \
  --train-csv data/derived/alignment/aligned_train_sentences.csv \
  --resume-model-dir outputs/m01_t5 \
  --output-dir outputs/m04_t5_aligned \
  --device auto --fp32 --epochs 1 --logging-steps 10
```

* Training rows after dropna: **262**
* Checkpoint: `outputs/m04_t5_aligned/`

### Experiment 2 — mixed corpus

```text
python -m akk2eng.pipeline.train \
  --train-csv data/derived/alignment/mixed_train.csv \
  --resume-model-dir outputs/m01_t5 \
  --output-dir outputs/m04_t5_mixed \
  --device auto --fp32 --epochs 1 --logging-steps 50
```

* Training rows after dropna: **1823**
* Checkpoint: `outputs/m04_t5_mixed/`

## Step 3 — Dev eval (isolated artifact dirs)

Default eval contract unchanged (beam=3, lex on, norm v2).

```text
python -m akk2eng.pipeline.eval --model-dir outputs/m04_t5_aligned \
  --output-dir outputs/eval_m04_aligned --experiments-dir outputs/experiments_m04_aligned --quiet

python -m akk2eng.pipeline.eval --model-dir outputs/m04_t5_mixed \
  --output-dir outputs/eval_m04_mixed --experiments-dir outputs/experiments_m04_mixed --quiet
```

## Step 4 — Results vs baseline (this run)

| Model | chrF | BLEU | Δ chrF vs baseline |
|-------|------|------|-------------------|
| **Baseline** `m01_t5` | 39.8601 | 43.03 | — |
| **Exp1** aligned-only (1 ep, CPU) | **41.6817** | 60.05 | **+1.82** |
| **Exp2** mixed (1 ep, CPU) | **34.0633** | 56.00 | **−5.80** |

**Artifacts:**

* `outputs/eval_m04_aligned/metrics.json`, `predictions_dev.csv`, `exp_*` under `outputs/experiments_m04_aligned/`
* `outputs/eval_m04_mixed/metrics.json`, `predictions_dev.csv`, `exp_*` under `outputs/experiments_m04_mixed/`

## Interpretation (audit-level)

1. **Aligned-only beat baseline** on dev chrF in this **1-epoch / CPU** pass — consistent with “high-quality sentence signal” but **must be confirmed** with `epochs=3` and **GPU** training to rule out step-count / noise artifacts.
2. **Mixed regressed sharply** vs baseline in the same conditions. Plausible factors (not proven here): single epoch insufficient to integrate duplicated corpus; optimization dynamics on ~1.8k rows with appended sentence pairs; or train/inference distribution interaction. **Do not treat this as final** until **3-epoch GPU** mixed run is logged.
3. **Submission gate (unchanged):** Kaggle only if dev chrF improves over **39.86** with a **stable** training protocol; aligned-only is *provisionally* above gate on this run — **confirm before submit**.

## Implementation added this pass

* `python -m akk2eng.pipeline.mix_train` — builds `mixed_train.csv` + stats JSON.
* `python -m akk2eng.pipeline.train` — **`--train-csv` may be repeated** to concatenate multiple CSVs in order (same columns: at minimum `transliteration`, `translation`).

Equivalent to mixed file without `mix_train`:

```text
python -m akk2eng.pipeline.train \
  --train-csv data/train.csv \
  --train-csv data/derived/alignment/aligned_train_sentences.csv \
  ...
```

(Document rows must appear **before** aligned rows if you rely on manual `--train-csv` ordering; `mix_train` enforces document-first + sorted aligned block.)

---

## GPU Confirmation Run — Aligned-only (epochs=3)

**Intent:** Confirm whether the **+1.82 chrF** aligned-only signal (1 epoch, CPU, `outputs/m04_t5_aligned`) survives **full training budget** (3 epochs, no `max-samples`).

### Training config (as-run, 2026-03-22)

| Field | Value |
|--------|--------|
| `train_csv` | `data/derived/alignment/aligned_train_sentences.csv` |
| `resume_model_dir` | `outputs/m01_t5` |
| `output_dir` | `outputs/m04_t5_aligned_full` |
| `device` | **`auto` → CPU** (`torch.cuda.is_available()` was **False**; `--device cuda` aborts in this environment) |
| `fp32` | yes (`--fp32`) |
| `epochs` | **3** |
| `batch_size` | 4 (default) |
| `learning_rate` | 3e-4 (default) |
| `logging_steps` | 20 (CLI override for shorter logs) |
| `train_runtime` | ~149 s (CPU) |

**Substrate note:** For the **originally specified** CUDA confirmation, re-run the same args with `--device cuda` on a workstation with a CUDA PyTorch wheel; expect different numerics vs CPU.

### Dataset

| Field | Value |
|--------|------:|
| Rows after dropna | **262** |

### Commands

**Executed (CPU fallback via `auto`):**

```bash
python -m akk2eng.pipeline.train \
  --train-csv data/derived/alignment/aligned_train_sentences.csv \
  --resume-model-dir outputs/m01_t5 \
  --output-dir outputs/m04_t5_aligned_full \
  --device auto --fp32 \
  --epochs 3 --logging-steps 20

python -m akk2eng.pipeline.eval \
  --model-dir outputs/m04_t5_aligned_full \
  --output-dir outputs/eval_m04_aligned_full \
  --experiments-dir outputs/experiments_m04_aligned_full
```

**Target GPU command (unchanged):** use `--device cuda` instead of `auto` when CUDA is available.

### Metrics (`outputs/eval_m04_aligned_full/metrics.json`)

| Metric | Value |
|--------|--------|
| **chrF** | **52.2530** |
| **BLEU** | **80.2650** |
| **Δ chrF vs baseline (~39.8601)** | **+12.39** |

**Output directories:**

* Model: `outputs/m04_t5_aligned_full/`
* Eval: `outputs/eval_m04_aligned_full/` (`metrics.json`, `predictions_dev.csv`, …)
* Experiments: `outputs/experiments_m04_aligned_full/exp_<UTC>/`

### Interpretation (required)

1. **Beat baseline?** **Yes** on frozen dev chrF (**52.25** vs **39.86**).
2. **Stable vs 1-epoch CPU run (41.68)?** **Yes — higher** with 3 epochs; same eval contract (beam=3, lex, norm v2).
3. **Overfitting / leakage risk?** **Material.** Aligned rows are derived from **full** `train.csv` **before** any train/dev split. Sentence-level pairs can share **`oare_id`** with documents in **`dev_split.csv`**, so dev chrF may be **optimistically biased** (partial label/surface overlap). **Do not treat 52.25 as an unbiased generalization estimate** until a **split-respecting** training corpus is used (e.g. align only `train_split.csv`, never `dev` docs).
4. **Trustworthy for Kaggle submission?** **Not solely on this number.** Public test is sentence-level and disjoint; high dev chrF under possible leakage does **not** certify LB gain. **M04 success candidate — awaiting submission decision**, but **only after** error-bucket / overlap audit or a clean split ablation.

### Decision rule (metrics-only)

| Condition | Mark |
|-----------|------|
| chrF > 39.86 | **M04 success candidate — awaiting submission decision** (with leakage caveat above) |
| chrF ≤ 39.86 | **No confirmed gain** |
