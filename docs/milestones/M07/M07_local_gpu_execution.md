# M07 — Local GPU execution (RTX 5090 / locked matrix)

**Milestone:** M07  
**Device:** CUDA workstation (e.g. **RTX 5090** / Blackwell); use **`--fp32`** per project guidance.  

**Before this:**

1. [M07_run1_confidence_builder.md](M07_run1_confidence_builder.md) complete — `data/derived/confidence/*.csv` and reports exist, **0** dev overlap.  
2. `outputs/m01_t5` checkpoint present (M06 continuation contract).  
3. Frozen split files under `data/splits/`.

---

## 1. Training (3 × 3 epochs)

Run from **repository root** with venv activated and CUDA PyTorch installed (e.g. `torch` **2.10+cu128** for sm_120).

### Baseline (M06 winner rerun)

```bash
python -m akk2eng.pipeline.train \
  --train-csv data/derived/selection/strict_plus_highconf_cap50.csv \
  --resume-model-dir outputs/m01_t5 \
  --output-dir outputs/m07_t5_baseline_m06_policy_a \
  --device cuda --fp32 \
  --epochs 3
```

### Candidate A (cap6)

```bash
python -m akk2eng.pipeline.train \
  --train-csv data/derived/confidence/strict_plus_confv2_cap6.csv \
  --resume-model-dir outputs/m01_t5 \
  --output-dir outputs/m07_t5_cap6 \
  --device cuda --fp32 \
  --epochs 3
```

### Candidate B (cap10)

```bash
python -m akk2eng.pipeline.train \
  --train-csv data/derived/confidence/strict_plus_confv2_cap10.csv \
  --resume-model-dir outputs/m01_t5 \
  --output-dir outputs/m07_t5_cap10 \
  --device cuda --fp32 \
  --epochs 3
```

---

## 2. Eval (frozen dev)

```bash
python -m akk2eng.pipeline.eval --model-dir outputs/m07_t5_baseline_m06_policy_a --output-dir outputs/eval_m07_baseline
python -m akk2eng.pipeline.eval --model-dir outputs/m07_t5_cap6 --output-dir outputs/eval_m07_cap6
python -m akk2eng.pipeline.eval --model-dir outputs/m07_t5_cap10 --output-dir outputs/eval_m07_cap10
```

Record **chrF** / **BLEU** from each `outputs/eval_m07_*/metrics.json` into [M07_run2_training_eval.md](M07_run2_training_eval.md) and apply the locked decision rules from `M07_plan.md` §10.

---

## 3. Notes

- Do **not** change decoding, normalization, lexicon defaults, or epochs for this matrix.  
- Training may show small run-to-run variance; **same-run** baseline vs candidates in one session is the primary comparison.  
- Kaggle submission only if a candidate clears the **success candidate** gate in `M07_plan.md` §11 — then add `M07_run3_kaggle_submit.md`.
