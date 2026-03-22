# M04 — Tool calls log

**Plan:** [M04_plan.md](M04_plan.md)

| Timestamp (UTC) | Action | Result / notes |
|-----------------|--------|----------------|
| 2026-03-22T00:00:00Z | Init | Folder seeded at M03 closeout. |
| 2026-03-22T09:00:00Z | Branch | `m04-sentence-alignment` from `main`. |
| 2026-03-22T09:05:00Z | Docs | Replaced `M04_plan.md` with full implementation plan. |
| 2026-03-22T09:10:00Z | Data | Located aid CSV at `data/Sentences_Oare_FirstWord_LinNum.csv`; audited coverage (253 train docs). |
| 2026-03-22T09:20:00Z | Code | Added `data/alignment.py`, `pipeline/align.py`, `train --resume-model-dir`, config defaults, README M04 section. |
| 2026-03-22T09:35:00Z | Tests | `tests/test_m04_alignment.py` + `tests/fixtures/m04_alignment/*`; `pytest` + `ruff` green. |
| 2026-03-22T09:40:00Z | Eval | `python -m akk2eng.pipeline.eval --quiet` refreshed `outputs/eval/metrics.json` (chrF ~39.86). |
| 2026-03-22T09:45:00Z | Align | `python -m akk2eng.pipeline.align` + `--audit-only`; run notes in `M04_run1_*`, `M04_run2_*`. |
| 2026-03-22T10:00:00Z | Mix + train | `mix_train`; multi `--train-csv`; Exp1/Exp2 train + eval → `M04_run3_training_eval.md`. |
| 2026-03-22T12:00:00Z | GPU confirm | Attempted aligned `epochs=3` `--device cuda`; CUDA unavailable in session → doc-only block in `M04_run3_training_eval.md`. |
| 2026-03-22T14:00:00Z | Aligned full | `train` 3 ep `--device auto` (CPU) → `m04_t5_aligned_full`; `eval` → `eval_m04_aligned_full`; `M04_run3` metrics + leakage note. |

## Copy-paste anchors

```bash
# Alignment build
python -m akk2eng.pipeline.align

# Phase A audit JSON
python -m akk2eng.pipeline.align --audit-only

# Dev eval (default checkpoint)
python -m akk2eng.pipeline.eval --train-csv data/train.csv --model-dir outputs/m01_t5

# Mixed CSV build
python -m akk2eng.pipeline.mix_train

# M04 continuation train (after aligned CSV exists)
python -m akk2eng.pipeline.train \
  --train-csv data/derived/alignment/aligned_train_sentences.csv \
  --resume-model-dir outputs/m01_t5 \
  --output-dir outputs/m04_t5_aligned \
  --device cuda --fp32

# Mixed continuation (or: --train-csv data/train.csv --train-csv data/derived/alignment/aligned_train_sentences.csv)
python -m akk2eng.pipeline.train \
  --train-csv data/derived/alignment/mixed_train.csv \
  --resume-model-dir outputs/m01_t5 \
  --output-dir outputs/m04_t5_mixed \
  --device cuda --fp32
```
