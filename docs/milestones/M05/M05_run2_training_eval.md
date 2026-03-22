# M05 — Run 2: Training + eval vs M04 baseline

**Milestone:** M05  
**Baseline to beat:** dev chrF **≈ 43.34** (M04 split-safe aligned-only, 3 epochs, same eval contract as M02/M04).

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

**Control (replication / regression check):** train on split-safe aligned CSV only (M04 path):

```bash
python -m akk2eng.pipeline.train \
  --train-csv data/derived/alignment/aligned_train_sentences_split.csv \
  --resume-model-dir outputs/m01_t5 \
  --output-dir outputs/m05_t5_control_aligned \
  --device cuda --fp32 \
  --epochs 3
```

> If CUDA is unavailable in the active environment, keep **implementation + commands** as above; use `--device cpu` only for short smokes. Milestone-grade numbers should be produced on **GPU** when available (RTX 5090 / cu128 posture per `docs/akk2eng.md`).

---

## Evaluation

Same contract as M04 (frozen dev, beam=3, lexicon on, normalization v2):

```bash
python -m akk2eng.pipeline.eval --model-dir outputs/m05_t5_augmented
```

(Adjust `--model-dir` for control run; mirror flags used in `M04_run3_training_eval.md`.)

---

## Results table (fill after runs)

| Run | `model_dir` | chrF | BLEU | Notes |
|-----|-------------|------|------|--------|
| M04 reference | _pinned in M04_run3_ | ~43.34 | _see M04_ | split-safe aligned-only |
| M05 control | `outputs/m05_t5_control_aligned` | _pending_ | _pending_ | 3-epoch replication |
| M05 augmented | `outputs/m05_t5_augmented` | _pending_ | _pending_ | expanded CSV |

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
