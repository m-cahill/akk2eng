# RediAI v3 Documentation

## Overview

RediAI v3 began as a clean clone of RediAI v2.1.0-frozen. This document serves as the primary reference for v3 development.

**Base Version:** v2.1.0-frozen
**Initial Tag:** v3.0.0-baseline
**Date:** 2026-01-02

---

## Documentation Authority Model

RediAI v3 documentation follows a strict authority hierarchy:

**Level 0 — Tags**  
  `v3.0.0-operational-lock`  
  `v3.0.1-proprietary-license`  
  `v3.1.0-external-certification`

**Level 1 — Canonical State**  
  `rediai-v3.md` (this document)

**Level 2 — Phase Declarations**  
  `PHASE_XVII_CLOSEOUT.md`

**Level 3 — Architecture Policy**  
  `ARCHITECTURE_POLICY.md`

**Level 4 — Milestone Artifacts**  
  `docs/v3refactor/Milestones/...`

**Level 5 — Entry Documents**  
  `README.md`

All documents other than `rediai-v3.md` are subordinate and must not redefine project state.

---

## v3 Milestones

| Milestone | Description | Status |
|-----------|-------------|--------|
| **M0** | Freeze v2.1 baseline | ✅ Complete |
| **M1** | Repository initialization & baseline hardening | ✅ Complete |
| **M2** | CI re-baselining & deferred failure codification | ✅ Complete |
| **M2.1** | CI unblock (7 iterations) | ✅ Complete |
| **M3** | Structural intent & guardrails | ✅ Complete |
| **M4** | Code quality remediation | ✅ Complete |
| **M5** | Contract package extraction | ✅ Complete |
| **M6** | Ports & Adapters (Phase II) | ✅ Complete |
| **M7** | Phase III Kickoff — Close Gates | ✅ Complete |
| **M8** | Phase IV — Operational Hardening | ✅ Complete |
| **M9** | Phase V — Release Lock | ✅ Complete |
| **M10** | Phase V — Local CI Harness + MVP | ✅ Complete (Phase V Closed) |
| **M11** | Phase VI — Workflow Hygiene | ✅ Complete |
| **M12** | Phase VI — Contract Completion | ✅ Complete |
| **M13** | Phase VI — API Contract Hardening | ✅ Complete |
| **M14** | Phase VI — CI Timeout Hardening | ✅ Complete (Phase VI Closed) |
| **M15** | Phase VII — CONTRACT-001 Triage | ✅ Complete |
| **M16** | Phase VII — AUTH-API-003 Resolution | ✅ Complete |
| **M17** | Phase VII — Infrastructure Closure | ✅ Complete |
| **M18** | Phase VII — TEST-MOCK-001 Resolution | ✅ Complete |
| **M19** | Phase VII — Fixture Hygiene (No-Op) | ✅ Complete |
| **M20** | Phase VII — Formal Closure | ✅ Complete (Phase VII Closed) |
| **M21** | Phase VIII — Scoping & Selection | ✅ Complete |
| **M22** | Phase VIII — SEC-SEM-002 Resolution | ✅ Complete |
| **M23** | Phase VIII — CI-006 Resolution | ✅ Complete |
| **M24** | Phase VIII — AUTH-API-002 Resolution | ✅ Complete |
| **M25** | Phase VIII — INFRA-OTEL-002 Resolution | ✅ Complete |
| **M26** | Phase VIII — API-CONTRACT-001 Resolution | ✅ Complete |
| **M27** | Phase VIII — API-ROUTE-404-001 Resolution | ✅ Complete |
| **M28** | Phase VIII — TEST-MOCK-001 Resolution | ✅ Complete |
| **Phase VIII** | **Formal Closure — Targeted Deferred Issue Resolution** | 🔒 **CLOSED** |
| **M29** | Phase IX — CI-TEST-CLUSTER-001 Resolution | ✅ Complete |
| **M30** | Phase IX — CI-TEST-TIER-001 Resolution | ✅ Complete |
| **M31** | Phase IX — CI-TEST-COVERAGE-001 Resolution | ✅ Complete |
| **M32** | Phase IX — CI-QUALITY-POLICY-001 Resolution | ✅ Complete |
| **Phase IX** | **CI Truthfulness & Debt Collapse** | 🔒 **CLOSED** |
| **M33** | Phase X — ARCH-POLICY-SPEC-001 (Policy Normalization) | ✅ Complete |
| **M34** | Phase X — ARCH-EXC-RETIRE-001 (First Exception Retired) | ✅ Complete |
| **M35** | Phase X — ARCH-EXC-RETIRE-002 (Second Exception Retired) | ✅ Complete |
| **Phase X** | **Architecture Normalization & Exception Retirement** | 🔒 **CLOSED** |
| **M36** | Phase XI — Governance Frameworks (Decision Matrix, Spike Plan, Rubric) | ✅ Complete |
| **M37** | Phase XI — ARCH-INFRA-001 Resolution (serving/ merged into api/) | ✅ Complete |
| **M38** | Phase XI — ARCH-INFRA-002 Resolution (TelemetryPort + adapters) | ✅ Complete |
| **M39** | Phase XI — ARCH-INFRA-003 Resolution (Same-layer by design) | ✅ Complete |
| **M40** | Phase XI — CI Signal Restoration (Unit Smoke introduced) | ✅ Complete |
| **M41** | Phase XI — ARCH-INFRA-005 Resolution (MessageQueuePort) | ✅ Complete |
| **M42** | Phase XI — UI Extraction Preparation (Plan-Only) | ✅ Complete |
| **M43** | Phase XI — Data Extraction Preparation (Plan-Only) | ✅ Complete |
| **M44** | Phase XI — Closure & Extraction Readiness Lock | ✅ Complete |
| **M45** | Phase XI — ARCH-INFRA-006 Corrective (registry→composition) | ✅ Complete |
| **Phase XI** | **Extraction Readiness & Boundary Retirement** | 🔒 **CLOSED** |
| **M46** | Phase XII — UI Package Extraction (rediai-ui scaffold) | ✅ Complete |
| **M47** | Phase XII — Data Package Extraction (rediai-data + services) | ✅ Complete |
| **M48** | Phase XII — Contracts Hardening & Versioning | ✅ Complete |
| **M49** | Phase XII — Core / Foundation Extraction (rediai-core + shims) | ✅ Complete |
| **M50** | Phase XII — Shim Retirement (CP3 + CP4) | ✅ Complete |
| **Phase XII** | **Component Separation (Execution)** | 🔒 **CLOSED** |
| **M51** | Phase XIII — ARCH-API-COMP-001 Resolution (API→Composition) | ✅ Complete |
| **M52** | Phase XIII — ARCH-INFRA-004 Resolution (Registry→Auditing→Persistence) | ✅ Complete |
| **M53** | Phase XIII — Domain Test Failures Part 1 (ORM + API Mismatches) | ✅ Complete |
| **M54** | Phase XIII — DOMAIN-FIX-001 Resolution (Fixture Cleanup + Collection Errors) | ✅ Complete |
| **M54b** | Phase XIII — DOMAIN-GATE-001 Resolution (Gate Class API Alignment) | ✅ Complete |
| **M55** | Phase XIII — DOMAIN-GATE-002 Resolution (Gate Context Compatibility) | ✅ Complete |
| **M56** | Phase XIII — DOMAIN-EVENT-001 Resolution (OpenLineageEvent API) | ✅ Complete |
| **Phase XIII** | **Runtime & Operational Hardening** | 🔒 **CLOSED** |
| **M57** | Phase XIV — Phase XIV Kickoff & Triage Snapshot | ✅ Complete |
| **M58** | Phase XIV — Event-Streaming Semantic Triage | ✅ Complete |
| **M59** | Phase XIV — DOMAIN-STREAM-001 Resolution | ✅ Complete |
| **M60** | Phase XIV — DOMAIN-PUB-001 Resolution | ✅ Complete |
| **M61** | Phase XIV — DOMAIN-CONS-001 Resolution | ✅ Complete |
| **M62** | Phase XIV — DOMAIN-NATS-001 Resolution | ✅ Complete |
| **M63** | Phase XIV — DOMAIN-INTEG-001 Resolution | ✅ Complete |
| **M64** | Phase XIV — Release Policy Definition (XIV-A) | ✅ Complete |
| **M65** | Phase XIV — Release Automation (XIV-B) | ✅ Complete |
| **M66a** | Phase XIV — Version Source Alignment | ✅ Complete |
| **M66** | Phase XIV — First Release Candidate (RC-0) | ✅ Complete |
| **M67** | Phase XIV — CI-BENCH-001 Resolution (Benchmark Tests) | ✅ Complete |
| **M68** | Phase XIV — CI-BENCH-002 Resolution (Benchmark Publishing) | ✅ Complete |
| **M69** | Phase XIV — COV-TRACE-001 Resolution (Trace Coverage Gate) | ✅ Complete |
| **M70** | Phase XIV — COV-BENCH-001 Resolution (Benchmark Coverage Scope) | ✅ Complete |
| **Phase XIV** | **Semantic Correction & Release Lock** | 🔒 **CLOSED** |
| **PreM75** | Phase XVI — Pre-Phase XVI Readiness Check | ✅ Complete |
| **M75** | Phase XVI — Coverage & Cleanliness Baseline (entry baseline + CI hygiene) | ✅ Complete |
| **M75b** | Phase XVI — 25% Coverage Ramp (OTEL-001 closed, fail_under 17→21) | ✅ Complete |
| **M75c** | Phase XVI — 45% Coverage Ramp (AUTH-DEV-001 + FIND-001 closed, fail_under 21→38) | ✅ Complete |
| **M75d** | Phase XVI — Registry Coverage Ramp (1,378+ tests, fail_under 38→52, CI QG 60.0%) | ✅ Complete |
| **M75e** | Phase XVI — Enforcement Hardening (CI-ENFORCE-001/002 + DATA-VALID-001 + LOG-STRUCT-001 closed, CI QG 61.55%) | ✅ Complete |
| **Phase XVI** | **Coverage & Clean Close Program** | 🟢 **ACTIVE** |
| **M76** | Phase XVII — Runtime Measurement Baseline | ✅ Complete |
| **M77** | Phase XVII — Training Initiation Investigation (no bottleneck) | ✅ Complete |
| **M78** | Phase XVII — Adapter Lifecycle Investigation (no bottleneck) | ✅ Complete |
| **M79** | Phase XVII — v3 Release Lock & Operational Closeout | ✅ Complete |
| **Phase XVII** | **Operational & Runtime Hardening** | 🔒 **CLOSED** |
| **M80** | Phase XVIII — Proprietary License Conversion (All Rights Reserved) + README freeze banner | ✅ Complete |
| **Phase XVIII** | **Post-Lock Governance (M80)** | 🔒 **CLOSED** |
| **M81** | Phase XIX — EPB External Runtime Certification Harness (EPB-only, v3.1.0) | ✅ Complete |
| **M82** | Phase XIX — EPB Certification CLI | ✅ Complete |
| **M83** | Phase XIX — External Certification Interface | ✅ Complete |
| **Phase XIX** | **External Runtime Certification (M81–M83)** | 🔒 **COMPLETE** |

