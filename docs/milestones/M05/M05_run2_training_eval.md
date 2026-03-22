# M05 — Run 2: Training + eval vs M04 baseline

**Milestone:** M05  
**Baseline to beat:** dev chrF **≈ 43.34** (M04 split-safe aligned-only, 3 epochs, same eval contract as M02/M04).

---

## Execution status (this session)

| Phase | Status |
|--------|--------|
| Augmentation builder (`--split-safe`) | **Done** — see [M05_run1_augmentation_builder.md](M05_run1_augmentation_builder.md) |
| Control + augmented **3-epoch GPU** train | **Not run here** — `torch.cuda.is_available()` was **False** in the execution environment |
| Eval on `m05_t5_*` checkpoints | **Pending** — requires local GPU training first |

**Milestone-grade chrF numbers below are intentionally unfilled until you run train + eval on CUDA** (e.g. RTX 5090 / cu128 per `docs/akk2eng.md`). Do **not** treat long CPU runs as the milestone comparison surface.

---

## Training (3 epochs — milestone comparison)

**Augmented continuation fine-tune:**

```bash
python -m akk2eng.pipeline.train \
  --train-csv data/derived/augmentation/augmented_train_sentences.csv \
  --resume-model-dir outputs/m01_t5 \
  --output-dir outputs/m05_t5_augmented \
  --device cuda --fp32 \
  --epochs 3
```

**Control (same-run aligned-only):** train on split-safe aligned CSV only (M04 path):

```bash
python -m akk2eng.pipeline.train \
  --train-csv data/derived/alignment/aligned_train_sentences_split.csv \
  --resume-model-dir outputs/m01_t5 \
  --output-dir outputs/m05_t5_control_aligned \
  --device cuda --fp32 \
  --epochs 3
```

> Run **control first**, then **augmented**, without changing augmentation code between the builder run and training.

---

## Evaluation

Same contract as M04 (frozen dev, beam=3, lexicon on, normalization v2):

```bash
python -m akk2eng.pipeline.eval --model-dir outputs/m05_t5_control_aligned
python -m akk2eng.pipeline.eval --model-dir outputs/m05_t5_augmented
```

(Mirror any extra flags used in `docs/milestones/M04/M04_run3_training_eval.md` if your local harness differs from defaults.)

---

## Results table (fill after GPU runs)

| Run | `model_dir` | chrF | BLEU | Notes |
|-----|-------------|------|------|--------|
| M04 reference | `M04_run3` / notes | ~43.34 | _see M04_ | historical split-safe aligned-only |
| M05 control | `outputs/m05_t5_control_aligned` | _pending_ | _pending_ | 3-epoch, same env as augmented |
| M05 augmented | `outputs/m05_t5_augmented` | _pending_ | _pending_ | expanded CSV (542 rows) |

---

## Interpretation (fill after GPU runs)

Answer after both evals complete:

1. **Pinned M04 baseline (~43.34):** Did augmented chrF **>** ~43.34?
2. **Same-run control:** Did augmented chrF **>** control chrF? (Catches env / training variance.)
3. **Augmentation types:** See Run 1 — `direct_aid_strict` 236; `expanded_partial_prefix` 296; `expanded_partial_prefix_relaxed` 8; `expanded_english_resplit` 2.
4. **Readout:** Real gain vs neutral vs regression?

### Success criteria (locked)

| Outcome | Condition |
|---------|-----------|
| **M05 fails** | augmented ≤ control **or** augmented ≤ ~43.34 |
| **M05 minimum success** | augmented **>** ~43.34 **and** augmented **>** control |
| **Strong success** | augmented **≥** 45 **and** clearly above control |
| **Exceptional** | augmented **≥** 47 |

---

## Decision labeling (after GPU metrics exist)

Pick **one** when the table is filled:

* `M05 success candidate — augmented beats baseline and control`
* `M05 neutral — augmented does not clearly beat control`
* `M05 regression — augmentation hurts`

**Current (pre-GPU):** **`M05 decision pending — training/eval not executed (CUDA unavailable in builder session).`**

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
