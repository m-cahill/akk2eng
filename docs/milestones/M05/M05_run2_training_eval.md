# M05 — Run 2: Training + eval vs M04 baseline

**Milestone:** M05  
**Baseline to beat:** dev chrF **≈ 43.34** (M04 split-safe aligned-only, 3 epochs, same eval contract as M02/M04).

---

## Execution status

| Phase | Status |
|--------|--------|
| Augmentation builder (`--split-safe`) | **Done** — [M05_run1_augmentation_builder.md](M05_run1_augmentation_builder.md) |
| Control + augmented **3-epoch GPU** train | **Blocked in Cursor/cloud sessions** — `torch.cuda.is_available()` **False** (verified again on GPU execution prompt) |
| Eval on `m05_t5_*` checkpoints | **Pending** — requires checkpoints from local GPU training |

**Milestone-grade chrF must come from your machine** (e.g. RTX 5090 / cu128). Do **not** use long CPU training as the comparison surface.

---

## Step 1 — Control training (GPU, run first)

```bash
python -m akk2eng.pipeline.train \
  --train-csv data/derived/alignment/aligned_train_sentences_split.csv \
  --resume-model-dir outputs/m01_t5 \
  --output-dir outputs/m05_t5_control_aligned \
  --device cuda --fp32 \
  --epochs 3
```

---

## Step 2 — Augmented training (GPU)

```bash
python -m akk2eng.pipeline.train \
  --train-csv data/derived/augmentation/augmented_train_sentences.csv \
  --resume-model-dir outputs/m01_t5 \
  --output-dir outputs/m05_t5_augmented \
  --device cuda --fp32 \
  --epochs 3
```

---

## Step 3 — Evaluate both (separate eval + experiment dirs)

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

Metrics: read `outputs/eval_m05_control/metrics.json` and `outputs/eval_m05_augmented/metrics.json` (or the latest `exp_*` snapshot under each `experiments_*` dir).

---

## Results table (fill after local GPU runs)

| Run | chrF | BLEU |
|-----|------|------|
| M05 control | _pending_ | _pending_ |
| M05 augmented | _pending_ | _pending_ |
| M04 baseline | ~43.34 | — (see M04 run notes) |

### Extended (optional)

| Run | `model_dir` | chrF | BLEU | Notes |
|-----|-------------|------|------|--------|
| M05 control | `outputs/m05_t5_control_aligned` | _pending_ | _pending_ | 3-epoch aligned-only |
| M05 augmented | `outputs/m05_t5_augmented` | _pending_ | _pending_ | 542-row augmented CSV |

---

## Interpretation (fill after GPU runs)

Answer **all** after both evals complete:

1. Did augmented beat **M04 baseline (~43.34)**?
2. Did augmented beat **M05 control**?
3. **Δ vs control** = augmented chrF − control chrF = _pending_
4. **Augmentation types** (from Run 1 builder): `direct_aid_strict` 236; `expanded_partial_prefix` 296; `expanded_partial_prefix_relaxed` 8; `expanded_english_resplit` 2.
5. **Readout:** real improvement vs neutral vs regression? (be explicit and conservative.)

### Success criteria (locked)

| Outcome | Condition |
|---------|-----------|
| **FAIL** | augmented ≤ control **or** augmented ≤ ~43.34 |
| **SUCCESS** | augmented **>** ~43.34 **and** augmented **>** control |
| **STRONG** | augmented **≥** 45 |
| **EXCEPTIONAL** | augmented **≥** 47 |

---

## Decision label (REQUIRED after measurement)

Choose **exactly one** once the results table is filled from **local** GPU eval:

* `M05 success candidate — augmented beats baseline and control`
* `M05 neutral — augmented does not clearly beat control`
* `M05 regression — augmentation hurts`

**Until then:**

```text
M05 decision pending — GPU training/eval not executed in this environment (CUDA unavailable); run Steps 1–3 locally and assign one label above from measured chrF.
```

---

## Expected artifacts (after local completion)

* `outputs/m05_t5_control_aligned/`
* `outputs/m05_t5_augmented/`
* `outputs/eval_m05_control/`
* `outputs/eval_m05_augmented/`
* `outputs/experiments_m05_control/` / `outputs/experiments_m05_augmented/`

---

## Exit criteria (from plan)

| Tier | chrF |
|------|------|
| Minimum | **> 43.34** |
| Strong | **≥ 45** |
| Exceptional | **≥ 47** |

---

## Submission

No Kaggle submission until dev chrF validates improvement (project discipline).
