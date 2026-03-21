# External Certification Interface (M83)

This document is the **single overview** for RediAI’s external certification interface. It does not redefine project state; see `rediai-v3.md` for canonical state.

---

## Architecture overview

RediAI exposes certification in three ways, all backed by the same harness:

| Interface        | Use case                    | Entry point                          |
|------------------|-----------------------------|--------------------------------------|
| **Harness**      | Internal / implementation   | `validate_epb(path)` (internal)      |
| **CLI**          | Scripts, CI, operators      | `rediai certify` / `rediai verify`   |
| **Programmatic API** | Pipelines, tests, integrations | `certify_bundle(path)`           |

- **Stable public API:** `certify_bundle(path)` from `RediAI.certification`. Returns a deterministic `CertificationVerdict`.
- **CLI:** `rediai certify <bundle-path> [--output FILE] [--pretty]` and `rediai verify` (alias). Same behavior, full verdict JSON, exit codes 0/1/2/3.
- **Harness:** `validate_epb` remains internal; docs and integrations should use `certify_bundle`.

---

## Artifact certification philosophy

- RediAI **validates** artifact bundles (EPB v1.0.0 and future contracts).
- RediAI **does not** build bundles, execute runtimes, or host artifacts.
- Verdicts are **deterministic** (sorted keys, no timestamps/UUIDs, reproducible).

---

## CLI usage

- **Certify:** `rediai certify <bundle-path> [--output FILE] [--pretty]`
- **Verify:** `rediai verify <bundle-path> [--output FILE] [--pretty]` (alias of certify)

See [EPB_CERTIFICATION_CLI.md](EPB_CERTIFICATION_CLI.md) for details and exit codes.

---

## API usage

```python
from RediAI.certification import certify_bundle

verdict = certify_bundle("path/to/bundle")  # str or Path
assert verdict.certified  # True if schema and hash valid
# verdict.schema_valid, verdict.hash_valid, verdict.errors
```

See `RediAI/certification/api.py` and `tests/certification_api/`.

---

## CI integration

Use CLI or API to gate deploy on certification. See [CI_ARTIFACT_VERIFICATION.md](CI_ARTIFACT_VERIFICATION.md) for exit codes and examples.

---

## External runtime integration

External systems (EZRA, research pipelines, AI model bundles) call RediAI as a trust gate; RediAI does not import or run those systems. See [EXTERNAL_RUNTIME_CERTIFICATION.md](EXTERNAL_RUNTIME_CERTIFICATION.md).

---

## Pointers

| Topic           | Document / location |
|----------------|----------------------|
| Harness scope  | [EPB_CERTIFICATION_HARNESS.md](EPB_CERTIFICATION_HARNESS.md) |
| CLI            | [EPB_CERTIFICATION_CLI.md](EPB_CERTIFICATION_CLI.md) |
| CI patterns    | [CI_ARTIFACT_VERIFICATION.md](CI_ARTIFACT_VERIFICATION.md) |
| External runtime | [EXTERNAL_RUNTIME_CERTIFICATION.md](EXTERNAL_RUNTIME_CERTIFICATION.md) |
| API            | `RediAI.certification.api.certify_bundle` |
| Fixtures       | `tests/fixtures/epb/v1_0_0/` |
| Tests          | `tests/certification/`, `tests/cli/`, `tests/certification_api/` |
