# M04 — Audit (closeout)

**Audit mode:** `DELTA AUDIT (M03 → M04)`

**Milestone:** M04 — Sentence alignment  
**Scope:** Deterministic sentence alignment builder, split-safe mode, training/eval integration, leakage remediation

---

## Score

```text
5.0 / 5.0
```

*Governance note:* Score reflects **correctness**, **data integrity** (leakage caught and fixed), **reproducibility** (hashes, reports), **discipline** (isolated variable, no forbidden scope creep), and a **meaningful validated metric gain** on the frozen dev contract after split-safe enforcement.

---

## Categories

| Category | Result | Notes |
|----------|--------|--------|
| **Correctness** | **PASS** | Alignment deterministic on fixtures; engine + CLI tested; overlap verification tested |
| **Data integrity** | **PASS** | Train/dev leakage from full-train alignment **identified**; **`--split-safe`** + **`verify_aligned_no_dev_oare_overlap`**; **0** shared `oare_id` on validated run |
| **Reproducibility** | **PASS** | `alignment_report*.json` with SHA-256; run logs in `M04_run3_training_eval.md`; tool log updated |
| **Discipline** | **PASS** | No architecture change; no decoding/normalization rewrite; no lexicon expansion; mixed path exploratory only |
| **Outcome quality** | **PASS** | **+3.48 chrF** vs **~39.8601** baseline under **same** eval contract (beam=3, lex, norm v2) |

---

## Key finding

> Initial **high** dev chrF (**~52.25**) used alignment built from **full** `train.csv`, allowing **train/dev document overlap** in supervision — **leakage-level metrics**, not unbiased generalization.

> After enforcing **alignment input = `train_split.csv` only** and **hard overlap check** vs `dev_split.csv`, gain **stabilized** at **+3.48 chrF** — confirming **real** improvement from sentence-aligned supervision.

---

## Strengths

- **Audit-first:** explicit hashes, skip reasons, method counts, split overlap JSON.
- **Fail-closed:** align `--split-safe` **exits non-zero** if any dev `oare_id` appears in aligned output.
- **Isolated variable:** same model family, checkpoint continuation, decoding, normalization, lexicon defaults.

---

## Risks / limits

- **Coverage:** aligned docs are a **fraction** of train (~16% docs aligned in split-safe run — see `M04_run3`); expansion is future work.
- **Training substrate:** validated numbers in repo notes include **CPU** (`--device auto`) where CUDA was unavailable; **GPU parity** optional for numerical alignment with production hardware.
- **Mixed corpus:** not the validated win; integration/weighting **deferred**.

---

## Deferred items

| Item | Rationale |
|------|-----------|
| **GPU parity run** | Optional confirmation on RTX 5090 / CUDA — expect ~43–44 chrF band |
| **Mixed training weighting / curriculum** | Future milestone — alignment + full corpus integration |
| **Alignment coverage expansion** | More sentence pairs / docs without sacrificing precision |

---

## Final recommendation

```text
M04 is fit for closure.
Proceed to M05 (Data augmentation) on a new branch.
```

---

## References

- Summary: [M04_summary.md](M04_summary.md)
- Training / eval + leakage fix: [M04_run3_training_eval.md](M04_run3_training_eval.md)
- Baseline / data audit: [M04_run1_baseline_and_data_audit.md](M04_run1_baseline_and_data_audit.md)
- Plan: [M04_plan.md](M04_plan.md)
- Tool log: [M04_toolcalls.md](M04_toolcalls.md)
- Prior milestone: [../M03/M03_audit.md](../M03/M03_audit.md)
