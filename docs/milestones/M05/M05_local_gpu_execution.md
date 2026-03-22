# M05 — Final execution (local GPU)

**Use this on your RTX 5090 (or any CUDA) environment.** Cursor/cloud runners typically have no CUDA — this is the **only remaining M05 step**.

**Related:** [M05_run2_training_eval.md](M05_run2_training_eval.md) (fill results here after this run).

---

## Preconditions

```python
import torch
assert torch.cuda.is_available(), "CUDA required for milestone-grade M05"
```

```bash
git branch --show-current   # expect: m05-data-augmentation
```

Augmented dataset must exist (already built split-safe):

* `data/derived/augmentation/augmented_train_sentences.csv`

---

## Step 1 — Control training (aligned-only, run first)

```bash
python -m akk2eng.pipeline.train \
  --train-csv data/derived/alignment/aligned_train_sentences_split.csv \
  --resume-model-dir outputs/m01_t5 \
  --output-dir outputs/m05_t5_control_aligned \
  --device cuda --fp32 \
  --epochs 3
```

---

## Step 2 — Augmented training

```bash
python -m akk2eng.pipeline.train \
  --train-csv data/derived/augmentation/augmented_train_sentences.csv \
  --resume-model-dir outputs/m01_t5 \
  --output-dir outputs/m05_t5_augmented \
  --device cuda --fp32 \
  --epochs 3
```

---

## Step 3 — Evaluation

```bash
python -m akk2eng.pipeline.eval \
  --model-dir outputs/m05_t5_control_aligned \
  --output-dir outputs/eval_m05_control \
  --experiments-dir outputs/experiments_m05_control

python -m akk2eng.pipeline.eval \
  --model-dir outputs/m05_t5_augmented \
  --output-dir outputs/eval_m05_augmented \
  --experiments-dir outputs/experiments_m05_augmented
```

---

## Step 4 — Extract metrics

Read:

* `outputs/eval_m05_control/metrics.json`
* `outputs/eval_m05_augmented/metrics.json`

Record **chrF** (primary) and **BLEU** (secondary).

---

## Step 5 — Decision logic

**Pinned reference:** M04 baseline **≈ 43.34** chrF (split-safe aligned-only, same eval contract).

| Outcome | Rule |
|---------|------|
| **SUCCESS** | `augmented > control` **and** `augmented > 43.34` |
| **NEUTRAL** | `augmented ≈ control` **or** `augmented ≤ 43.34` (no clear win vs both) |
| **REGRESSION** | `augmented < control` |

Use conservative judgment on “≈ control” (small noise band).

---

## Step 6 — Update doc

Edit [M05_run2_training_eval.md](M05_run2_training_eval.md):

1. Fill the results table (control / augmented / M04 baseline).
2. Add a short **Interpretation** section.
3. Include **exactly one** of:

```text
M05 success candidate — augmented beats baseline and control
```

```text
M05 neutral — augmented does not clearly beat control
```

```text
M05 regression — augmentation hurts
```

---

## Do **not**

* Rerun the augmentation builder
* Change augmentation heuristics
* Change training hyperparameters (for this comparison)
* Submit to Kaggle yet
* Update `docs/akk2eng.md` until M05 is formally closed

---

## Completion signal (paste back)

```text
Control chrF:
Augmented chrF:
Δ vs control:
Decision:
```

---

## Artifacts (expected under `outputs/`, gitignored)

* `m05_t5_control_aligned/`
* `m05_t5_augmented/`
* `eval_m05_control/`
* `eval_m05_augmented/`
* `experiments_m05_control/` / `experiments_m05_augmented/`