---

## Milestone ID Reconciliation

> **Note:** The label **M45** was used for a Phase XI corrective (ARCH-INFRA-006). The Phase XII roadmap item "Contracts Hardening & Versioning" (originally planned as M45 in V3_ROADMAP_r2.md) was executed as **M48** to preserve immutability of closed milestones.

---

## Database Schema

See `rediai.md` for complete database schema documentation (inherited from v2.1).

---

## Known Deferred Issues

See [Deferred Issues Registry](docs/v3refactor/audit/DeferredIssuesRegistry.md) for complete tracking.

| Issue | Component | Status | Target |
|-------|-----------|--------|--------|
| ~~Missing `requirements-ci.txt`~~ | CI setup action | ✅ **FIXED** | M1 |
| ~~Missing `requirements-docs.txt`~~ | Docs workflows | ✅ **FIXED** | M1 |
| ~~JSONDecodeError~~ | `incremental_audit.py` | ✅ **FIXED** | M2 |
| ~~Async execution bugs (CI-004)~~ | Benchmark system | ✅ **FIXED** | M3 |
| Integration test flakiness (CI-005) | Keycloak tests | ⏳ Deferred | M5+ |
| ~~flake8 JSON format (CI-006)~~ | `incremental_audit.py` | ✅ **FIXED** | M23 |
| ~~Flake8 violations (CI-007)~~ | Linters | ✅ **FIXED** | M4 |
| Pylint debt (CI-008) | Code quality | ⏳ Deferred (guardrailed) | M5+ |
| MyPy strict (CI-009) | Type checking | ⏳ Deferred (scoped) | M5+ |
| ~~Shim retirement (ARCH-M49-001)~~ | Core extraction | ✅ **RESOLVED** | M50 |
| ~~API→Composition violation (ARCH-API-COMP-001)~~ | Architecture | ✅ **RESOLVED** | M51 |
| Bandit/Safety (CI-010/011) | Security scans | ⏳ Deferred (reviewed) | M5+ |
| Pydocstyle (CI-012) | Docstrings | ⏳ Deferred (scoped) | M7+ |
| Radon complexity (CI-013) | Maintainability | ⏳ Deferred (baseline) | M7+ |
| ~~Layer violations (ARCH-001)~~ | Architecture | ✅ **REDUCED** (13→6) | M6 |
| ~~Coverage <15% (CI-014)~~ | Testing | ✅ **FIXED** | M4 |
| ~~Disk space exhaustion (CI-015)~~ | Workflows | ✅ **FIXED** | M4 |
| ~~Broken test files (CI-016)~~ | Legacy tests | ✅ **FIXED** | M4 |
| ~~Upload metrics parsing (CI-017)~~ | Scripts | ✅ **FIXED** | M4 |
| Compliance stubs (COMP-001) | GDPR/HIPAA | ⏳ Deferred | M5+ |

