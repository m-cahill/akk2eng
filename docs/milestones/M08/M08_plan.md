# M08 Plan — Alignment quality & new supervision (seed)

**Milestone:** M08  
**Status:** **Seeded** (not started — post–M07 pivot)  
**Baseline tag:** `v0.0.10-m07`

---

## Why M08 exists

M07 **conclusively** showed that **confidence-based selection alone** cannot expand beyond the **M06 optimum** (236 strict + **2** expansion). Adding **only a few** more rows from the same split-safe augmented pool collapsed dev chrF by **~6.6** vs the same-run M06 Policy A baseline. The beneficial expansion signal is **too sparse** to separate reliably with current heuristics on this pool.

---

## Direction (locked intent)

1. **Improve alignment quality** — structural fixes upstream of selection (not more scoring tweaks on the M05 CSV).
2. **New sources of high-confidence supervision** — only where honest split-safe / no-leakage rules hold.
3. **Pipeline improvements** that increase **precision** of training pairs, not **recall** of noisy expansion rows.

---

## Explicitly out of scope (initial)

- Further **`confidence_v2`** / filtering iterations on the **same** M05 augmented pool as the primary lever  
- **Recall-first** expansion or volume targets without a new alignment or data contract  
- **Weighting / duplication / curriculum** (M06 Policy B lesson carries forward)

---

## References

- M07 closeout: [../M07/M07_summary.md](../M07/M07_summary.md)  
- M07 audit (high-value failure): [../M07/M07_audit.md](../M07/M07_audit.md)  
- Tool log: [M08_toolcalls.md](M08_toolcalls.md)  
- SoT: [../../akk2eng.md](../../akk2eng.md)
