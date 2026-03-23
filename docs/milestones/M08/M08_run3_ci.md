# M08 — Run 3: CI verification (GitHub Actions)

**Milestone:** M08 — Alignment-quality recovery  
**Workflow:** `.github/workflows/ci.yml` (`CI`)  
**Job:** `lint-and-test`

---

## Verification gate

```text
ALL REQUIRED CI CHECKS = GREEN
```

**Status:** ✅ **GREEN** (verified 2026-03-23)

---

## Passing workflow run (authoritative)

| Field | Value |
|-------|--------|
| **GitHub Actions run URL** | https://github.com/m-cahill/akk2eng/actions/runs/23416637937 |
| **Run database ID** | `23416637937` |
| **Workflow conclusion** | `success` |
| **Commit SHA (HEAD at trigger)** | `64e68d37af82c8138624511296f793612206771c` |
| **Display title** | `fix(ci): sanity test disables lexicon so CI works without data/train.csv` |
| **Trigger** | `push` to `main` |
| **Created (UTC)** | `2026-03-23T00:46:52Z` |
| **Updated (UTC)** | `2026-03-23T00:49:46Z` |
| **Job duration** | **~2m51s** (`lint-and-test`) |

### Step results (`lint-and-test`)

| Step | Status |
|------|--------|
| Ruff check | ✅ |
| Ruff format (check only) | ✅ |
| Pytest | ✅ (`91 passed`) |

### Warnings (non-blocking)

- GitHub **Node.js 20** deprecation notice on `actions/checkout`, `actions/setup-python`, `actions/cache` (runner platform; no job failure).
- Pytest **DeprecationWarning** (SWIG / Hugging Face stack) — same as local runs; **not** treated as failure.

---

## CI remediation (closeout sequence)

Earlier `main` pushes in this closeout sequence failed required checks until fixed:

1. **Ruff format** — `ruff format` applied to `src/` + `tests/` (commit `115ee10`).
2. **Pytest** — `tests/test_sanity.py` now passes `use_lexicon=False` so CI does not require gitignored `data/train.csv` for lexicon pair building (commit `64e68d3`).

The **green** run above is on **`64e68d3`** and is the **hard gate** for M08 closure.

---

## Kaggle

**No** `M08_run3_kaggle_submit.md` (regression milestone; no submission).

---

## Confirmation

All required jobs in workflow **CI** completed **successfully** for the verified run. No required checks were skipped or failed on the gate commit.
