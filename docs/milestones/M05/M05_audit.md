# M05 — Audit (closeout)

**Audit mode:** `DELTA AUDIT (M04 → M05)`

**Milestone:** M05 — Data augmentation (alignment expansion)  
**Scope:** Augmentation pipeline, split-safe dataset, GPU train + eval vs control and M04 pin

---

## Score

```text
5.0 / 5.0
```

Governance: implementation correct and tested; **no leakage**; reproducible builder artifacts; scope discipline (Methods 2–3 deferred); **negative outcome measured honestly** with same-run control—high audit value.

---

## Categories

| Category | Result | Notes |
|----------|--------|-------|
| **Correctness** | **PASS** | Builder deterministic; pytest coverage; CLI `--split-safe` overlap check fail-closed |
| **Data integrity** | **PASS** | Train split only; zero dev `oare_id` overlap on augmented CSV |
| **Reproducibility** | **PASS** | SHA-256 on inputs/output; `augmentation_report.json`; run logs in `M05_run1` / `M05_run2` |
| **Discipline** | **PASS** | No decoding/normalization/model changes; no mid-run heuristic retuning; no Kaggle submit |
| **Outcome quality** | **PASS** | Clear **regression** vs control; conclusion actionable |

---

## Key finding

```text
Naive volume expansion dominated by partial-prefix alignment (~296 rows) diluted
high-confidence strict supervision and produced catastrophic dev regression
(augmented chrF ~20.39 vs control ~45.36, Δ ~−25 chrF).
```

Qualitative: sample predictions shifted toward **short, generic** outputs (e.g. witness-list fragments), consistent with **label noise** overwhelming the signal.

---

## Strengths

- Explicit **provenance** per row (`augmentation_type`, `augmentation_confidence`, `source_row_id`)
- **Strict vs expanded** counts separated in reports
- **Same-run control** isolates augmentation effect from historical baseline drift
- **Successful failure:** eliminated an unsafe direction without polluting metrics

---

## Risks / limits

- Expanded rows **unweighted** vs strict rows (by design for this experiment)
- No **confidence threshold** or curriculum in M05
- Control chrF **>** historical M04 ~43.34 — interpret comparisons primarily as **augmented vs control**

---

## Deferred

| Item | Rationale |
|------|-----------|
| Confidence-based filtering / caps on partial-prefix | M06 candidate |
| Weighted sampling (strict > expanded) | M06 candidate |
| Back-translation | Intentionally out of M05 scope |
| Noise augmentation | Deferred |

---

## Final recommendation

```text
M05 fit for closure. Proceed to M06 — precision-preserving data expansion
(quality-gated supervision), informed by this regression.
```

---

## References

- Summary: [M05_summary.md](M05_summary.md)
- Training / eval: [M05_run2_training_eval.md](M05_run2_training_eval.md)
- Builder: [M05_run1_augmentation_builder.md](M05_run1_augmentation_builder.md)
- Plan: [M05_plan.md](M05_plan.md)
- Tool log: [M05_toolcalls.md](M05_toolcalls.md)
- Prior milestone: [../M04/M04_audit.md](../M04/M04_audit.md)
