# External Runtime Certification (M83)

This document describes how **external systems** (e.g. EZRA runtime, research artifact pipelines, AI model bundles) can integrate RediAI as a **certification interface**. RediAI remains **artifact-boundary pure**: it validates bundles and produces verdicts; it does not build, execute, or host runtimes.

---

## Philosophy

- RediAI **validates** artifact bundles (EPB v1.0.0 and future contracts).
- RediAI **does not** import or run external runtimes.
- External systems **call** RediAI (CLI or API) and act on the **deterministic verdict**.

---

## EZRA runtime bundles (EPB)

For EZRA Perception Bundles (EPB v1.0.0):

**CLI:**

```bash
rediai certify /path/to/epb/bundle
# or
rediai verify /path/to/epb/bundle
```

**Python API:**

```python
from RediAI.certification import certify_bundle

verdict = certify_bundle("/path/to/epb/bundle")
if verdict.certified:
    deploy()
else:
    # inspect verdict.errors, verdict.schema_valid, verdict.hash_valid
    raise SystemExit(1)
```

---

## Research artifact bundles

Same interface: pass the bundle path (directory) to `certify_bundle` or `rediai certify` / `rediai verify`. If the bundle conforms to the same EPB v1.0.0 contract (manifest, detections, state, hashes), RediAI will validate it. Future artifact types may be added under the same pattern.

---

## AI model bundles

If packaged as an EPB-compliant bundle, use the same CLI or API. RediAI does not load or run models; it only validates the bundle structure and hashes.

---

## Integration pattern

1. **Build** the bundle in your system (RediAI does not build).
2. **Call** RediAI certification (CLI or `certify_bundle`).
3. **Branch** on the verdict: certified → proceed; not certified → fail or remediate.

---

## See also

- [EXTERNAL_CERTIFICATION_INTERFACE.md](EXTERNAL_CERTIFICATION_INTERFACE.md) — Overview
- [EPB_CERTIFICATION_HARNESS.md](EPB_CERTIFICATION_HARNESS.md) — EPB scope and non-goals
- [CI_ARTIFACT_VERIFICATION.md](CI_ARTIFACT_VERIFICATION.md) — CI usage
