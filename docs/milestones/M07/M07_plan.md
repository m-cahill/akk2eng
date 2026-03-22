# M07 — Confidence-Driven Expansion

**Milestone ID:** M07
**Working title:** Confidence-driven expansion
**Target branch:** `m07-confidence-driven-expansion`
**Audit target:** **5.0 / 5.0**
**Baseline:** `main` after M06 closeout (`v0.0.9-m06`)

## Milestone question

Can a **better deterministic confidence score** recover a **few additional high-quality expansion rows** from the split-safe M05 augmented pool and beat the current best known training mix from M06 (**236 strict + 2 selected expansion rows**) on the frozen dev split?

## Locked context

M05 proved that ungated expansion is harmful: the split-safe augmented mix grew to **542** rows and collapsed to about **20.39 chrF** versus **45.36 chrF** for the same-run strict-only control. M06 then showed the opposite: a **tiny**, **extreme-precision** selection of only **2** expansion rows improved dev chrF to **52.2530**, while **Policy B** demonstrated that weighting / duplication can reintroduce collapse. The project ledger now records:

```text
Strict aligned > high-confidence expanded > partial-prefix > noisy synthetic
Expansion is only beneficial under extreme precision gating.
```

M07 therefore must answer a narrow question: **can we find a few more rows like the M06 winners without drifting back toward noisy volume or weighting?**

## 1. Objective

Improve the **confidence-scoring fidelity** of the existing split-safe expansion pool so that the system can admit a **small number of additional rows** beyond the M06 winning set, while preserving the precision-first regime that produced the M06 gain.

## 2. Locked constraints

These are not negotiable in M07:

* Keep the **existing evaluation contract** unchanged: frozen dev split, same continuation path, **beam=3**, lexicon on, normalization v2.
* Keep the **same model family** and same general training recipe used in M06.
* Do **not** change decoding, normalization, lexicon behavior, model architecture, epochs, or trainer behavior.
* Do **not** use weighting, duplication, curriculum, or any other mixing trick. M06 Policy B already showed that this can destroy the gain.
* Do **not** generate new augmentation rows in M07. Operate only on the existing split-safe M05 augmented CSV plus the M06 winning dataset.
* Do **not** use dev labels, dev predictions, Kaggle leaderboard results, or manual row labeling to define the scorer.
* Do **not** mine `publications.csv`, external corpora, or new external data in M07.
* No Kaggle submission unless a candidate beats the M07 same-run baseline and the historical best dev pin of **52.2530 chrF**.

## 3. Hypothesis

The M06 result suggests that `augmentation_confidence` is directionally useful but too coarse. A **deterministic rescoring layer** using row metadata plus simple text-quality features should be able to recover a **few** more usable rows from the M05 pool. Because M06 succeeded with only **2** rows and Policy B failed when mixture shape changed, M07 should remain in an **extreme precision / tiny-cap** regime.

## 4. In scope

M07 includes only:

1. A deterministic **confidence_v2 scoring layer** over the existing M05 augmented pool.
2. A scored candidate pool CSV plus hashed JSON reports.
3. Two tiny-cap candidate training datasets built on top of the M06 winning baseline.
4. CI-safe tests for scoring, filtering, determinism, and fail-closed behavior.
5. A locked **3-run local GPU matrix**:

   * M06 winning baseline rerun
   * Candidate cap6
   * Candidate cap10
6. Honest closeout with success / neutral / regression decision.

## 5. Out of scope

Do not do any of the following in M07:

* new alignment heuristics
* back-translation
* noise augmentation
* lexicon redesign
* named-entity handling
* publications mining
* model swap / larger backbone
* decoding experiments
* trainer weighting
* more than the locked run matrix unless explicitly opened in a later milestone

## 6. Experimental matrix

| Run             | Dataset                                                 | Purpose                                             |
| --------------- | ------------------------------------------------------- | --------------------------------------------------- |
| **Baseline**    | `data/derived/selection/strict_plus_highconf_cap50.csv` | same-run M06 champion comparator                    |
| **Candidate A** | `data/derived/confidence/strict_plus_confv2_cap6.csv`   | test tiny additional expansion under better scoring |
| **Candidate B** | `data/derived/confidence/strict_plus_confv2_cap10.csv`  | test whether a slightly larger tiny-cap still helps |

### Cap rationale

* **cap6** means at most **6** total expansion rows mixed with **236** strict rows, so expansion is at most about **2.5%** of the training CSV.
* **cap10** means at most **10** total expansion rows, so expansion is at most about **4.1%**.

These caps intentionally stay close to the M06 winning regime and far away from M05-style volume.

## 7. Locked dataset definitions

### Baseline — `strict_plus_highconf_cap50.csv`

Use the existing M06 winner as read-only baseline:

* **236** strict rows
* **2** M06-selected expansion rows
* no weighting
* no changes

### Candidate A — `strict_plus_confv2_cap6.csv`