---

## Audit Status

See [Score Trend](docs/v3refactor/audit/ScoreTrend.md) for detailed scoring.
See [Phase VI Audit](docs/v3refactor/audit/v3PhaseVIaudit.md) for the latest comprehensive v2.1 vs v3 progress audit.
See [M6 Comprehensive Audit](docs/v3refactor/audit/v3M6audit.md) for the M6 milestone audit.

| Milestone | Overall Score | Status |
|-----------|---------------|--------|
| v2.1 Baseline | 3.8 | Reference |
| M1 | 3.8 | ✅ Complete |
| M2 + M2.1 | 3.9 | ✅ Complete (CI recovered + hardened) |
| M3 + M3.1 | 4.2 | ✅ Complete (structural foundation) |
| M4 | 4.5 | ✅ Complete (quality remediation) |
| M5 | 4.7 | ✅ Complete (contract extraction) |
| M6 | 4.70 | ✅ Complete (ports & adapters, full audit) |
| M7 | 4.85 | ✅ Complete (SEC-001 & ARCH-002 resolved, gates enforced) |
| M8 | 4.85 | ✅ Complete (CI-023/24/25/26 resolved, baselines established) |
| M9 | 4.9 | ✅ Complete (Phase V Release Lock, 17 runs, CI honest) |
| M10 | 4.9 | ✅ Complete (Phase V Closed, 10 runs, MVP validated) |
| M11 | 4.9 | ✅ Complete (Phase VI, SEC-VAL-001 resolved, workflow hygiene) |
| M12 | 4.9 | ✅ Complete (Phase VI, TrainingConfig contract, OpenLineage governance) |
| M13 | 4.9 | ✅ Complete (Phase VI, API-001 resolved, contract drift documented) |
| M14 | 4.9 | ✅ Complete (Phase VI, TIMEOUT-001 resolved, CI hardening) |
| **Phase VI** | **4.9** | ✅ **Complete** |
| M15 | 4.9 | ✅ Complete (Phase VII, CONTRACT-001 triage, 23/25 tests fixed) |
| M16 | 4.9 | ✅ Complete (Phase VII, AUTH-API-003 resolved) |
| M17 | 4.9 | ✅ Complete (Phase VII, INFRA-OTEL-001 + AUTH-DI-001 resolved) |
| M18 | 4.9 | ✅ Complete (Phase VII, TEST-MOCK-001 resolved) |
| M19 | 4.9 | ✅ Complete (Phase VII, No-Op closure) |
| M20 | 4.9 | ✅ Complete (Phase VII, Formal closure attestation) |
| **Phase VII** | **4.9** | ✅ **Complete (Formal closure, Phase VIII handoff ready)** |
| M21 | 4.9 | ✅ Complete (Phase VIII, Scoping & selection) |
| M22 | 4.9 | ✅ Complete (Phase VIII, SEC-SEM-002 resolved) |
| M23 | 4.9 | ✅ Complete (Phase VIII, CI-006 resolved) |
| M24 | 4.9 | ✅ Complete (Phase VIII, AUTH-API-002 resolved) |
| M25 | 4.9 | ✅ Complete (Phase VIII, INFRA-OTEL-002 resolved) |
| M26 | 4.9 | ✅ Complete (Phase VIII, API-CONTRACT-001 resolved) |
| M27 | 4.9 | ✅ Complete (Phase VIII, API-ROUTE-404-001 resolved) |
| M28 | 4.9 | ✅ Complete (Phase VIII, TEST-MOCK-001 resolved) |
| **Phase VIII** | **4.9** | 🔒 **FORMALLY CLOSED** |
| M29 | 4.9 | ✅ Complete (Phase IX, CI-TEST-CLUSTER-001 resolved) |
| M30 | 4.9 | ✅ Complete (Phase IX, CI-TEST-TIER-001 resolved) |
| M31 | 4.9 | ✅ Complete (Phase IX, CI-TEST-COVERAGE-001 resolved) |
| M32 | 4.9 | ✅ Complete (Phase IX, CI-QUALITY-POLICY-001 resolved) |
| **Phase IX** | **4.9** | 🔒 **FORMALLY CLOSED** |
| M33 | 4.9 | ✅ Complete (Phase X, ARCH-POLICY-SPEC-001 resolved) |
| M34 | 4.9 | ✅ Complete (Phase X, ARCH-EXC-RETIRE-001 resolved) |
| M35 | 4.9 | ✅ Complete (Phase X, ARCH-EXC-RETIRE-002 resolved) |
| **Phase X** | **4.9** | 🔒 **CLOSED** |
| M36 | 4.9 | ✅ Complete (Phase XI, Governance frameworks) |
| M37 | 4.9 | ✅ Complete (Phase XI, ARCH-INFRA-001 resolved) |
| M38 | 4.9 | ✅ Complete (Phase XI, ARCH-INFRA-002 resolved) |
| M39 | 4.9 | ✅ Complete (Phase XI, ARCH-INFRA-003 resolved) |
| M40 | 4.9 | ✅ Complete (Phase XI, CI Signal Restoration — Unit Smoke) |
| M41 | 4.9 | ✅ Complete (Phase XI, ARCH-INFRA-005 resolved — MessageQueuePort) |
| M42 | 4.9 | ✅ Complete (Phase XI, UI Extraction Preparation — zero drift baseline) |
| M43 | 4.9 | ✅ Complete (Phase XI, Data Extraction Preparation — coupling inventory) |
| M44 | 4.9 | ✅ Complete (Phase XI, Closure — extraction readiness certified) |
| M45 | 4.9 | ✅ Complete (Phase XI, ARCH-INFRA-006 corrective — registry→composition fix) |
| **Phase XI** | **4.9** | 🔒 **CLOSED** |
| M46 | 4.9 | ✅ Complete (Phase XII, UI Package Extraction — workspace package + CI guardrails) |
| M47 | 4.9 | ✅ Complete (Phase XII, Data Package Extraction — rediai-data + 6 service interfaces) |
| M48 | 4.9 | ✅ Complete (Phase XII, Contracts Hardening — deterministic codegen + CI truthful) |
| M49 | 4.9 | ✅ Complete (Phase XII, Core Extraction — rediai-core package + shims) |
| M50 | 4.95 | ✅ Complete (Phase XII, Shim Retirement — consumers migrated, extraction complete) |
| **Phase XII** | **4.95** | 🔒 **CLOSED** |
| M51 | 4.95 | ✅ Complete (Phase XIII, ARCH-API-COMP-001 resolved — API boundary hardened) |
| M52 | 4.95 | ✅ Complete (Phase XIII, ARCH-INFRA-004 resolved — infrastructure exceptions eliminated) |
| M53 | 4.95 | ✅ Complete (Phase XIII, Domain API repair — DOMAIN-ORM-001/API-001/API-002 resolved) |
| M54 | 4.95 | ✅ Complete (Phase XIII, Fixture cleanup — DOMAIN-FIX-001 resolved, zero collection errors) |
| M54b | 4.95 | ✅ Complete (Phase XIII, Gate API alignment — DOMAIN-GATE-001 resolved, shape alignment complete) |
| M55 | 4.95 | ✅ Complete (Phase XIII, Gate Context Compatibility — DOMAIN-GATE-002 resolved, 30/30 gate tests) |
| M56 | 4.96 | ✅ Complete (Phase XIII, OpenLineageEvent API — DOMAIN-EVENT-001 resolved, 6/6 event tests) |
| **Phase XIII** | **4.96** | 🔒 **CLOSED** |
| M57 | 4.96 | ✅ Complete (Phase XIV, Kickoff & Triage Snapshot — baseline verified, 7 issues tracked) |
| M58 | 4.96 | ✅ Complete (Phase XIV, Event-Streaming Triage — 27 failures categorized into 5 buckets) |
| M59 | 4.97 | ✅ Complete (Phase XIV, DOMAIN-STREAM-001 Resolved — RegistryEventStreamer 9/9 tests pass) |
| M60 | 4.98 | ✅ Complete (Phase XIV, DOMAIN-PUB-001 Resolved — EventPublisher 5/5 tests pass) |
| M61 | 4.98 | ✅ Complete (Phase XIV, DOMAIN-CONS-001 Resolved — EventConsumer 7/7 tests pass) |
| M62 | 4.98 | ✅ Complete (Phase XIV, DOMAIN-NATS-001 Resolved — RegistryNATSManager 5/5 tests pass) |
| PreM75 | 4.96 | ✅ Complete (Phase XVI, Pre-Entry Readiness — CI verified green, Phase XVI entry authorized) |
| M75 | 4.96 | ✅ Complete (Phase XVI, Coverage Baseline — 19.6% CI baseline frozen, OTEL-001/AUTH-DEV-001/FIND-001 triaged, ramp plan declared) |
| M75b | 4.97 | ✅ Complete (Phase XVI, 25% Ramp — OTEL-001 closed, 235+ tests added, fail_under 17→21, Quality Gate 51.19%) |
| M75c | 4.97 | ✅ Complete (Phase XVI, 45% Ramp — AUTH-DEV-001 + FIND-001 closed, 136+ tests added, fail_under 21→38, Quality Gate 52.40%) |
| M75d | 4.97 | ✅ Complete (Phase XVI, Registry Coverage Ramp — 1,378+ tests added, fail_under 38→52, Quality Gate 60.0%) |
| M75e | 4.98 | ✅ Complete (Phase XVI, Enforcement Hardening — CI-ENFORCE-001/002 + DATA-VALID-001 + LOG-STRUCT-001 closed, 378+ tests added, fail_under 52 (unchanged), Quality Gate 61.55%; CI now structurally truthful) |

