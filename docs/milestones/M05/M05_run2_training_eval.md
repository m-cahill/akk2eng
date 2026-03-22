# M05 — Run 2: Training + eval vs M04 baseline

**Milestone:** M05  
**Status:** **Complete** (local GPU, 2026-03-22)

---

## Execution status

| Phase | Status |
|--------|--------|
| Augmentation builder | **Done** — [M05_run1_augmentation_builder.md](M05_run1_augmentation_builder.md) |
| Control 3-epoch GPU train | **Done** → `outputs/m05_t5_control_aligned` |
| Augmented 3-epoch GPU train | **Done** → `outputs/m05_t5_augmented` |
| Eval (both) | **Done** → `outputs/eval_m05_control`, `outputs/eval_m05_augmented` |

**Eval commands used (as-run):**

```bash
python -m akk2eng.pipeline.eval --model-dir outputs/m05_t5_control_aligned --output-dir outputs/eval_m05_control
python -m akk2eng.pipeline.eval --model-dir outputs/m05_t5_augmented --output-dir outputs/eval_m05_augmented
```

(Optional mirrored experiment dirs: `--experiments-dir outputs/experiments_m05_*` — not required for metrics.)

---

## Training commands (reference)

**Control (run first):**

```bash
python -m akk2eng.pipeline.train \
  --train-csv data/derived/alignment/aligned_train_sentences_split.csv \
  --resume-model-dir outputs/m01_t5 \
  --output-dir outputs/m05_t5_control_aligned \
  --device cuda --fp32 \
  --epochs 3
```

**Augmented:**

```bash
python -m akk2eng.pipeline.train \
  --train-csv data/derived/augmentation/augmented_train_sentences.csv \
  --resume-model-dir outputs/m01_t5 \
  --output-dir outputs/m05_t5_augmented \
  --device cuda --fp32 \
  --epochs 3
```

---

## Results table (as-run)

| Run | chrF | BLEU |
|-----|------|------|
| M05 control | **45.3584** | **63.8998** |
| M05 augmented | **20.3932** | **12.7255** |
| M04 baseline (historical pin) | **~43.34** | — |

**Δ vs control:** **20.3932 − 45.3584 = −24.9652** chrF.

### Extended

| Run | `model_dir` | chrF | BLEU | Notes |
|-----|-------------|------|------|--------|
| M05 control | `outputs/m05_t5_control_aligned` | 45.3584 | 63.8998 | 236 rows, 177 steps |
| M05 augmented | `outputs/m05_t5_augmented` | 20.3932 | 12.7255 | 542 rows, 408 steps |

---

## Interpretation

1. **vs M04 baseline (~43.34):** Augmented (**20.39**) **did not** beat the historical pin; it **collapsed** vs it.
2. **vs M05 control:** Augmented **did not** beat control; **large regression**.
3. **Δ vs control:** **≈ −24.97 chrF** (primary milestone discriminator).
4. **Augmentation types** (builder): `direct_aid_strict` **236**; `expanded_partial_prefix` **296**; `expanded_partial_prefix_relaxed` **8**; `expanded_english_resplit` **2**. Most added mass is **partial-prefix**—M05 effectively tested whether that recall path adds usable signal when mixed unweighted with strict pairs.
5. **Readout:** **Regression.** Sample augmented outputs skewed **short / generic** (e.g. witness boilerplate) vs control’s fuller translations—consistent with **noisy or mis-paired** supervision **diluting** the high-confidence strict signal.

**Control vs M04 pin:** Control **45.36** > historical **~43.34** → treat **same-run augmented vs control** as authoritative; historical baseline is a **sanity bracket**, not the only comparator.

### Success criteria (locked) — outcome

| Gate | Result |
|------|--------|
| FAIL if augmented ≤ control or ≤ ~43.34 | **FAIL** (both) |
| SUCCESS if augmented > ~43.34 and > control | **Not met** |

---

## Decision label (REQUIRED)

```text
M05 regression — augmentation hurts
```

---

## Artifacts (local, gitignored)

* `outputs/m05_t5_control_aligned/`
* `outputs/m05_t5_augmented/`
* `outputs/eval_m05_control/metrics.json`
* `outputs/eval_m05_augmented/metrics.json`

---

## Submission

No Kaggle submission (dev regression; project discipline).

---

## Runbook

[M05_local_gpu_execution.md](M05_local_gpu_execution.md)
