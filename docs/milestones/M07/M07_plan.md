# M07 Plan — Confidence-driven expansion (seed)

**Milestone:** M07  
**Status:** **Seeded** (not started — plan sketch only)  
**Baseline tag:** `v0.0.9-m06`

---

## Why M07 exists

M06 proved that **extreme precision gating** can yield a large dev gain with only **two** high-confidence expansion rows. The limiter is not “expansion” in the abstract — it is **confidence coverage** and **scoring fidelity**.

---

## Direction (locked intent for planning)

1. **Discover more high-confidence rows** under honest split-safe constraints (no leakage).
2. **Improve confidence scoring** / provenance so ranking matches human-interpretable alignment quality.
3. **Do not** increase training volume blindly — recall-first expansion without gates is **explicitly** out of posture (M05/M06 lesson).

---

## Out of scope (initial)

- Raw volume targets without per-row quality gates  
- Repeating M05-style unweighted partial-prefix dominance  
- Trainer architecture swaps (defer to roadmap unless unblocker)

---

## References

- M06 closeout: [../M06/M06_summary.md](../M06/M06_summary.md)  
- Tool log: [M07_toolcalls.md](M07_toolcalls.md)  
- SoT: [../../akk2eng.md](../../akk2eng.md)
