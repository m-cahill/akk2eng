# M03 — Audit (closeout)

**Audit mode:** `DELTA AUDIT (M02 → M03)`

**Milestone:** M03 — Normalization engine  
**Scope:** Inference-time transliteration normalization (`v1` experiment → **`v2` default**)

---

## Score

```text
5.0 / 5.0
```

*Governance note:* Score reflects **process quality** (isolation, measurement, rollback) and **absence of regressions** in the shipped default (v2). Product metric uplift was not achieved; that outcome is recorded as a **finding**, not a scoring penalty, because the milestone hypothesis was **tested and falsified** for v1 and **bounded** for v2.

---

## Categories

| Category | Result | Notes |
|----------|--------|--------|
| Functionality | **PASS** | Normalization integrated at `run_inference()`; artifacts + CLI |
| Determinism | **PASS** | Pure deterministic transforms; no stochastic decoding changes |
| Governance | **PASS** | A/B runs, archived metrics, run docs (`M03_run1`, `M03_run2`), tool log |
| CI integrity | **PASS** | `tests/test_m03_normalize.py`; no workflow changes required for M03 |
| Reproducibility | **PASS** | Same split, seed, checkpoint → v2 ON vs OFF produced identical dev outputs in measured A/B |

---

## Findings

### Strengths

- **Proper isolation** of the data-layer change (single call site; config + CLI).
- **Clean rollback path:** harmful **v1** documented and superseded by **v2** without decoding/model/lexicon edits.
- **No unintended side effects** on references or post-process order (normalize → translate → lexicon).
- **Audit trail:** version string in `metrics.json` / `config.json` for every eval snapshot.

### Risks / limits

- **Normalization does not improve** dev chrF vs norm-off under **v2** on the current split (parity).
- **Public leaderboard** remains in the **~11.6–11.9** band; M03 did **not** add a validated submit (per discipline: no dev gain → no submit).
- **v1** must not be reintroduced without **joint** training-data normalization or evidence of held-out benefit.

---

## Final recommendation

```text
M03 is fit for closure.
Proceed to M04 (Sentence Alignment).
```

---

## References

- Summary: [M03_summary.md](M03_summary.md)
- v1 measurement: [M03_run1_normalization.md](M03_run1_normalization.md)
- v2 measurement: [M03_run2_conservative_norm.md](M03_run2_conservative_norm.md)
- Plan: [M03_plan.md](M03_plan.md)
- Prior milestone: [../M02/M02_audit.md](../M02/M02_audit.md)