* Start from the full split-safe M05 augmented CSV.
* Recompute `confidence_v2` for eligible expansion rows.
* Keep all **236** strict rows.
* Select the top **6 total expansion rows** by `confidence_v2`.
* The **2 M06-winning rows must remain included** unless a hard data-integrity failure makes scoring impossible; if either disappears, **stop and report**.

### Candidate B — `strict_plus_confv2_cap10.csv`

* Same process as Candidate A.
* Keep the top **10 total expansion rows** by `confidence_v2`.
* The **2 M06-winning rows must remain included** here as well.

If fewer than 6 or 10 rows survive the locked filters, write a smaller dataset and record the shortfall in the report. Do **not** relax the rules after seeing counts.

## 8. Locked `confidence_v2` rules

Implement a new deterministic scoring layer, preferably under:

* `src/akk2eng/data/confidence.py`
* `src/akk2eng/pipeline/select_confident_train.py`

### Source pool

Start from `data/derived/augmentation/augmented_train_sentences.csv`.

Eligible pool for rescoring:

* non-strict rows only
* exclude any row whose `augmentation_type` contains `relaxed` (case-insensitive)
* fail closed if required columns are missing

### Hard exclusions

Drop a candidate row before scoring if any of the following is true:

* `augmentation_confidence` is missing or non-numeric
* translation text contains `<gap>` or `broken` markers
* normalized translation text has fewer than **4** whitespace tokens
* exact duplicate normalized translation text already exists among higher-ranked candidates

For duplicate handling, keep only the highest-ranked instance under the tie-break rules below.

### Score definition

For each remaining candidate row, compute:

```text
confidence_v2 =
  augmentation_confidence
  + type_prior
  + digit_consistency_adjustment
  + length_adequacy_adjustment
  + source_gap_penalty
```

#### Components

`augmentation_confidence`

* existing numeric value from M05

`type_prior`

* `+0.05` for `expanded_english_resplit`
* `+0.00` for `expanded_partial_prefix`
* no relaxed rows are eligible

`digit_consistency_adjustment`

* extract Arabic numeral tokens from transliteration and translation
* `+0.05` if both sides contain numerals and the multisets match exactly
* `-0.05` if one side contains numerals and the other does not
* `0.00` otherwise

`length_adequacy_adjustment`

* let `src_len` = transliteration whitespace-token count
* let `tgt_len` = translation whitespace-token count
* `+0.05` if `tgt_len` is between `max(4, floor(0.15 * src_len))` and `ceil(1.25 * src_len)`
* `-0.05` otherwise

`source_gap_penalty`

* `-0.05` if transliteration contains `<gap>` or `broken`
* `0.00` otherwise

After summing, clip `confidence_v2` into `[0.0, 1.0]`.

### Tie-break order

1. descending `confidence_v2`
2. descending raw `augmentation_confidence`
3. preferred type order: `expanded_english_resplit` before `expanded_partial_prefix`
4. `source_row_id` (lexicographic as string)
5. original row order

## 9. Phase plan

### Phase 1 — scorer + reports

Implement the scorer and builder CLI.

Suggested outputs under gitignored `data/derived/confidence/`:

* `scored_expansion_pool.csv`
* `confidence_v2_report.json`
* `strict_plus_confv2_cap6.csv`
* `strict_plus_confv2_cap6_report.json`
* `strict_plus_confv2_cap10.csv`
* `strict_plus_confv2_cap10_report.json`

Each report must include:

* source CSV SHA-256
* output CSV SHA-256
* eligible pool counts before and after each hard exclusion
* counts by `augmentation_type`
* score summary statistics
* top selected rows with `source_row_id`, `augmentation_type`, raw `augmentation_confidence`, and `confidence_v2`
* whether the two M06-winning rows were preserved
* dev overlap result (`0` required)

### Phase 2 — tests and CI-safe verification

Add tests, preferably:

* `tests/test_m07_confidence.py`
* fixtures under `tests/fixtures/m07_confidence/`

Required coverage:

* deterministic scoring
* exact-duplicate translation handling
* digit consistency bonus / penalty
* length adequacy adjustment
* hard exclusion behavior
* cap6 / cap10 counts
* preservation of the two M06-winning rows
* fail-closed behavior for missing columns / bad confidence
* dev-overlap fail-closed behavior

M07 must remain CPU-only in CI.

### Phase 3 — docs and runbooks

Create and fill:

* `docs/milestones/M07/M07_plan.md`
* `docs/milestones/M07/M07_run1_confidence_builder.md`
* `docs/milestones/M07/M07_run2_training_eval.md`
* `docs/milestones/M07/M07_local_gpu_execution.md`
* `docs/milestones/M07/M07_toolcalls.md`

`M07_run1_confidence_builder.md` must capture the scored-pool summary, selected rows, caps, and hashes.
`M07_run2_training_eval.md` must hold the 3-run results and locked decision label.
`M07_local_gpu_execution.md` must contain exact RTX 5090 commands.

### Phase 4 — local GPU execution matrix

User-run only after CI-safe phases are green.

