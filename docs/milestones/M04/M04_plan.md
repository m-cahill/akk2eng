# M04 Plan — Sentence alignment

**Milestone:** M04  
**Title:** Sentence alignment  
**Status:** **Closed** (`v0.0.7-m04`)  
**Baseline tag:** `v0.0.6-m03`  
**Primary intent:** reduce the train/test granularity mismatch by deriving deterministic, auditable sentence-level training pairs from the official training data, then run bounded training experiments that isolate alignment as the variable.

### As-run exit note (2026-03-22)

- **Shipped:** deterministic alignment engine (`alignment.py`), `pipeline.align`, tests, mixed-train helper, config paths, README / tool log updates.
- **Leakage remediation:** alignment from full `train.csv` produced **~52.25 chrF** (untrustworthy). **`--split-safe`** + dev `oare_id` overlap check enforced; **0 overlap** on validated run.
- **Final validated metric:** **~43.34 chrF** vs baseline **~39.8601** → **+3.48 chrF** (same eval contract: beam=3, lex on, norm v2). Documented in [M04_run3_training_eval.md](M04_run3_training_eval.md) and [M04_summary.md](M04_summary.md).
- **Kaggle:** no submission required for closeout (discipline: validated local gain; optional GPU parity noted in audit).
- **Closeout artifacts:** [M04_summary.md](M04_summary.md), [M04_audit.md](M04_audit.md); source of truth updated in [`docs/akk2eng.md`](../../akk2eng.md).

## Why this milestone exists

M03 established that normalization is safe but not a primary optimization lever. The next likely gain is structural: the current training data is document-level, while competition inference is sentence-level. The official data description explicitly highlights this mismatch and provides a sentence-alignment aid file.

## Objective

Build a deterministic sentence-alignment pipeline for the official training data, integrate it as an optional training path, and validate whether sentence-aligned fine-tuning improves dev chrF over the pinned M04 baseline.

## Hard exit criteria

1. A deterministic alignment builder exists in repo code and is covered by tests.
2. The builder produces:

   * a sentence-aligned training CSV,
   * an alignment report with coverage / skip reasons / method counts,
   * a stable content hash or equivalent reproducibility marker.
3. At least one controlled training/eval run is completed using the aligned data.
4. All M04 experiments save the normal audit artifacts:

   * `config.json`
   * `metrics.json`
   * `predictions_dev.csv`
5. `pytest` and `ruff check src tests` stay green.
6. `docs/akk2eng.md` is updated for any new data contract, config surface, or milestone status change (substantive **Derived Data Contracts** subsection deferred to M04 closeout once the builder contract is stable).

## Stretch exit criteria

1. Best M04 run beats the pinned M04 baseline on dev chrF.
2. Only if dev improves, sync the winning config into the Kaggle notebook/runtime path and make one disciplined Kaggle submission.
3. Public leaderboard exceeds the prior stable band only as validation, never as the reason to submit.

## Non-goals

* No model architecture change.
* No decoding redesign.
* No normalization algorithm rewrite.
* No lexicon expansion work.
* No publication OCR mining / `publications.csv` extraction / multilingual translation reconstruction; that belongs to later data-augmentation work, not M04.
* No competition-data-derived CSVs committed to git. Commit code, fixtures, schemas, and reports only. Competition rules restrict redistribution of competition data.

## Guardrails

* Keep the current model family fixed.
* Keep current repo-default inference controls fixed unless a compatibility bug forces a change.
* Keep normalization at current safe default (`v2`) during M04 unless a bug fix is required.
* Keep lexicon behavior unchanged during M04.
* Use only official competition files already in the accepted bundle for the alignment workflow.
* Preserve the deterministic dev split and current evaluation contract.
* No probe submissions.
* Any unresolved ambiguity or low-confidence alignment behavior must be explicitly deferred in the audit with rationale.

---

## Phase A — Baseline pin and alignment data audit

**Goal:** remove ambiguity before touching training.

### Tasks

