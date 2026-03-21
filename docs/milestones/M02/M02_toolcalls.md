# M02 — Tool calls log

**Tactical sprint:** see [M02_plan.md — Quick +5 score strategy](M02_plan.md#quick-5-score-strategy-tactical-sprint).

| Timestamp | Action | Result / notes |
|-----------|--------|----------------|
| 2026-03-21 | M02-C: `repetition_penalty=1.2`, `no_repeat_ngram_size=3` in `T5BaselineTranslator.generate` | Dev chrF 18.65→34.41; repetition bucket 87.8%→73.7%; see [M02_run1_m02c_decoding.md](M02_run1_m02c_decoding.md) |
| 2026-03-21 | M02-C.1: Kaggle notebook `generate()` updated to match repo decode | Log template: [M02_run2_kaggle.md](M02_run2_kaggle.md); fill public LB after submit |

## Targeted error analysis workflow (checklist)

Use with **frozen** dev predictions + references (same seed / split as eval). See **Step 3** in [M02_plan.md](M02_plan.md).

| Step | Done | Notes |
|------|------|--------|
| Table built (`transliteration`, `reference`, `prediction`) | [ ] | e.g. `outputs/eval/dev_predictions.csv` |
| Bucket tags applied | [ ] | repetition, lexical, numeric, under-translation, overlap/drift |
| Counts + ranked top bucket | [ ] | paste summary row below |
| Human samples + hypothesis | [ ] | link or paste in this file |
| Next experiment ID + single lever | [ ] | must cite bucket |

**Top bucket this sprint:** *(name + count)*  
**Hypothesis:**  
**Planned lever:**  

---

## Copy-paste anchors (fill as M02 lands)

```bash
# Dev eval + metrics (M02-A)
python -m akk2eng.pipeline.eval --train-csv data/train.csv --model-dir outputs/m01_t5

# Error buckets (M02-B)
python -m akk2eng.pipeline.analyze_errors

# Local submission smoke (unchanged contract)
python -m akk2eng.pipeline.run --model-dir outputs/m01_t5
```
