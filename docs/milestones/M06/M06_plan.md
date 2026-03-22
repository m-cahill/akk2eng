# M06 — Precision-preserving data expansion

**Milestone ID:** M06  
**Working title:** Precision-preserving data expansion  
**Target branch:** `m06-precision-preserving-expansion`  
**Audit target:** **5.0 / 5.0**  
**Baseline:** `main` at M06 start (post–M05 closeout governance)

**Milestone question:** Can a **small, deterministic, high-confidence, capped, strict-dominant** subset of M05 expansion rows beat **strict-only** training on the frozen dev split?

---

## Context (locked evidence from M05)

M05 proved that naive expansion was harmful. The split-safe augmented set grew from **236 strict rows** to **542 total**, with **296** of the added rows from **partial-prefix** alignment, and the augmented model fell to **20.39 chrF** versus **45.36 chrF** for the same-run strict-only control. The ledger records:

```text
Strict aligned > high-confidence expanded > partial-prefix > noisy synthetic
```

**No Kaggle submission without dev chrF improvement.** M06 is therefore a **selection-and-mixing** milestone, not a new augmentation-heuristics milestone.

---

## 1. Objective

Recover useful signal from the M05 expansion pipeline **without repeating the M05 mistake**. M06 tests whether **quality gating + strict-dominant mixing** can turn a subset of the M05 expansion rows into a net positive.

---

## 2. Locked constraints

These are not negotiable in M06:

- Keep the **existing evaluation contract**: frozen dev split, same training continuation path, **beam=3**, lexicon on, normalization v2.
- Keep the **same model family** and same general training recipe used in M05.
- Do **not** change decoding, normalization, model architecture, or lexicon behavior in M06.
- Do **not** invent new augmentation heuristics in M06.
- M06 may only operate on the **split-safe M05 superset** and apply **selection / weighting / caps**.
- No Kaggle submission unless a candidate beats the dev gate defined below.

---

## 3. Hypothesis

M05 failed because **low-confidence partial-prefix rows dominated the added mass** and diluted the high-signal strict pairs. M06 tests the opposite posture:

> Keep all strict rows, admit only a small high-confidence expansion slice, exclude relaxed paths, cap added mass, and keep strict rows dominant at sample time.

---

## 4. In scope

M06 includes only:

1. A deterministic **selection policy layer** on top of `augmented_train_sentences.csv`
2. Deterministic **policy reports** with hashes and row counts
3. A **weighted materialization** option that preserves strict-row dominance without changing the trainer
4. A locked **3-run local GPU matrix**:

   - strict-only control
   - Policy A
   - Policy B

5. Honest closeout with success / neutral / regression decision

---

## 5. Out of scope

Do not do any of the following in M06:

- new alignment heuristics
- back-translation
- noise augmentation
- lexicon redesign
- named-entity handling
- model swap / larger backbone
- decoding experiments
- Kaggle notebook refactor
- more than the locked run matrix unless explicitly opened as a later milestone

---

## 6. Experimental matrix

| Run          | Dataset                                                           | Purpose                                       |
| ------------ | ----------------------------------------------------------------- | --------------------------------------------- |
| **Control**  | `data/derived/alignment/aligned_train_sentences_split.csv`        | authoritative same-run comparator             |
| **Policy A** | `data/derived/selection/strict_plus_highconf_cap50.csv`           | test gating + cap only                        |
| **Policy B** | `data/derived/selection/strict_plus_highconf_cap50_weighted2x.csv` | test gating + cap + strict-dominant weighting |

---

## 7. Locked policy definitions

### Policy A — `strict_plus_highconf_cap50`

Start from the split-safe M05 source:

`data/derived/augmentation/augmented_train_sentences.csv`

Rules:

- Keep **all** `direct_aid_strict` rows.
- For expansion rows:

  - **drop any row whose `augmentation_type` contains `relaxed`** (case-insensitive substring)
  - allow only deterministic expansion rows from the existing M05 output
  - use existing `augmentation_confidence` as the **only** ranking score

- Threshold:

  - primary threshold: `augmentation_confidence >= 0.90`
  - fallback allowed **once only**: if fewer than **16** expansion rows survive at the primary threshold, lower threshold to `0.80` and record the fallback in the report

- Cap:

  - keep at most `floor(0.50 * strict_count)` expansion rows
  - with M05 strict count = 236, this caps expansion at **118** (when that strict count holds in the source file)

- Ranking / tie-break order:

  1. descending `augmentation_confidence`
  2. preferred type order: `expanded_english_resplit` before `expanded_partial_prefix`
  3. `source_row_id` (lexicographic as string)
  4. original row order

- Fail closed if `augmentation_confidence` is missing or non-numeric **anywhere** in the source CSV.
- Re-run dev-overlap verification and fail closed if non-zero.

### Policy B — `strict_plus_highconf_cap50_weighted2x`

Use the **exact same selected rows as Policy A**, then materialize a strict-dominant training CSV by:

- duplicating each strict row **2× total** (each strict appears twice in order)
- keeping each expansion row **1×**
- preserving stable row order across repeats
- documenting repeat factors in the report

This avoids trainer changes while still testing weighted supervision.

---

## 8. Implementation phases

### Phase 1 — selector and policy reports

Implemented as:

