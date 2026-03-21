# Release Notes — v3.3.0 (External Certification Interface)

**Version:** v3.3.0  
**Tag:** v3.3.0-external-certification-interface  

---

## Highlights

- **External certification interface** — Complete verification surface: programmatic API, CLI alias, and documentation for CI and external runtimes.
- **Programmatic certification API** — Stable public API `certify_bundle(path)` from `RediAI.certification`; returns deterministic CertificationVerdict; thin wrapper over existing harness.
- **CLI verify alias** — `rediai verify` is an alias of `rediai certify`; same flags, exit codes, and full verdict JSON.
- **CI artifact verification documentation** — Exit codes, pipeline patterns, and API usage in CI (see CI_ARTIFACT_VERIFICATION.md).
- **External runtime certification documentation** — Guidance for external systems (EZRA, research, AI bundles) to integrate RediAI as an artifact trust gate (see EXTERNAL_RUNTIME_CERTIFICATION.md, EXTERNAL_CERTIFICATION_INTERFACE.md).

---

## RediAI v3 feature complete

With M83, Phase XIX (External Runtime Certification) is complete. RediAI v3 is **feature complete**. No further milestones are planned in the v3 line.

---

No runtime behavior changes to core orchestration. Certification harness (M81) and CLI (M82) behavior unchanged; API is additive.
