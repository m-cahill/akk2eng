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