1. Re-run the current repo-default eval path on the frozen dev split and record it as the **M04 baseline**.
2. Independently identify the best archived local dev result already referenced by prior milestone docs, and record whether it is or is not the same as the current default.
3. Create `M04_run1_baseline_and_data_audit.md` with:

   * baseline config,
   * checkpoint used,
   * decode settings,
   * normalization / lexicon state,
   * resulting chrF / BLEU,
   * note on “default vs archived best” if they differ.
4. Inspect the local competition bundle for:

   * `Sentences_Oare_FirstWord_LinNum.csv`
   * any train-side fields needed for deterministic sentence segmentation.
5. Produce a small data audit artifact, e.g. `outputs/alignment/baseline_alignment_audit.json`, containing:

   * train row count,
   * number of docs represented in the sentence-aid file,
   * obvious schema/coverage gaps,
   * line-number edge cases observed.

### Definition of done

* The baseline comparison target is pinned and documented.
* The alignment input files are confirmed and their schema/coverage is documented.
* There is no ambiguity about what M04 must beat.

---

## Phase B — Deterministic alignment engine

**Goal:** derive high-precision sentence pairs without fabricating alignments.

### Suggested implementation surface

* `src/akk2eng/data/alignment.py`
* `src/akk2eng/pipeline/align.py` or equivalent CLI/module
* config additions in the existing config surface only if truly needed

### Required behavior

1. **Line-number parsing**

   * Support line values like `1`, `1'`, `1''`.
   * Support float-encoded line numbers from the aid CSV (e.g. `1.01` → `1'`, `1.02` → `1''`).
   * Preserve ordering deterministically.

2. **Transliteration sentence boundary extraction**

   * Use `Sentences_Oare_FirstWord_LinNum.csv` as the anchor source.
   * Build sentence spans from train transliterations using first-word + line-number anchors.
   * Do not silently “best guess” across broken anchors; skip and log ambiguous cases.

3. **Conservative English sentence splitting**

   * Deterministic splitter only.
   * Prefer high precision over recall.
   * Keep rules explicit and testable.

4. **Monotonic sentence pairing**

   * Exact-count match first.
   * One bounded fallback allowed: adjacent English merge/split heuristic with deterministic scoring.
   * Skip ambiguous cases instead of forcing low-confidence pairs.

5. **Quality metadata**

   * Each aligned row should carry:

     * stable `sentence_id`
     * `oare_id`
     * `line_start`
     * `line_end`
     * `alignment_method`
     * `alignment_confidence`
   * Emit an `alignment_report.json` with:

     * docs processed
     * docs aligned
     * sentence pairs produced
     * method counts
     * skip-reason histogram
     * hash of produced aligned CSV

### Output contract

Generated locally only, not committed:

* `data/derived/alignment/aligned_train_sentences.csv` or equivalent gitignored path
* `data/derived/alignment/alignment_report.json`
* optional `data/derived/alignment/alignment_candidates.csv`

### Definition of done

* Running the builder twice on the same inputs produces byte-stable outputs.
* Ambiguous docs are skipped, not hallucinated into alignment.
* The output schema is documented in run notes and later in `akk2eng.md` (closeout).

---

## Phase C — Tests and verification for the builder

**Goal:** make M04 auditable and safe.

### Required tests

1. `tests/test_m04_alignment.py`
2. Small committed synthetic fixtures only; no competition data in git.
3. Cover at least:

   * line-number parsing with prime marks
   * deterministic sentence ordering
   * exact-count alignment
   * fallback merge/split alignment
   * ambiguous-case skip behavior
   * stable output hashing / serialization
4. Add one fixture-level end-to-end test that:

   * builds aligned output from a tiny synthetic input set,
   * verifies aligned row count,
   * verifies stable sentence IDs,
   * verifies stable report hash.

### Definition of done

* Tests pass locally and in CI.
* The builder is deterministic on committed fixtures.

---

## Phase D — Training/eval integration

**Goal:** measure alignment, not architecture.

### Training rules

* Same model family.
* Same seed discipline.
* Same dev split.
* Same inference/eval path unless a winning model replaces the checkpoint.
* Alignment is the primary changed variable.

### Experiment matrix (Phase D — locked)

