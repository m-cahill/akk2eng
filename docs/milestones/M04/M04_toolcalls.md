# M04 — Tool calls log

**Plan:** [M04_plan.md](M04_plan.md)

| Timestamp | Action | Result / notes |
|-----------|--------|----------------|
| 2026-03-22T00:00:00Z | Init | Folder seeded at M03 closeout; populate as M04 executes. |

## Copy-paste anchors

```bash
# Dev eval (after M04 data path exists)
python -m akk2eng.pipeline.eval --train-csv data/train.csv --model-dir outputs/m01_t5

# Error buckets
python -m akk2eng.pipeline.analyze_errors
```
