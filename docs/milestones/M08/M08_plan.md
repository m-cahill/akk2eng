# M08 Plan — Alignment-quality recovery

**Milestone ID:** M08  
**Working title:** Alignment-quality recovery  
**Target branch:** `m08-alignment-quality-recovery`  
**Audit target:** 5.0 / 5.0  
**Baseline:** `main` after M07 closeout (`v0.0.10-m07`)  
**Status:** **Closed** — regression (`v0.0.11-m08`). Phases 1–4 complete; **no Kaggle submission**. Closeout: `M08_summary.md`, `M08_audit.md`.

---

## Milestone question

Can a **narrow, deterministic, full-sentence alignment-repair pass** recover a few **strict-grade / resplit-grade** sentence pairs from the original train split and beat the current best training mix from M06 (**236 strict + 2 proven expansion rows**) on the frozen dev split?

---

## Why this milestone

M06 showed that **tiny, ultra-clean** extra supervision can help a lot; M07 showed that **confidence scoring cannot safely widen** the M05 augmented pool. The beneficial M06 rows were **`expanded_english_resplit`**. M08 tests **alignment-quality v2** (semicolon/colon full-clause resplit only on **count mismatch `na == ne + 1`**) **without** partial-prefix, relaxed rows, publications, or further pool scoring.

---

## Locked constraints (summary)

- **Unchanged** frozen dev eval contract: beam=3, lexicon on, normalization v2, same continuation training recipe as M06/M07.
- **No** weighting, duplication, curriculum, or confidence rescoring on the M05 pool in M08.
- **No** partial-prefix / relaxed / fragmentary supervision.
- **No** `publications.csv`, external corpora, dev labels, leaderboard probing, or manual curation.
- Inputs: `data/splits/train_split.csv`, `data/splits/dev_split.csv`, `data/Sentences_Oare_FirstWord_LinNum.csv`, M06 Policy A baseline CSV (winner union + identity lock).
- **Kaggle submission** only if a candidate beats same-run baseline by **≥ +0.5 chrF** and beats historical dev pin **52.2530** (see decision rules in run2 doc).

Full rule text is mirrored in **`M08_run2_training_eval.md`** and the original milestone charter (handoff).

---

## Experimental matrix (locked)

| Run | Dataset |
|-----|---------|
| **Baseline** | `data/derived/selection/strict_plus_highconf_cap50.csv` |
| **Candidate A** | `data/derived/alignment_quality/aligned_train_sentences_quality_v2_split.csv` |
| **Candidate B** | `data/derived/alignment_quality/aligned_train_sentences_quality_v2_plus_m06.csv` |

---

## Implementation map

| Component | Location |
|-----------|----------|
| Repair + build | `src/akk2eng/data/alignment_quality.py` |
| CLI | `python -m akk2eng.pipeline.align_quality` → `src/akk2eng/pipeline/align_quality.py` |
| Defaults | `DEFAULT_ALIGNMENT_QUALITY_OUTPUT_DIR` in `src/akk2eng/config.py` |
| Tests | `tests/test_m08_alignment_quality.py`, fixtures `tests/fixtures/m08_alignment_quality/` |

---

## M06 winner identities (fail-closed)

Must match baseline CSV expansion rows (see `M07_run1_confidence_builder.md`):

- `fc678a23-7011-4f9d-8957-ebf2c8dbbb43:2651ad13-ef9b-4941-a3e9-44d76a13b191`
- `fc678a23-7011-4f9d-8957-ebf2c8dbbb43:c7d5c7a2-793b-49e0-8991-c57d70981fcf`

---

## Early no-op gate

Emitted in **`alignment_quality_v2_report.json`**:

- `early_no_op_gate_candidate_a` — Candidate A canonical fingerprint matches M04 split-safe strict CSV **and** `recovered_row_count == 0` (when `--strict-baseline-csv` exists and is read).
- `early_no_op_gate_candidate_b_identical_to_m06_baseline` — Candidate B canonical core fingerprint matches full M06 baseline.
- `early_no_op_stop_recommended` — both true → **skip GPU matrix**; close milestone honestly.

---

## Phase checklist

| Phase | Scope | Status |
|-------|--------|--------|
| **1** | Builder + reports + recovered-docs CSV | ✅ |
| **2** | CPU-safe tests | ✅ |
| **3** | Docs / runbooks | ✅ |
| **4** | Local GPU 3-run matrix | ✅ (regression documented in `M08_run2_training_eval.md`) |
| **Closeout** | Summary, audit, `docs/akk2eng.md`, tag, M09 seed, CI log | ✅ |

---

## References

- [M08_toolcalls.md](M08_toolcalls.md)  
- [M07_summary.md](../M07/M07_summary.md)  
- SoT: [../../akk2eng.md](../../akk2eng.md) (update **only at M08 formal closeout**)