**Phase VIII Closure:** See [Phase_VIII_CLOSURE.md](docs/v3refactor/Milestones/Phase8/Phase_VIII_CLOSURE.md) for comprehensive closure documentation.

**Phase IX Closure:** See [M32_summary.md](docs/v3refactor/Milestones/Phase9/M32_summary.md) for Phase IX closure documentation.

**Phase X Closure:** See [M35_summary.md](docs/v3refactor/Milestones/Phase10/M35_summary.md) for architecture normalization and exception retirement documentation.

**Phase XI Closure:** See [M44_summary.md](docs/v3refactor/Milestones/Phase11/M44_summary.md) for extraction readiness and boundary retirement documentation.

**Phase XII Closure:** See [PhaseXII_Closeout.md](docs/v3refactor/Milestones/Phase12/PhaseXII_Closeout.md) for component separation execution and core extraction documentation.

**Phase XIII Closure:** See [phaseXIII-closeout.md](docs/v3refactor/SupraphaseB/phaseXIII-closeout.md) for runtime and operational hardening documentation.

**Phase XIV Closure:** Phase XIV (Semantic Correction & Release Lock) closed 2026-01-19 with M70. RC-0 shipped, benchmark publishing established, trace coverage gate truthful.

**Phase XVI Entry:** Pre-Phase XVI readiness verified 2026-02-28. See [PreM75_plan.md](docs/v3refactor/Milestones/Phase16/PreM75/PreM75_plan.md) and [PreM75_run1.md](docs/v3refactor/Milestones/Phase16/PreM75/PreM75_run1.md) for CI verification evidence.

