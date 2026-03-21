# CI Artifact Verification (M83)

This document describes **CI-friendly patterns** for using RediAI certification to verify EPB (or other certified) bundles before deploy. It does not redefine project state; see [EXTERNAL_CERTIFICATION_INTERFACE.md](EXTERNAL_CERTIFICATION_INTERFACE.md) for the overview.

---

## Exit codes

| Code | Meaning                          |
|------|----------------------------------|
| 0    | Certification successful         |
| 1    | Schema validation failed         |
| 2    | Hash mismatch / tampered payload |
| 3    | Bundle format / load error       |

Use these in pipeline conditionals; **do not deploy** when exit code is non-zero.

---

## CLI in CI

```bash
# Fail the step if not certified
rediai certify path/to/bundle
# or alias:
rediai verify path/to/bundle
```

With options:

```bash
rediai certify path/to/bundle --output verdict.json --pretty
```

Example pipeline (conceptual):

1. **Build** the bundle (external to RediAI).
2. **Certify** with `rediai certify path/to/bundle` (or `rediai verify`).
3. **Deploy** only if exit code is 0.

---

## Programmatic API in CI

From Python (e.g. in a CI script or test):

```python
from RediAI.certification import certify_bundle

verdict = certify_bundle("path/to/bundle")
if verdict.certified:
    # proceed to deploy or next step
    pass
else:
    raise SystemExit(1)  # or use exit code 1, 2, 3 per verdict
```

The same exit-code semantics apply: schema failure → 1, hash failure → 2, load error → 3. Map from `verdict.errors` and `verdict.schema_valid` / `verdict.hash_valid` if you need to distinguish.

---

## See also

- [EPB_CERTIFICATION_CLI.md](EPB_CERTIFICATION_CLI.md) — CLI usage and flags
- [EXTERNAL_CERTIFICATION_INTERFACE.md](EXTERNAL_CERTIFICATION_INTERFACE.md) — Overview and architecture
