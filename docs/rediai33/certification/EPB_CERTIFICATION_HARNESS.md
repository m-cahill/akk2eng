# EPB Certification Harness (M81)

**Scope:** RediAI v3.1.0 extends its perimeter with a deterministic **EPB (EZRA Perception Bundle) certification harness**. This document describes scope, non-goals, and usage.

## Scope

- **Validate EPB v1.0.0 bundles** (directory or future zip) against the vendored EPB schema and canonicalization rules.
- **Recompute canonical hash** from contract rules (clean-room implementation; **no EZRA imports**).
- **Confirm embedded hash matches** recomputed bundle and file hashes.
- **Emit deterministic CertificationVerdict JSON** (sorted keys, no timestamps/UUIDs, deterministic error ordering).
- **Signature handling:** Parse signature fields if present; set `signature_evaluated: false`, `signature_valid: null` (no crypto in v3.1.0).

## Non-goals

- **No SBOM / SLSA provenance / PyPI linkage / rebuild reproducibility** — those remain EZRA responsibilities.
- **No EZRA runtime dependency** — RediAI must never `import ezra` or depend on EZRA code. Only vendored schema/spec artifacts and bundle files are consumed.

## Deterministic verdict contract

Verdict JSON:

- Sorted keys
- No timestamps, no UUIDs
- Errors list sorted deterministically
- Fields: `artifact_type`, `certified`, `epb_version`, `errors`, `hash_valid`, `rediai_version`, `schema_valid`, `signature_evaluated`, `signature_present`, `signature_valid`

## Source of truth for schema/spec

- **EPB v1.0.0 spec:** Vendored from EZRA `docs/specs/epb_v1/EPB_V1_SPEC.md` → `docs/v3refactor/certification/EPB_V1_SPEC.md`.
- **Schemas:** Vendored from EZRA `docs/specs/epb_v1/schemas/*.schema.json` → `RediAI/certification/epb/schema/`.
- When updating: copy from EZRA repo and document the EZRA tag/commit in this file.

## Pointers

- **Schema dir:** `RediAI/certification/epb/schema/`
- **Fixtures:** `tests/fixtures/epb/v1_0_0/valid/`, `tampered_payload/`, `tampered_hash/`
- **Tests:** `tests/certification/` (includes no-EZRA-import guardrail)
- **API:** `certify_bundle(path)` (stable public API) from `RediAI.certification`; `validate_epb` is internal. See [EXTERNAL_CERTIFICATION_INTERFACE.md](EXTERNAL_CERTIFICATION_INTERFACE.md).

## CI

- Required step: `pytest tests/certification/` (see `.github/workflows/ci.yml`).
