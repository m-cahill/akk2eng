# M06 — Run 2 — Training + eval (3-run matrix)

**Purpose:** Run the **locked** local GPU matrix and record dev **chrF** under the frozen eval contract (beam=3, lexicon on, normalization v2).

**Plan:** [M06_plan.md](M06_plan.md)  
**Commands:** [M06_local_gpu_execution.md](M06_local_gpu_execution.md)

---

## Preconditions

- [x] `M06_run1_policy_builder.md` complete: Policy A/B CSVs + reports on disk, `dev_overlap_oare_ids == 0`
- [x] Policy parameters **frozen** — no threshold/cap tuning after seeing metrics

---

## Results (locked — M06 closeout)

Eval contract: same as M02/M04/M05 (frozen dev split, continuation from `outputs/m01_t5`, **3 epochs**, `--fp32`).

| Run | `train-csv` | chrF | BLEU | Notes |
|-----|---------------|------|------|--------|
| **Control** | `data/derived/alignment/aligned_train_sentences_split.csv` | **45.3584** | *(see local `metrics.json`)* | same-run comparator |
| **Policy A** | `data/derived/selection/strict_plus_highconf_cap50.csv` | **52.2530** | *(see local `metrics.json`)* | gated + cap |
| **Policy B** | `data/derived/selection/strict_plus_highconf_cap50_weighted2x.csv` | **25.4027** | *(see local `metrics.json`)* | 2× strict weighting — **regression** |

**Paths to metrics (canonical):** `outputs/eval_m06_control/metrics.json`, `outputs/eval_m06_policy_a/metrics.json`, `outputs/eval_m06_policy_b/metrics.json`.

---

## Locked paste-back (audit)

```text
Control chrF: 45.3584
Policy A chrF: 52.2530
Policy B chrF: 25.4027
Best Δ vs control: +6.8946
Decision: M06 success candidate — quality-gated expansion beats control
```

**Success vs plan:** Policy A beats same-run control by **+6.8946 chrF** (> **+0.5** band) and beats the prior pin **45.3584 chrF**. **Decision label:** success candidate.

---

## Decision (locked label)

**Chosen label:**

```text
M06 success candidate — quality-gated expansion beats control
```

**Rationale (short):** Only **two** high-confidence expansion rows passed Policy A gates; adding them to **236** strict rows improved dev chrF materially. Policy B duplicated strict supervision without adding signal and correlated with **collapse** (~25 chrF), showing that **dilution / reweighting** can reintroduce harm even when row identity matches Policy A.

---

## Submission

Kaggle submit runbook: [M06_run3_kaggle_submit.md](M06_run3_kaggle_submit.md) (authorized after success-candidate gate).
