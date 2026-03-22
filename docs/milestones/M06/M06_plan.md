# M06 Plan — Precision-preserving data expansion

**Milestone:** M06  
**Title:** Precision-preserving data expansion  
**Status:** **Seeded** (not started — plan only)  
**Baseline tag:** `v0.0.8-m05`

---

## Why this milestone exists

M05 implemented split-safe **alignment expansion** and measured a **large dev regression** vs a same-run aligned-only control (~**−25 chrF**), dominated by **partial-prefix** and other low-confidence rows mixed unweighted with M04-strict pairs.

M06 must answer:

> How do we **grow** supervision **without** repeating M05’s noise failure?

---

## Objective (draft)

Design **quality-gated** or **weighted** use of expanded pairs (or alternative data strategies) such that dev chrF **does not regress** vs aligned-only control, with full provenance and audit parity to M05.

---

## Non-goals (initial)

* No mandatory model architecture upgrade (defer to later roadmap unless unblocker)
* No change to default decoding / normalization / lexicon without justified bug fix
* No Kaggle submission until dev improvement is validated

---

## References

* M05 closeout: [../M05/M05_summary.md](../M05/M05_summary.md)
* Tool log: [M06_toolcalls.md](M06_toolcalls.md)
* Project SoT: [../../akk2eng.md](../../akk2eng.md)
