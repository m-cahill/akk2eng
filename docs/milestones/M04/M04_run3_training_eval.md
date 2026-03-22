# M04 Run 3 — Training / eval (placeholder)

**Status:** Not run in-repo during initial M04 implementation pass.

**Planned Experiment 1 (sentence-aligned continuation):**

```bash
python -m akk2eng.pipeline.train \
  --train-csv data/derived/alignment/aligned_train_sentences.csv \
  --resume-model-dir outputs/m01_t5 \
  --output-dir outputs/m04_t5_aligned \
  --device cuda --fp32
```

Then:

```bash
python -m akk2eng.pipeline.eval --model-dir outputs/m04_t5_aligned
```

Record under `outputs/experiments/exp_<UTC>/`: `config.json`, `metrics.json`, `predictions_dev.csv`.

**Baseline to beat:** chrF **~39.86** (see [M04_run1_baseline_and_data_audit.md](M04_run1_baseline_and_data_audit.md)).

**Experiment 2:** only if Exp 1 is worse or inconclusive — single bounded mixed/curriculum fallback per [M04_plan.md](M04_plan.md).
