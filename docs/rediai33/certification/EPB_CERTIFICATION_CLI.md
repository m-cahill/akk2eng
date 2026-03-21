# EPB Certification CLI (M82)

**Command:** `rediai certify <bundle-path>`

RediAI can validate EPB v1.0.0 bundles from the command line and emit a deterministic CertificationVerdict. The CLI calls the M81 certification harness only; no certification logic lives in the CLI layer.

---

## Usage

```bash
rediai certify <bundle-path> [--output FILE] [--pretty]
```

- **&lt;bundle-path&gt;** — Path to an EPB bundle (directory containing `manifest.json`, `detections.json`, `state.json`, `hashes.json`).
- **--output**, **-o** — Write verdict JSON to a file instead of stdout.
- **--pretty**, **-p** — Pretty-print JSON (indented, sorted keys; still deterministic).

---

## Output

Full **CertificationVerdict** JSON (same structure as M81):

- `artifact_type`, `certified`, `epb_version`, `errors`, `hash_valid`, `rediai_version`, `schema_valid`, `signature_evaluated`, `signature_present`, `signature_valid`

Without `--pretty`, output is compact (no trailing newline in library; CLI may add newline). With `--pretty`, output is indented with sorted keys.

---

## Exit codes

| Code | Meaning                          |
|------|----------------------------------|
| 0    | Certification successful         |
| 1    | Schema validation failed         |
| 2    | Hash mismatch / tampered payload |
| 3    | Bundle format / load error       |

Code **3** covers: file not found, invalid path, not a bundle, unreadable or corrupted bundle (any failure before validation).

---

## CI usage

In a pipeline:

```bash
rediai certify bundle.epb
# exit 0 → certified; non-zero → fail the step
```

To capture verdict to a file:

```bash
rediai certify bundle.epb --output CertificationVerdict.json
```

---

## See also

- [EPB_CERTIFICATION_HARNESS.md](EPB_CERTIFICATION_HARNESS.md) — Harness scope and non-goals
- `tests/fixtures/epb/v1_0_0/` — Valid and tampered fixtures
- `tests/cli/` — CLI tests