- `src/akk2eng/data/selection.py`
- `src/akk2eng/pipeline/select_train.py`

Outputs under gitignored `data/derived/selection/`:

- `strict_plus_highconf_cap50.csv`
- `strict_plus_highconf_cap50_report.json`
- `strict_plus_highconf_cap50_weighted2x.csv`
- `strict_plus_highconf_cap50_weighted2x_report.json`

Each report includes:

- source CSV SHA-256
- output CSV SHA-256
- strict row count
- selected expansion row count
- excluded relaxed row count
- `counts_by_augmentation_type` on the written training CSV
- confidence threshold used
- whether fallback was triggered
- cap value used
- strict / expanded effective sampling ratio
- `prerequisite_analysis` (source row counts, confidence summaries, counts ≥0.90 / ≥0.80 for non-relaxed expansion)
- dev overlap (`dev_overlap_oare_ids`, `dev_overlap_passes`; **0** overlap required)

### Phase 2 — tests and CI-safe verification

- `tests/test_m06_selection.py` + fixtures under `tests/fixtures/m06_selection/`
- M06 remains **CPU-only** in CI; no local competition data or GPU required.

### Phase 3 — docs and runbooks

- `docs/milestones/M06/M06_run1_policy_builder.md`
- `docs/milestones/M06/M06_run2_training_eval.md`
- `docs/milestones/M06/M06_local_gpu_execution.md`
- `docs/milestones/M06/M06_plan.md` (this file)
- `docs/milestones/M06/M06_toolcalls.md`

`M06_run1_policy_builder.md` captures prerequisite checks, as-built counts, and hashes after the user runs the selector locally.  
`M06_run2_training_eval.md` holds the 3-run results table and final decision label after GPU work.  
`M06_local_gpu_execution.md` lists exact RTX 5090 commands.

### Phase 4 — local GPU execution matrix

**User-run only** (not automated in CI). See `M06_local_gpu_execution.md`.

---

## 9. Decision rules

Use a **conservative noise band of ±0.5 chrF**.

### Success candidate

A candidate is a success candidate only if it:

- beats the **same-run M06 control** by **at least +0.5 chrF**
- also beats the current validated best dev pin: **45.3584 chrF**
- does not show obvious qualitative collapse

### Neutral

Neutral if:

- best candidate is within **±0.5 chrF** of control, or
- it edges control but does **not** beat **45.3584**

### Regression

Regression if:

- best candidate is **more than 0.5 chrF below** control, or
- qualitative outputs again become short / generic / templated

### Required decision label

Use exactly one of:

```text
M06 success candidate — quality-gated expansion beats control
```

```text
M06 neutral — gated expansion does not clearly beat control
```

```text
M06 regression — even gated expansion hurts
```

---

## 10. Submission gate

No Kaggle submission in M06 unless:

- a candidate clears the **success candidate** rule above, and
- the result is documented in `M06_run2_training_eval.md`

If that happens, create:

- `docs/milestones/M06/M06_run3_kaggle_submit.md`

If not, do **not** create a Kaggle submit run doc.

---

## 11. Deliverables

**Code:** deterministic selection module, policy CLI, config path additions, tests.

**Docs:** `M06_plan.md`, `M06_run1_policy_builder.md`, `M06_run2_training_eval.md`, `M06_local_gpu_execution.md`, `M06_toolcalls.md`.

**Gitignored local artifacts:** policy CSVs, policy reports, training outputs, eval outputs.

---

## 12. Guardrails

- Freeze policy parameters **before** training.
- Do not tune thresholds or caps after seeing eval results.
- Do not change M05 augmentation logic in M06.
- Do not use full-train alignment artifacts for this milestone’s train matrix.
- Do not weaken strict dominance.
- Do **not** update `docs/akk2eng.md` until M06 is formally closed.
- If all candidates fail, close the milestone honestly and move on.

---

## 13. Exit criteria

M06 is complete when all of the following are true:

- selector CLI implemented and tested
- policy reports are deterministic and hashed
- CI is green
- control + Policy A + Policy B local runs completed (user GPU)
- `M06_run2_training_eval.md` contains final metrics and one locked decision label
- milestone is either honestly closed or, if warranted, one Kaggle submission is made under the gate above

---

## 14. Closeout instructions for Cursor

At closeout:

1. Generate `docs/milestones/M06/M06_summary.md` and `docs/milestones/M06/M06_audit.md`
2. Update `docs/akk2eng.md` with M06 status, result summary, and any new learned constraints
3. Merge the milestone branch only after closeout artifacts are complete
4. Seed `docs/milestones/M07/M07_plan.md` and `docs/milestones/M07/M07_toolcalls.md`
5. Put all post-closeout follow-on work on a **new branch**, not the closed M06 branch
6. Ensure all documentation is updated as necessary

---

## 15. Completion signal for paste-back

```text
Control chrF:
Policy A chrF:
Policy B chrF:
Best Δ vs control:
Decision:
```

---

## Prerequisite discipline

Treat `augmented_train_sentences.csv` as an **existing M05 artifact**. Do not regenerate it as part of normal M06 work unless it is missing or inconsistent with recorded M05 hashes/counts; if regeneration is required, document it as a reproducibility recovery step in `M06_run1_policy_builder.md`.