**M75 (Coverage Baseline):** Phase XVI entry milestone closed 2026-02-28. Baseline frozen at 19.6% CI. Three must-close items triaged (OTEL-001, AUTH-DEV-001, FIND-001). Ramp plan M75b–M75f declared. See [M75_summary.md](docs/v3refactor/Milestones/Phase16/M75/M75_summary.md).

**M75b (25% Ramp):** Closed 2026-02-28. OTEL-001 closed. 235+ behavioral tests added across auditing, ports, composition, telemetry, and rediai_core. Quality Gate confirms 51.19% (≥25% target). `fail_under` raised 17→21. Pre-existing `event.meta_data` bug fixed in `auditing/decorators.py`. See [M75b_summary.md](docs/v3refactor/Milestones/Phase16/M75b/M75b_summary.md). PR: #97.

**M75c (45% Ramp):** Closed 2026-02-28. AUTH-DEV-001 closed (production auth bypass eliminated; `ENVIRONMENT` default changed to `"production"`; 5 regression tests). FIND-001 retired (mystery skip replaced with 404 contract assertion). 136+ behavioral tests added across registry.metrics, registry.publication_config, storage.s3, queue adapters. Quality Gate confirms 52.40% (≥45% target). `fail_under` raised 21→38 in pyproject.toml and .coveragerc. See [M75c_summary.md](docs/v3refactor/Milestones/Phase16/M75c/M75c_summary.md). PR: #100.

