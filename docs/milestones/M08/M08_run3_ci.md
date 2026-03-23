# M08 — Run 3: CI verification (GitHub Actions)

**Milestone:** M08 — Alignment-quality recovery  
**Workflow:** `.github/workflows/ci.yml`  
**Job:** `lint-and-test` (Ruff check, Ruff format check, Pytest)

---

## Verification gate

```text
ALL REQUIRED CI CHECKS = GREEN
```

*(Details below populated after merge to `main` and workflow completion.)*

---

## Run metadata

| Field | Value |
|-------|--------|
| GitHub Actions run URL | *See below* |
| Commit SHA (on `main`) | *See below* |
| Trigger | `push` to `main` |
| Workflow conclusion | *See below* |
| Jobs | `lint-and-test` |

### Steps / statuses

| Step | Status |
|------|--------|
| Ruff check | *pending* |
| Ruff format (check only) | *pending* |
| Pytest | *pending* |

### Notes

- Warnings: upstream `DeprecationWarning` (SWIG / Hugging Face stack) may appear in logs; **no required check failures**.
- **No** `M08_run3_kaggle_submit.md` (per regression closeout).

---

## Placeholder (replaced after CI)

_RUN_METADATA_PLACEHOLDER_
