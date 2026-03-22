# M06 — Run 2 — Training + eval (3-run matrix)

**Purpose:** Run the **locked** local GPU matrix and record dev **chrF** under the frozen eval contract (beam=3, lexicon on, normalization v2).

**Plan:** [M06_plan.md](M06_plan.md)  
**Commands:** [M06_local_gpu_execution.md](M06_local_gpu_execution.md)

---

## Preconditions

- [ ] `M06_run1_policy_builder.md` complete: Policy A/B CSVs + reports on disk, `dev_overlap_oare_ids == 0`
- [ ] Policy parameters **frozen** — no threshold/cap tuning after seeing metrics

---

## Results (paste after GPU runs)

Eval contract: same as M02/M04/M05 (frozen dev split, continuation from `outputs/m01_t5`, **3 epochs**, `--fp32`).

| Run | `train-csv` | chrF | BLEU | Notes |
|-----|---------------|------|------|--------|
| **Control** | `data/derived/alignment/aligned_train_sentences_split.csv` | | | same-run comparator |
| **Policy A** | `data/derived/selection/strict_plus_highconf_cap50.csv` | | | |
| **Policy B** | `data/derived/selection/strict_plus_highconf_cap50_weighted2x.csv` | | | |

**Paths to metrics:** `outputs/eval_m06_control/metrics.json`, `outputs/eval_m06_policy_a/metrics.json`, `outputs/eval_m06_policy_b/metrics.json` (or as adjusted locally — keep one canonical mapping here after the run).

---

## Decision (locked label — pick exactly one)

Reference pin: **45.3584** chrF (M05 control). Same-run control is the primary comparator. Noise band: **±0.5** chrF.

**Chosen label:**

```text
(paste one of the three labels from M06_plan.md §9)
```

**Rationale (short):**

---

## Paste-back template (for chat / audit)

```text
Control chrF:
Policy A chrF:
Policy B chrF:
Best Δ vs control:
Decision:
```

---

## Submission

Per plan: **no** `M06_run3_kaggle_submit.md` unless a candidate clears the **success candidate** gate in §9 of `M06_plan.md`.
