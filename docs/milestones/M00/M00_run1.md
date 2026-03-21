# CI Run Analysis — M00 Run 1

**Workflow:** CI  
**Run ID:** 23370891164  
**Trigger:** push  
**Branch:** main  
**Commit:** dfd2dc7 — "ci: use main branch only"  
**Date:** 2026-03-21T03:18:18Z  
**Duration:** 19s  
**URL:** https://github.com/m-cahill/akk2eng/actions/runs/23370891164  

---

## 1. Workflow Identity

| Field | Value |
|-------|-------|
| Workflow name | CI |
| Run ID | 23370891164 |
| Trigger | push |
| Branch | main |
| Commit SHA | dfd2dc701a0f6036462ba2635e1d4dee5b911cb6 |

## 2. Change Context

| Field | Value |
|-------|-------|
| Milestone | M00 (post-closeout) |
| Declared intent | CI branch config: use `main` only (remove `master`) |
| Run type | Corrective (branch rename follow-up) |

## 3. Baseline Reference

- **Last trusted green:** v0.0.1-m00 (tag 046d073)
- **Invariants:** Ruff + pytest must pass; no `continue-on-error` on required jobs

---

## Step 1 — Workflow Inventory

| Job / Check | Required? | Purpose | Pass/Fail | Notes |
|-------------|-----------|---------|-----------|-------|
| lint-and-test | ✅ Yes | Ruff lint + format + pytest | ✅ Pass | Single job, ~19s |
| Ruff check | ✅ Yes | Lint src, tests | ✅ Pass | "All checks passed!" |
| Ruff format --check | ✅ Yes | Format compliance | ✅ Pass | "14 files already formatted" |
| Pytest | ✅ Yes | Sanity tests | ✅ Pass | "2 passed in 0.37s" |

**Merge-blocking:** All checks are required; none use `continue-on-error`.

**Annotation (informational):** Node.js 20 actions deprecation warning for `actions/checkout@v4` and `actions/setup-python@v5`. Non-blocking; applies from June 2026.

---

## Step 2 — Signal Integrity Analysis

### A) Tests

- **Tier:** Sanity (unit-level pipeline + loader)
- **Failures:** None
- **Missing:** No tests for changed surface (CI YAML only); no regression risk

### B) Coverage

- **Enforced:** None (M00 scope: minimal CI, no coverage gate)
- **Exclusions:** N/A

### C) Static / Policy Gates

- **Ruff:** Enforces current reality (line-length 100, py310, E/F/I/W)
- **Format:** Check-only; no auto-fix in CI

### D) Performance / Benchmarks

- Not present

---

## Step 3 — Delta Analysis

**Files changed:** `.github/workflows/ci.yml` — `branches: [main, master]` → `branches: [main]`

**CI signals affected:** Trigger scope only; no change to lint/test logic.

**Unexpected deltas:** None.

---

## Step 4 — Failure Analysis

No failures. All steps passed.

---

## Step 5 — Invariants & Guardrails Check

| Invariant | Status |
|-----------|--------|
| Required CI checks enforced | ✅ |
| No semantic scope leakage | ✅ |
| Release/consumer contracts unchanged | ✅ |
| Determinism preserved | ✅ |

**Post-job note:** Pip cache save failed ("another job may be creating this cache") — informational only; does not affect job success.

---

## Step 6 — Verdict

> **Verdict:** This run is safe to merge. All required checks passed. The change (CI branch config) is correctly scoped and does not weaken any gate. CI remains truthful for M00.

**✅ Merge approved**

---

## Step 7 — Next Actions

| Action | Owner | Scope | Milestone |
|--------|-------|-------|-----------|
| (Optional) Update actions to Node 24–compatible versions before June 2026 | Human | `.github/workflows/ci.yml` | Post-M01 |
| (Optional) Address pip cache save warning | None | Informational | — |

---

## Summary

| Metric | Value |
|--------|-------|
| Status | ✅ Success |
| Jobs | 1/1 passed |
| Ruff check | Pass |
| Ruff format | Pass |
| Pytest | 2 passed, 0.37s |
| Blocking issues | 0 |