**M75d (Registry Coverage Ramp):** Closed 2026-03-01. 1,378+ tests added across 27 files targeting registry core, supporting modules, and zero-coverage modules. Quality Gate confirms 60.0% (≥60% target). `fail_under` raised 38→52. Four production bugs documented (DATA-VALID-001 × 3, LOG-STRUCT-001). See [M75d_summary.md](docs/v3refactor/Milestones/Phase16/M75d/M75d_summary.md). PR: #101.

**M75e (Enforcement Hardening):** Closed 2026-03-01. CI enforcement became structurally truthful: CI-ENFORCE-001 closed (coverage gate reads fail_under=52 from pyproject.toml, 37pp hardcode gap eliminated), CI-ENFORCE-002 closed (tests/unit/ 1,501 tests blocking on ubuntu-latest). DATA-VALID-001 closed (3 ORM column bugs fixed). LOG-STRUCT-001 closed (StructuredLogger exc_info bug fixed). Security env defaults aligned to "production" (app.py). 378+ behavioral tests added. Quality Gate 61.55%. `fail_under` remains 52 (per exit logic, <70% bucket). See [M75e_summary.md](docs/v3refactor/Milestones/Phase16/M75e/M75e_summary.md).

**Phase XVII Closure:** Phase XVII (Operational & Runtime Hardening) closed 2026-03-03 with M79. M76 established runtime baseline; M77/M78 confirmed no measurable bottleneck in training initiation or adapter lifecycle. v3 declared **Operationally Hardened (Baseline Verified)**. Tag `v3.0.0-operational-lock` prepared; see [PHASE_XVII_CLOSEOUT.md](docs/v3refactor/PHASE_XVII_CLOSEOUT.md) and [M79_summary.md](docs/v3refactor/Milestones/Phase17/M79/M79_summary.md).

