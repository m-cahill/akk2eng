# M06 — Run 3 — Kaggle submission (Policy A)

**Milestone:** M06  
**Authority:** Dev **success candidate** satisfied — see [M06_run2_training_eval.md](M06_run2_training_eval.md).

---

## Model checkpoint

- **Fine-tuned weights (local):** `outputs/m06_t5_policy_a`  
- **Training CSV:** `data/derived/selection/strict_plus_highconf_cap50.csv` (**236** strict + **2** expansion)  
- **Continuation base:** `outputs/m01_t5` (per locked matrix)

---

## Expected improvement (hypothesis vs baseline)

- **M01 public LB reference:** **11.9** (see `docs/akk2eng.md`, `M01_run3.md`).  
- Policy A improves **dev chrF** materially vs same-run control; **public leaderboard movement is not guaranteed** and must be measured on submit.

---

## Local submission generation (reference)

From repo root, with competition `data/test.csv` present:

```bash
python -m akk2eng.pipeline.run \
  --model-dir outputs/m06_t5_policy_a \
  --output outputs/submission_m06_policy_a.csv
```

Use **`--test-csv`** / **`--output`** overrides as needed. Ensure notebook path on Kaggle matches repo **decode contract** (beam=3, lexicon, normalization v2) per M02/M06 governance.

---

## Leaderboard log (fill after submit — do not fabricate)

```text
Public LB:
Private LB:
```

**Notes:** *(date, notebook version, any runtime caveats)*