#### Train

```bash
python -m akk2eng.pipeline.train \
  --train-csv data/derived/selection/strict_plus_highconf_cap50.csv \
  --resume-model-dir outputs/m01_t5 \
  --output-dir outputs/m07_t5_baseline_m06_policy_a \
  --device cuda --fp32 \
  --epochs 3

python -m akk2eng.pipeline.train \
  --train-csv data/derived/confidence/strict_plus_confv2_cap6.csv \
  --resume-model-dir outputs/m01_t5 \
  --output-dir outputs/m07_t5_cap6 \
  --device cuda --fp32 \
  --epochs 3

python -m akk2eng.pipeline.train \
  --train-csv data/derived/confidence/strict_plus_confv2_cap10.csv \
  --resume-model-dir outputs/m01_t5 \
  --output-dir outputs/m07_t5_cap10 \
  --device cuda --fp32 \
  --epochs 3
```

#### Eval

```bash
python -m akk2eng.pipeline.eval --model-dir outputs/m07_t5_baseline_m06_policy_a --output-dir outputs/eval_m07_baseline
python -m akk2eng.pipeline.eval --model-dir outputs/m07_t5_cap6 --output-dir outputs/eval_m07_cap6
python -m akk2eng.pipeline.eval --model-dir outputs/m07_t5_cap10 --output-dir outputs/eval_m07_cap10
```

## 10. Decision rules

Use a conservative noise band of **±0.5 chrF**.

### Success candidate

A candidate is a success candidate only if it:

* beats the **same-run M07 baseline** by **at least +0.5 chrF**
* also beats the historical best dev pin of **52.2530 chrF**
* does not show obvious qualitative collapse

### Neutral

Neutral if:

* best candidate is within **±0.5 chrF** of the same-run baseline, or
* it edges the same-run baseline but does **not** beat **52.2530**

### Regression

Regression if:

* both candidates are more than **0.5 chrF below** the same-run baseline, or
* qualitative outputs become short / generic / templated again

### Required decision label

Use exactly one of:

```text
M07 success candidate — confidence-v2 expansion beats M06 baseline
```

```text
M07 neutral — confidence-v2 does not clearly beat M06 baseline
```

```text
M07 regression — additional expansion reintroduces noise
```

## 11. Submission gate

No Kaggle submission in M07 unless:

* a candidate clears the **success candidate** rule above, and
* the result is documented in `M07_run2_training_eval.md`

If that happens, create:

* `docs/milestones/M07/M07_run3_kaggle_submit.md`

If the M06 public leaderboard result arrives during M07, append it to the M06 submit log only. Do **not** change M07 scope or retune the scorer around it.

## 12. Deliverables

Code:

* deterministic `confidence_v2` scorer
* builder CLI
* config defaults if needed
* tests

Docs:

* `M07_plan.md`
* `M07_run1_confidence_builder.md`
* `M07_run2_training_eval.md`
* `M07_local_gpu_execution.md`
* `M07_toolcalls.md`

Gitignored local artifacts:

* scored pool CSV
* candidate CSVs
* candidate reports
* training outputs
* eval outputs

## 13. Guardrails

* Freeze the scorer before GPU runs.
* Do not use manual row curation as a selection gate.
* Do not alter the M06 winning baseline dataset.
* Do not introduce weighting, duplication, or curriculum.
* Do not regenerate the M05 augmented CSV unless it is missing or inconsistent with recorded M05 artifacts; if recovery is required, document it explicitly.
* Do not update `docs/akk2eng.md` until M07 is formally closed.
* If both candidates fail, close the milestone honestly.

## 14. Exit criteria

M07 is complete when all of the following are true:

* scorer CLI implemented and tested
* scored-pool and candidate reports are deterministic and hashed
* CI-safe checks are green
* baseline + cap6 + cap10 local runs are completed
* `M07_run2_training_eval.md` contains final metrics and one locked decision label
* milestone is honestly closed, and if warranted, one Kaggle submission is logged

## 15. Closeout instructions for Cursor

At closeout:

1. Generate:

   * `docs/milestones/M07/M07_summary.md`
   * `docs/milestones/M07/M07_audit.md`
2. Update `docs/akk2eng.md` with:

   * M07 status
   * result summary
   * any new learned constraints
3. Merge the milestone branch only after closeout artifacts are complete.
4. Seed the next milestone folder:

   * `docs/milestones/M08/M08_plan.md`
   * `docs/milestones/M08/M08_toolcalls.md`
5. Put all post-closeout work on a new branch, not the closed M07 branch.
6. **ensure all documentation is updated as necessary.**

## 16. Completion signal for paste-back

```text
Baseline chrF:
Cap6 chrF:
Cap10 chrF:
Best Δ vs baseline:
Decision:
```

The core idea is simple: **M06 proved the system can benefit from tiny, ultra-clean expansion; M07 should test whether better confidence scoring can safely widen that set by a handful of rows, without drifting back toward M05/M06-Policy-B failure modes.**
