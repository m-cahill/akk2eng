# M07 — Tool calls log

**Plan:** [M07_plan.md](M07_plan.md)

| Timestamp (UTC) | Action | Result / notes |
|-----------------|--------|----------------|
| 2026-03-22T00:00:00Z | Seed | Folder created at M06 closeout (`v0.0.9-m06`). **No implementation yet.** |
| 2026-03-22T12:00:00Z | Branch | `git checkout -b m07-confidence-driven-expansion` from `main`. |
| 2026-03-22T12:05:00Z | Docs | Overwrote `M07_plan.md` with locked operational plan (user paste). |
| 2026-03-22T12:30:00Z | Code | Added `src/akk2eng/data/confidence.py`, `pipeline/select_confident_train.py`, `config.DEFAULT_CONFIDENCE_OUTPUT_DIR`. |
| 2026-03-22T12:45:00Z | Tests | Added `tests/test_m07_confidence.py`, `tests/fixtures/m07_confidence/*.csv`. |
| 2026-03-22T13:00:00Z | Local run | `python -m akk2eng.pipeline.select_confident_train` — cap6/cap10 built; dev overlap 0; M06 winners preserved. |
| 2026-03-22T13:10:00Z | Docs | Added `M07_run1_confidence_builder.md`, `M07_run2_training_eval.md`, `M07_local_gpu_execution.md`; README M07 blurb. |
| 2026-03-22T13:15:00Z | Verify | `pytest tests -q`, `ruff check src tests` — green. |
| 2026-03-22T18:00:00Z | Closeout | `M07_summary.md`, `M07_audit.md`; `M07_run2_training_eval.md` final metrics; `docs/akk2eng.md` ledger; seed `M08/`; tag `v0.0.10-m07`; merge → `main`. |

## Copy-paste anchors

```bash
python -m pytest tests -q
python -m ruff check src tests
python -m akk2eng.pipeline.select_confident_train
```
