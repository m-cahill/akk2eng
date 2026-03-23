# M08 — Local GPU execution (RTX 5090 / CUDA workstation)

**Milestone:** M08 — Alignment-quality recovery  
**Environment:** User machine with CUDA + PyTorch built for the GPU (see `README.md` / M01-A Blackwell notes). Run from **repository root**.

## Preconditions

- Builder finished: `data/derived/alignment_quality/*.csv` + JSON reports exist.
- `early_no_op_stop_recommended` is **false** (otherwise skip this file entirely).

## Train (3 epochs, FP32, resume M01 checkpoint)

```bash
python -m akk2eng.pipeline.train \
  --train-csv data/derived/selection/strict_plus_highconf_cap50.csv \
  --resume-model-dir outputs/m01_t5 \
  --output-dir outputs/m08_t5_baseline_m06_policy_a \
  --device cuda --fp32 \
  --epochs 3

python -m akk2eng.pipeline.train \
  --train-csv data/derived/alignment_quality/aligned_train_sentences_quality_v2_split.csv \
  --resume-model-dir outputs/m01_t5 \
  --output-dir outputs/m08_t5_alignment_quality_v2 \
  --device cuda --fp32 \
  --epochs 3

python -m akk2eng.pipeline.train \
  --train-csv data/derived/alignment_quality/aligned_train_sentences_quality_v2_plus_m06.csv \
  --resume-model-dir outputs/m01_t5 \
  --output-dir outputs/m08_t5_alignment_quality_v2_plus_m06 \
  --device cuda --fp32 \
  --epochs 3
```

## Eval (frozen dev contract)

```bash
python -m akk2eng.pipeline.eval --model-dir outputs/m08_t5_baseline_m06_policy_a --output-dir outputs/eval_m08_baseline
python -m akk2eng.pipeline.eval --model-dir outputs/m08_t5_alignment_quality_v2 --output-dir outputs/eval_m08_alignment_quality_v2
python -m akk2eng.pipeline.eval --model-dir outputs/m08_t5_alignment_quality_v2_plus_m06 --output-dir outputs/eval_m08_alignment_quality_v2_plus_m06
```

Record chrF from each `outputs/eval_m08_*/metrics.json` into **`M08_run2_training_eval.md`**.