**M80 (Phase XVIII):** Post-lock governance maintenance completed 2026-03-03. License converted to proprietary (All Rights Reserved); README updated with freeze banner and private posture; no code or CI change. Tag `v3.0.1-proprietary-license` applied to M80 commit `34d006d3`. See [M80_summary.md](docs/v3refactor/Milestones/Phase18/M80/M80_summary.md).

**M81 (Phase XIX):** EPB External Runtime Certification Harness. Status: Closed. CI Validation: 22690183881 / 22690183921. Outcome: v3.1.0-external-certification. See [M81_summary.md](docs/v3refactor/Milestones/Phase19/M81/M81_summary.md), [M81_plan.md](docs/v3refactor/Milestones/Phase19/M81/M81_plan.md), [EPB_CERTIFICATION_HARNESS.md](docs/v3refactor/certification/EPB_CERTIFICATION_HARNESS.md).

**M82 (Phase XIX):** EPB Certification CLI. Status: Closed. Command: `rediai certify <bundle-path> [--output FILE] [--pretty]`. Full CertificationVerdict JSON; exit codes 0/1/2/3; deterministic output; CI runs `pytest tests/cli/`. Outcome: v3.2.0-epb-cert-cli. See [M82_summary.md](docs/v3refactor/Milestones/Phase19/M82/M82_summary.md), [M82_plan.md](docs/v3refactor/Milestones/Phase19/M82/M82_plan.md), [EPB_CERTIFICATION_CLI.md](docs/v3refactor/certification/EPB_CERTIFICATION_CLI.md).

**M83 (Phase XIX):** External Certification Interface. Status: Closed. Stable programmatic API `certify_bundle(path)`; CLI alias `rediai verify`; CI and external-runtime documentation; example pipeline (stubs). Outcome: v3.3.0-external-certification-interface. See [M83_summary.md](docs/v3refactor/Milestones/Phase19/M83/M83_summary.md), [M83_plan.md](docs/v3refactor/Milestones/Phase19/M83/M83_plan.md), [EXTERNAL_CERTIFICATION_INTERFACE.md](docs/v3refactor/certification/EXTERNAL_CERTIFICATION_INTERFACE.md).

## RediAI v3 — Feature Complete

**RediAI v3 is feature complete.**

Phase XIX (External Runtime Certification) is complete. RediAI now provides:

- **EPB certification harness** (M81): Deterministic validation of EPB v1.0.0 bundles; schema and hash integrity; no EZRA imports.
- **Certification CLI** (M82): `rediai certify` and `rediai verify`; full CertificationVerdict JSON; exit codes 0/1/2/3; CI-compatible.
- **Programmatic certification API** (M83): `certify_bundle(path)` as stable public interface; thin wrapper over harness.
- **CI artifact verification pattern**: Gate deploy on certification; document exit codes and pipeline usage.
- **External runtime certification interface**: Documentation and example for external systems (EZRA, research, AI bundles) to use RediAI as a deterministic artifact trust gate.

