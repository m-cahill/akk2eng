# M09 Plan — Training dynamics & supervision integration (seed)

**Milestone:** M09  
**Status:** **Seeded** (not started — post–M08 closeout)  
**Baseline tag:** `v0.0.11-m08`

---

## Why M09 exists

M06 found a **razor-thin** supervision optimum. M07 showed **selection / scoring** cannot widen the M05 pool. M08 showed **structural alignment repair** (+46 full-sentence pairs) causes **catastrophic regression** (~−32 chrF) — **distribution mismatch** dominates local label correctness.

---

## Direction (locked intent)

Focus on **how the model learns from supervision**, not on adding more rows via alignment or selection:

1. **Training dynamics** — stability, effective learning rate, catastrophic forgetting under mixture shift.  
2. **Curriculum / staged integration** — if at all, introduce new supervision **gradually** or in **isolated phases**, with measurement at each step.  
3. **Data integration strategy** — explicit hypotheses about **mixture composition** vs M06 optimum (not recall-first widening).

---

## Explicitly out of scope (initial)

- Further **alignment-repair** iterations (M08 branch closed negative).  
- **Selection / confidence scoring** on the M05 augmented pool (M07 branch closed negative).  
- **Publications mining**, **back-translation**, or **lexicon / decode** experiments unless re-opened with a new charter.

---

## References

- M08 closeout: [../M08/M08_summary.md](../M08/M08_summary.md)  
- M08 audit: [../M08/M08_audit.md](../M08/M08_audit.md)  
- Tool log: [M09_toolcalls.md](M09_toolcalls.md)  
- SoT: [../../akk2eng.md](../../akk2eng.md)
