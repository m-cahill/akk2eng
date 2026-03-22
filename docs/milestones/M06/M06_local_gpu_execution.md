# M06 — Local GPU execution (RTX 5090 / locked matrix)

**Milestone:** M06  
**Device:** CUDA workstation (e.g. RTX 5090); use **`--fp32`** per project Blackwell guidance.

**Before this:** complete [M06_run1_policy_builder.md](M06_run1_policy_builder.md) so `data/derived/selection/*.csv` exist and reports show **0** dev overlap.

---

## 1. Training (3 × 3 epochs)

Run from **repository root** with venv activated and CUDA PyTorch installed.

### Control

```bash
python -m akk2eng.pipeline.train \
  --train-csv data/derived/alignment/aligned_train_sentences_split.csv \
  --resume-model-dir outputs/m01_t5 \
  --output-dir outputs/m06_t5_control_aligned \
  --device cuda --fp32 \
  --epochs 3
```

### Policy A

```bash
python -m akk2eng.pipeline.train \
  --train-csv data/derived/selection/strict_plus_highconf_cap50.csv \
  --resume-model-dir outputs/m01_t5 \
  --output-dir outputs/m06_t5_policy_a \
  --device cuda --fp32 \
  --epochs 3
```

### Policy B

```bash
python -m akk2eng.pipeline.train \
  --train-csv data/derived/selection/strict_plus_highconf_cap50_weighted2x.csv \
  --resume-model-dir outputs/m01_t5 \
  --output-dir outputs/m06_t5_policy_b \
  --device cuda --fp32 \
  --epochs 3
```

---

## 2. Eval (frozen contract)

```bash
python -m akk2eng.pipeline.eval --model-dir outputs/m06_t5_control_aligned --output-dir outputs/eval_m06_control
python -m akk2eng.pipeline.eval --model-dir outputs/m06_t5_policy_a --output-dir outputs/eval_m06_policy_a
python -m akk2eng.pipeline.eval --model-dir outputs/m06_t5_policy_b --output-dir outputs/eval_m06_policy_b
```

Copy **chrF** / **BLEU** from each `metrics.json` into [M06_run2_training_eval.md](M06_run2_training_eval.md) and apply the §9 decision rules from [M06_plan.md](M06_plan.md).

---

## 3. Paste-back

```text
Control chrF:
Policy A chrF:
Policy B chrF:
Best Δ vs control:
Decision:
```