RediAI acts as a **deterministic artifact certification layer** for AI systems and external runtimes, without building, executing, or hosting those runtimes.

## v3.1.0 Declaration

RediAI v3.1.0 introduces the EPB certification harness, enabling RediAI to validate and certify external artifact bundles while preserving the frozen runtime core.

## v3.2.0 Declaration

RediAI v3.2.0 adds the EPB certification CLI (`rediai certify`), providing a CI-compatible, deterministic certification interface. The CLI calls the M81 harness only; no certification logic resides in the CLI layer.

## v3.3.0 Declaration

RediAI v3.3.0 completes the external certification interface: programmatic API (`certify_bundle`), CLI verify alias, CI and external-runtime documentation, and example pipeline. RediAI v3 is feature complete; Phase XIX is complete.

---

**Target:** 5.0 (achieved Architecture 5.0, Modularity 5.0, Tests & CI 5.0, Security 5.0, DX 5.0, Docs 5.0)

### Coverage Margin Policy

Quality Gate enforces coverage from pyproject.toml (currently 60%).

Project policy requires maintaining at least a 2% safety margin.
Coverage must not drop below 62% without an ADR.

---

## Architecture

v3 implements a monorepo structure with the following packages (scaffolds established in M3):

```
packages/
├── rediai-contracts/  # Shared interfaces & types
├── rediai-core/       # Core ML training logic
├── rediai-wrapper/    # Integration & compatibility layer
├── rediai-data/       # Data layer & ETL
└── rediai-ui/         # Frontend (future)
```

**Current Status (M6):** 
- `rediai-contracts`: ✅ Real package with 17 extracted models, JSON Schema + TypeScript codegen
- Others: Scaffolds ready for extraction

**Hexagonal Architecture (M6):**
```
RediAI/
├── ports/         # Protocol interfaces (domain boundaries)
│   ├── auth.py    # AuthContextPort, JWTClaimsProtocol
│   ├── events.py  # EventPublisherPort
│   ├── persistence.py  # DatabaseSessionPort, WorkflowRepositoryPort
│   └── rbac.py    # RBACPort, RoleProtocol
├── adapters/      # Infrastructure implementations
│   ├── auth_fastapi.py
│   ├── events_websocket.py
│   ├── persistence_sqlalchemy.py
│   └── rbac_serving.py
└── composition/   # Dependency wiring (composition root)
    └── providers.py  # get_db_session, get_auth_context, etc.
```

**Layer Violations:** Reduced from 13 to 6 (54% reduction). See `docs/architecture/M05_LAYER_VIOLATIONS_ALLOWLIST.md`.

**M7 Updates:**
- Import-linter: Switched from `independence` to `layers` contracts (resolves ARCH-002)
- Security gate: Re-enabled enforcement (SEC-001 fixed)
- Integration tests: Added `tests/integration/test_composition_wiring.py` (13 tests)

See `docs/vision/V3_VISION.md` for complete architecture and migration strategy.

---

## Migrations

No new migrations in v3.0.0-baseline. All migrations from v2.1 are inherited:

- `001_initial` — Core tables
- `002_add_metadata_columns` — Metadata support
- `003_add_workflow_specs` — Workflow specifications
- `004_add_tenant_id_columns` — Multi-tenant support
- `005_add_audit_logs` — Audit logging
- `006_xai_and_research` — XAI capabilities
- `007_add_workflow_registry` — Workflow registry
- `008_expand_contract_example` — Expand/contract migration example

---

## Related Documents

- `rediai.md` — Original v2.1 documentation (comprehensive)
- `docs/v3refactor/V3_ROADMAP_r2.md` — **Canonical v3 roadmap (Phase XI → v3.0.0)**
- `docs/v3refactor/audit/phaseXIaudit.md` — Phase XI entry audit (plan vs reality)
- `docs/architecture/ARCHITECTURE_POLICY.md` — Canonical architecture policy
- `docs/v3refactor/audit/DeferredIssuesRegistry.md` — Active and resolved issues
- `docs/milestones/M0.md` — v2.1 freeze milestone
- `docs/milestones/M1.md` — Repository initialization milestone
- `docs/milestones/M2.md` — CI recovery + tooling hardening milestone
- `docs/v3refactor/` — v3 refactor planning documents

---

## Final Freeze Declaration — v3

As of tag v3.0.1-proprietary-license,
RediAI v3 is frozen.

No architectural, behavioral, CI, or enforcement changes may occur
without explicit phase re-opening.

Future work occurs at artifact boundaries (e.g., EZRA integration)
without modifying the v3 core substrate.
