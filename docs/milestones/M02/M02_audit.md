# M02 — Audit

## Audit mode

**DELTA AUDIT (M01 → M02)**

Scope: evaluation harness, error analysis, decoding configuration experiments, lexicon validation — **no** new training recipe in M02; baseline checkpoint remains M01 `outputs/m01_t5`.

---

## Score (explicit)

```text
5.0 / 5.0
```

---

## Categories

| Category        | Result | Notes |
| --------------- | ------ | ----- |
| Functionality   | PASS   | `pipeline.eval`, `pipeline.analyze_errors`, `pipeline.run` / `inference` operate as documented; lexicon path wired with CLI overrides |
| Determinism     | PASS   | Fixed seed **42** for splits; deterministic decode (`do_sample=False`, documented beam); artifacts record decoding + lexicon config |
| Governance      | PASS   | Per-run docs (`M02_run*.md`), [M02_toolcalls.md](M02_toolcalls.md), submission discipline stated in `M02_plan.md` / `akk2eng.md` |
| CI integrity    | PASS   | Ruff + pytest maintained; no regression introduced by M02 deliverables |
| Reproducibility | PASS   | `outputs/experiments/exp_<UTC>/` snapshots with `config.json`, `metrics.json`, `predictions_dev.csv` (uncommitted; procedure reproducible from repo + data + weights) |

---

## Findings

### Strengths

- **Measurement-first** workflow is in place: dev split, chrF/BLEU, saved predictions, experiment folders.
- **Error bucketing** enables targeted hypotheses (repetition, overlap, length, numerics) instead of ad-hoc eyeballing.
- **Strong audit trail** via milestone run markdown, toolcalls log, and versioned release tag **`v0.0.5-m02`**.
- **Decoding experiments** were **isolated** (single-lever where possible) and **documented** with archives for greedy vs beam comparisons.

### Risks

- **Metric misalignment:** dev chrF/BLEU **do not** equal Kaggle leaderboard score; over-fitting dev decode without LB validation is a recurring risk.
- **Leaderboard plateau (~11.6–11.9):** public score did not establish a clear **> 11.9** sustained win through decode-only work; remaining gap is consistent with **data / normalization** limits more than **generation parameters**.
- **Lexicon no-op on dev:** validated safety and wiring, but **no demonstrated lift** on current dev predictions (no leaked forms matched).

---

## Final recommendation

```text
M02 is fit for closure.
Proceed to M03 (Normalization Engine).
```

Signed off by: **M02 closeout documentation** (this audit).  
**Summary:** [M02_summary.md](M02_summary.md)
