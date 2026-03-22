# M06 — Tool calls log

**Plan:** [M06_plan.md](M06_plan.md)

| Timestamp (UTC) | Action | Result / notes |
|-----------------|--------|----------------|
| 2026-03-22T00:00:00Z | Seed | Folder created at M05 closeout (`v0.0.8-m05`). **No implementation yet.** |
| 2026-03-22T12:00:00Z | Branch | `git checkout main` @ `bde8dcb`; `git checkout -b m06-precision-preserving-expansion`. |
| 2026-03-22T12:00:00Z | Implement | Phases 1–3: `selection.py`, `select_train.py`, `config`, tests, docs, `M06_plan.md` replace. |
| 2026-03-22T14:30:00Z | Verify | `pytest tests`, `ruff check src tests` — green after M06 implementation. |
| 2026-03-22T18:00:00Z | Closeout | `M06_summary.md`, `M06_audit.md`, `M06_run3_kaggle_submit.md`, run1/2 updates, `docs/akk2eng.md`, seed `M07/`; merge + tag `v0.0.9-m06`. |

## Copy-paste anchors

```bash
python -m pytest tests -q
python -m ruff check src tests
```
