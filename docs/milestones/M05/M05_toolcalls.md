# M05 — Tool calls log

**Plan:** [M05_plan.md](M05_plan.md)

| Timestamp (UTC) | Action | Result / notes |
|-----------------|--------|----------------|
| 2026-03-22T00:00:00Z | Seed | Folder and plan stub created at M04 closeout (`v0.0.7-m04`). **No implementation yet.** |
| 2026-03-22T12:00:00Z | git | `git checkout -b m05-data-augmentation` — start M05 implementation. |
| 2026-03-22T12:00:00Z | write | Replace `M05_plan.md`, add `augmentation.py`, `pipeline/augment.py`, config, tests, run docs. |
| 2026-03-22T14:30:00Z | pytest / ruff | `pytest tests -q`, `ruff check src tests` — green after M05 implementation. |
| 2026-03-22T18:00:00Z | `python -m akk2eng.pipeline.augment --split-safe` | Built `augmented_train_sentences.csv` (542 rows, sha256 in `M05_run1`); dev overlap 0; CUDA false → no GPU train/eval in session. |
| 2026-03-22T20:00:00Z | CUDA check | `torch.cuda.is_available()` False — M05 GPU train/eval **not started**; `M05_run2` updated with explicit eval `--output-dir` / `--experiments-dir` commands; decision label remains pending local GPU. |
| 2026-03-22T21:00:00Z | write | Added `M05_local_gpu_execution.md` (local RTX/CUDA runbook); linked from `M05_run2` + `M05_plan.md`. |

## Copy-paste anchors

```bash
# (M05) — populate after kickoff
python -m pytest tests -q
python -m ruff check src tests
```
