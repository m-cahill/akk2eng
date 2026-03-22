# M03 — Tool calls log

**Plan:** [M03_plan.md](M03_plan.md)

| Timestamp | Action | Result / notes |
|-----------|--------|----------------|
| 2026-03-21T00:00:00Z | Implementation start | Locked answers: normalize in `run_inference`, inputs only, **no** hyphen→space, dup-collapse `len>=3`, inference-only. |
| 2026-03-21T00:00:01Z | Write / edit | Add `src/akk2eng/data/normalize.py`, `config` flags, wire `inference.py` + `eval.py` artifacts + optional `--no-normalization`. |
| 2026-03-21T00:00:02Z | Tests | Add `tests/test_m03_normalize.py`, run `pytest`. |
| 2026-03-21T00:00:03Z | Docs | Update `M03_plan.md`, add `M03_run1_normalization.md`; optional `docs/akk2eng.md` M03 note. |
| 2026-03-22T07:03:00Z | Eval (background) | `python -m akk2eng.pipeline.eval --quiet` — may load HF base if `outputs/m01_t5` missing; user should run with real checkpoint + `data/train.csv` and paste chrF into `M03_run1_normalization.md`. |
| 2026-03-22T07:10:00Z | pytest / ruff | Full suite **27 passed**; ruff clean on touched files. |
| 2026-03-22T12:00:00Z | eval A/B | `pipeline.eval` norm ON then OFF; `analyze_errors` per run; populate `M03_run1_normalization.md`. |
| 2026-03-22T12:45:00Z | eval restore | Re-ran norm **ON** eval so `outputs/eval/` matches `USE_NORMALIZATION=True`. |
| 2026-03-22T12:50:00Z | Docs | `M03_run1_normalization.md` filled; `SUBMIT_TO_KAGGLE=NO`; `docs/akk2eng.md` M03 row updated. |
| 2026-03-22T14:00:00Z | M03.2 code | `normalize.py` v2: drop NFKC+lowercase; `NORMALIZATION_VERSION=v2`; tests + eval A/B + `M03_run2_conservative_norm.md`. |
| 2026-03-22T14:40:00Z | Eval v2 | chrF/BLEU/buckets **identical** ON vs OFF on dev (39.8601); `outputs/eval` restored norm ON; `docs/akk2eng.md` + `M03_plan.md` updated. |
| 2026-03-22T16:00:00Z | M03 closeout | Added `M03_summary.md`, `M03_audit.md`; `akk2eng.md` M03 section + tag `v0.0.6-m03`; seeded `M04/` (no code/experiments). |

## Copy-paste anchors

```bash
# Dev eval (after normalization is wired)
python -m akk2eng.pipeline.eval --train-csv data/train.csv --model-dir outputs/m01_t5

# Error buckets
python -m akk2eng.pipeline.analyze_errors
```