Run **both** experiments (alignment coverage is sparse; aligned-only is high regression risk):

**Experiment 1 — sentence-aligned continuation (isolated signal)**

* Start from the current M01/M03 working checkpoint.
* Continue fine-tuning on **sentence-aligned pairs only** (`aligned_train_sentences.csv`).
* Evaluate on the frozen dev split with the current repo-default eval path.
* **Expectation:** often worse or unstable vs baseline (small effective dataset).

**Experiment 2 — mixed corpus (co-primary; required)**

* Concatenate **full** `train.csv` **then** `aligned_train_sentences.csv` → `mixed_train.csv` (see `python -m akk2eng.pipeline.mix_train`).
* Same continuation checkpoint and training hyperparameters as Exp 1 unless a deliberate A/B is documented.
* **This is the primary comparison** for M04 success (alignment as signal injection, not replacement).

**Optional (out of default matrix):** document-to-sentence curriculum or upsampling aligned rows (e.g. 2–3×) — only if documented in run notes; not required for M04 closeout.

### Required artifacts for each experiment

Under `outputs/experiments/exp_<timestamp>/`:

* `config.json`
* `metrics.json`
* `predictions_dev.csv`

Also include alignment metadata in `config.json`, such as:

* alignment CSV hash
* alignment report hash
* alignment mode
* confidence filter if used

### Definition of done

* At least one aligned-data experiment completes end-to-end.
* Results are compared directly against the pinned M04 baseline in `M04_run3_training_eval.md`.

---

## Phase E — Submission gate and notebook sync

**Goal:** submit only on evidence.

### Rules

1. Submit only if best M04 run improves dev chrF over the pinned M04 baseline.
2. Before submission, ensure the Kaggle notebook/runtime path matches the winning repo config exactly.
3. Log the submission in `M04_run4_kaggle.md`.
4. If there is no dev gain, do not submit; close the milestone honestly with “alignment builder shipped, no validated Kaggle submit.”

### Definition of done

* Either:

  * one justified Kaggle submission was made and logged, or
  * no submission was made and the reason is explicit.

---

## Suggested file changes

* `src/akk2eng/data/alignment.py`
* `src/akk2eng/pipeline/align.py` or equivalent
* `src/akk2eng/config.py` only for minimal opt-in alignment settings
* `tests/test_m04_alignment.py`
* `tests/fixtures/m04_alignment/*` using synthetic data only
* `docs/milestones/M04/M04_run1_baseline_and_data_audit.md`
* `docs/milestones/M04/M04_run2_alignment_builder.md`
* `docs/milestones/M04/M04_run3_training_eval.md`
* `docs/milestones/M04/M04_run4_kaggle.md` only if a submission occurs

---

## Verification checklist

Before calling M04 complete:

* `ruff check src tests`
* `pytest`
* Run the alignment builder twice on the same local competition files and confirm identical output hash
* Confirm alignment-derived data stays gitignored
* Confirm at least one aligned-data training/eval run produced the standard experiment artifacts
* Confirm `docs/akk2eng.md` reflects the new derived-data contract and M04 status
* Confirm notebook parity only if a Kaggle submission was actually justified

---

## Closeout prompt for Cursor

Use this when M04 implementation is complete and the branch is ready to close:

> Close out M04 formally. Generate `docs/milestones/M04/M04_summary.md` and `docs/milestones/M04/M04_audit.md` using the established prompts, and update `docs/akk2eng.md` with M04 status, scope, closeout, any new data contract, and any release tag. Update `docs/milestones/M04/M04_plan.md` to closed status with an as-run exit note. If a Kaggle submission was not justified, state that explicitly. Merge the milestone branch only after the summary/audit are complete. Then create and seed `docs/milestones/M05/M05_plan.md` and `docs/milestones/M05/M05_toolcalls.md` on the next branch, not as a post-closeout push on the closed milestone branch. Ensure all documentation is updated as necessary.

---

## References

* Prior milestone closeout: [../M03/M03_summary.md](../M03/M03_summary.md)
* Tool / run log: [M04_toolcalls.md](M04_toolcalls.md)
