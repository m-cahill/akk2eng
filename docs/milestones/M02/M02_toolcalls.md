# M02 — Tool calls log

| Timestamp | Action | Result / notes |
|-----------|--------|----------------|
| | | |

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
# Dev eval (placeholder — implement per M02_plan Step 2)
python -m akk2eng.pipeline.validate --train-csv data/train.csv --model-dir outputs/m01_t5

# Local submission smoke (unchanged contract)
python -m akk2eng.pipeline.run --model-dir outputs/m01_t5
```
