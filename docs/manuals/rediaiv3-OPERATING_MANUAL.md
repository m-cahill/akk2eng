# RediAI v3 — Operating Manual

**Document Type:** Operating Manual, Mental Model, and Execution Guide
**Authority Level:** Canonical (subordinate only to `rediai-v3.md`)
**Audience:** AI agents (Cursor / GPT), senior engineers
**Status:** Living document — reflects current stabilized posture

---

## 1. Purpose & Identity

### 1.1 What RediAI v3 Is

RediAI is a **deterministic orchestration and certification system** for AI training workflows. It provides:

- A **DAG-based workflow engine** for composable, reproducible training pipelines
- An **XAI suite** (attribution, saliency, concept discovery, counterfactuals) integrated into the training loop
- A **game theory kernel** (CFR solver, Nash equilibrium computation, exploitability gates)
- A **multi-tenant infrastructure** with RBAC, audit trails, and tenant-scoped persistence
- A **certification layer** for validating external artifact bundles (EPB) without executing them
- A **contract-first API** where Pydantic models generate JSON Schema and TypeScript types

### 1.2 What RediAI v3 Is Not

| RediAI is NOT | Use instead |
|---|---|
| A general-purpose ML framework | PyTorch, TensorFlow |
| A hyperparameter tuning service | Optuna, Ray Tune |
| A model serving platform | TorchServe, TF Serving |
| A data engineering pipeline | Airflow, Prefect |
| An AutoML system | Auto-sklearn, NAS |
| A runtime for external systems like EZRA | EZRA runs independently; RediAI certifies its artifacts |

### 1.3 Role in the Ecosystem

RediAI sits at the **orchestration and certification boundary**:

- **Upstream:** Researchers and ML teams submit workflow specs and training configurations
- **Downstream:** Trained models, artifacts, and metrics are persisted, certified, and exportable
- **External boundary:** External runtimes (e.g., EZRA) produce artifacts; RediAI validates and certifies those artifacts without importing, building, or hosting the external runtime

RediAI acts as a **deterministic artifact certification layer** for AI systems and external runtimes.

### 1.4 Source of Truth Hierarchy

When documents conflict, precedence is:

1. `rediai-v3.md` — canonical system state
2. `ARCHITECTURE_POLICY.md` — architecture rules
3. Milestone artifacts — point-in-time truth
4. This document — operational synthesis

AI agents MUST defer to higher-authority sources.

---

## 2. Core Mental Model

### 2.1 System Abstraction

RediAI = Spec → Deterministic Execution → Certified Artifacts

```
Input (WorkflowSpec)
  → Execution (DAG engine + XAI hooks + game-theoretic gates)
    → Output (Artifacts + Events + CertificationVerdict)
```

Every interaction with RediAI follows this shape: a **declarative specification** enters the system, passes through **deterministic execution** with instrumented observability, and produces **versioned, auditable outputs**.

### 2.2 The 3 Loops

RediAI's behavior is compressed into three interlocking loops. These are introduced by this manual as a didactic model for AI agents. They are derived from, and consistent with, the actual system architecture and governance.

#### Execution Loop

```
WorkflowSpec → DAG scheduling → Node execution → Artifact storage → Event emission
```

The execution loop handles runtime behavior. A workflow specification (YAML/JSON) is parsed into a directed acyclic graph of nodes. Nodes execute sequentially or in parallel per the DAG. Each node produces artifacts (model checkpoints, evaluation metrics, LaTeX exports) stored in S3-compatible storage. Every state transition emits a domain event via the event bus (NATS/WebSocket).

#### Validation Loop

```
Schema validation → Gate evaluation → Contract checks → Certification verdict
```

The validation loop enforces correctness at every boundary. Workflow specs are validated against JSON Schema contracts. Runtime gates (exploitability thresholds, performance minimums, data quality checks) block progression if thresholds are not met. External artifact bundles are certified via deterministic schema + hash verification. Every validation result is recorded as an auditable event.

#### Governance Loop

```
CI pipeline → Architecture enforcement → Milestone proof pack → Audit → Release posture
```

The governance loop ensures the system itself remains trustworthy. CI enforces architecture boundaries (import-linter), contract integrity (codegen checks), and test thresholds (coverage gates). Every change is captured in a milestone lifecycle (plan → execution → summary → audit). Governance artifacts are machine-readable and immutable once closed. Release posture (tag + version) is gated on CI truthfulness.

### 2.3 AI-Native Insight

Three principles distinguish RediAI's architecture:

**Architecture-as-enforcement.** Architectural rules are not documentation — they are CI-enforced constraints. The 8-layer hexagonal model is codified in `pyproject.toml` import-linter contracts and verified by `tests/architecture/test_module_boundaries.py`. A layer violation fails the `module-boundaries` required check and blocks PR merge.

**CI as authority.** CI is the single arbiter of system health. There is no soft-fail. Required checks are blocking. `Green = safe` is a system invariant. Coverage thresholds are read from `pyproject.toml` (not hardcoded in workflows). Architecture, contracts, and tests run as first-class enforcement, not afterthought validation.

**Machine-readable governance.** Milestone artifacts (plan, summary, audit) follow templated structures. Deferred issues have IDs, exit criteria, and ownership. The architecture policy is versioned (SemVer) and has a digest test (`test_arch_policy_digest.py`) that fails if the policy structure changes without a corresponding test update.

### 2.4 System Boundary Diagram

```text
User / External System
        ↓
   (WorkflowSpec / EPB Bundle)
        ↓
┌─────────────────────────────┐
│        RediAI v3            │
│                             │
│  Execution Layer (DAG)       │
│  Validation Layer (Gates)    │
│  Governance Layer (CI)       │
│                             │
└─────────────────────────────┘
        ↓
Artifacts / Events / Verdict
```

---

## 3. Architecture Model

### 3.1 8-Layer Architecture

RediAI v3 implements an **8-layer hexagonal architecture**. The canonical source of truth for this model is `docs/architecture/ARCHITECTURE_POLICY.md` (v1.1.3).

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 8: composition         │ Dependency injection wiring  │
├─────────────────────────────────────────────────────────────┤
│ Layer 7: adapters            │ Infrastructure → Ports       │
├─────────────────────────────────────────────────────────────┤
│ Layer 6: api                 │ Presentation (HTTP/WS)       │
├─────────────────────────────────────────────────────────────┤
│ Layer 5: persistence,        │ Infrastructure               │
│          queue, storage      │                              │
├─────────────────────────────────────────────────────────────┤
│ Layer 4: registry, workflow  │ Domain (orchestration)       │
├─────────────────────────────────────────────────────────────┤
│ Layer 3: xai, models         │ Domain (independent)         │
├─────────────────────────────────────────────────────────────┤
│ Layer 2: ports               │ Protocol interfaces          │
├─────────────────────────────────────────────────────────────┤
│ Layer 1: core (foundation:   │ Foundation                   │
│ observability, certification, │                             │
│ utilities)                   │                              │
└─────────────────────────────────────────────────────────────┘

  Layer 0 (external): rediai_contracts — cross-boundary contracts (imports nothing)
```

**Dependency rule:** Higher layers MAY import from lower layers. Lower layers MUST NOT import from higher layers.

**Allowed dependency examples:**

| From | To | Allowed? |
|---|---|---|
| `registry` (L4) | `ports` (L2) | Yes — domain depends on port interfaces |
| `api` (L6) | `persistence` (L5) | Yes — presentation accesses infrastructure |
| `adapters` (L7) | `ports` (L2) | Yes — adapters implement port contracts |
| `composition` (L8) | `adapters` (L7) | Yes — composition root wires adapters |

**Forbidden dependency examples:**

| From | To | Why forbidden |
|---|---|---|
| `ports` (L2) | `api` (L6) | Foundation cannot depend on presentation |
| `models` (L3) | `workflow` (L4) | Independent domain cannot depend on orchestration |
| `persistence` (L5) | `composition` (L8) | Infrastructure cannot depend on wiring |

**Same-layer rule (Section 2.4 of ARCHITECTURE_POLICY.md):** Modules within the same layer MAY import from each other if the coupling is (1) unidirectional, (2) operationally necessary, and (3) explicitly documented. Example: `queue → persistence` (both Layer 5) is allowed; `persistence → queue` is forbidden.

**Cross-cutting concerns (permanent by design):**

| Pattern | Rationale |
|---|---|
| `RediAI.models.* → RediAI.xai.hooks` | XAI instrumentation (observability) |
| `RediAI.plugins.builtin → RediAI.queue.celery_adapter` | Plugin system (IoC) |
| `RediAI.workflow.* → RediAI.composition` | Hexagonal DI pattern (M6) |
| `RediAI.registry.* → RediAI.composition` | Hexagonal DI pattern (M6) |

**Operational surface note:** CLI is not part of the canonical architecture. It is an operational surface only. The `RediAI.cli` module is an outer consumer shell for the certification harness; it is registered in the import-linter config above the composition layer and is a thin interface that calls into the certification layer (Layer 1) only. If CLI is promoted to a canonical layer, `ARCHITECTURE_POLICY.md` must be updated first.

### 3.2 Package Decomposition

RediAI v3 uses a monorepo with extracted packages under `packages/`:

| Package | Purpose | Status | Dependency Rule |
|---|---|---|---|
| `rediai-contracts` | Shared interfaces, types, Pydantic models → JSON Schema → TypeScript | Production (3.0.0) | Imports **nothing** from RediAI or other packages |
| `rediai-core` | Foundation utilities: config, errors, types, tenants, telemetry | Alpha (0.1.0) | Imports `rediai-contracts` only |
| `rediai-data` | Data layer: ORM models, repositories, service interfaces | Alpha (0.1.0) | Imports `rediai-contracts` only |
| `rediai-ui` | Frontend scaffold (React + Vite) | Scaffold (3.0.0) | Imports `@rediai/contracts` via API only |
| `rediai-wrapper` | Integration & compatibility layer | Placeholder | Imports `rediai-core`, `rediai-contracts` |

**Contracts independence is CI-enforced:**

```toml
# pyproject.toml
[[tool.importlinter.contracts]]
name = "Contracts Independence"
type = "forbidden"
source_modules = ["rediai_contracts"]
forbidden_modules = ["RediAI"]
```

**Contract generation pipeline:**

```
Pydantic models (Python)
  → tools/generate_schema.py → JSON Schema (packages/rediai-contracts/dist/json_schema/)
  → npm run generate:types → TypeScript types (packages/rediai-contracts/dist/types/)
```

17 contract models are generated. CI (`contracts-gen.yml`) verifies generated files are up to date. Nondeterministic output (timestamps, UUIDs) was eliminated in M48.

### 3.3 Dependency Flow Rules

1. **Contracts are source of truth.** All cross-package and cross-boundary communication is defined in `rediai-contracts`. Contracts must not contain implementation code or external dependencies beyond typing.

2. **Core must remain pure.** `rediai-core` holds foundation utilities (config loading, error hierarchy, tenant primitives, telemetry types). It must not import from `RediAI.*`, `rediai-data`, or `rediai-wrapper`.

3. **No upward dependencies.** Within the main `RediAI` package, lower layers must not import from higher layers. This is enforced by the import-linter `Hexagonal Architecture Layers` contract, which is a required CI check.

4. **Domain independence at Layer 3.** Modules at Layer 3 (`xai`, `models`, `personality`, `game_theory`) must be independent of each other. They may only depend on Layers 1–2 (foundation, ports, contracts).

5. **Presentation boundary at Layer 6.** Domain and infrastructure layers must not import from `api.*`. The only exception is documented cross-cutting concerns (Section 4 of `ARCHITECTURE_POLICY.md`).

---

## 4. Capability Model

### 4.1 Workflow Engine

**What it does:** Executes DAG-based training pipelines. Nodes are scheduled by topological order. Each node execution is instrumented with OpenTelemetry spans. Artifacts are versioned and stored in S3-compatible storage.

**Where it lives:**

| Module | Role |
|---|---|
| `RediAI/workflow/engine.py` | DAG execution engine |
| `RediAI/workflow/nodes.py` | Node type definitions |
| `RediAI/workflow/xai_nodes.py` | XAI-instrumented workflow nodes |
| `RediAI/workflow/modulation_nodes.py` | FiLM/modulation workflow nodes |
| `RediAI/workflow/academic_nodes.py` | Academic export nodes (LaTeX, BibTeX) |
| `RediAI/workflow/rewardlab_nodes.py` | RewardLab decomposition/ablation nodes |

**What it produces:** `WorkflowResult` containing artifacts (model checkpoints, metrics, exports), status transitions, and OpenLineage events.

### 4.2 XAI System

**What it does:** Provides explainability instrumentation integrated into the training loop. Generates attribution maps, saliency visualizations, concept discovery results, and counterfactual explanations.

**Where it lives:**

| Module | Role |
|---|---|
| `RediAI/xai/attribution.py` | Saliency and attribution generators |
| `RediAI/xai/hooks.py` | Model forward-pass instrumentation hooks |
| `RediAI/xai/concepts.py` | Concept discovery |
| `RediAI/xai/goals.py` | Goal-conditioned explanations |
| `RediAI/xai/registry.py` | XAI method registry (plugin-based) |

**What it produces:** Attribution maps (NumPy arrays), saliency visualizations, concept clusters, counterfactual diffs. All outputs are deterministic given the same model + input + seed.

### 4.3 Game Theory Engine

**What it does:** Computes Nash equilibria via Counterfactual Regret Minimization (CFR). Provides exploitability metrics that serve as deployment gates. Supports reward shaping and strategic-level training parameters.

**Where it lives:**

| Module | Role |
|---|---|
| `RediAI/game_theory/cfr_solver.py` | CFR solver for Nash computation |
| `RediAI/game_theory/exploitability.py` | Exploitability metric computation |
| `RediAI/game_theory/nash_helpers.py` | Nash equilibrium utilities |
| `RediAI/game_theory/strategic_levels.py` | Strategic level definitions |
| `RediAI/modulation/reward_shapers/` | Nash, strategic, temporal, tag-bias reward shapers |

**What it produces:** Nash strategy profiles (probability distributions), exploitability scores (float, lower = closer to Nash), `GateResult` verdicts (pass/fail with remediation suggestions).

### 4.4 Registry System

**What it does:** Manages workflow lifecycle state: registration, versioning, status transitions, gate evaluation, RBAC enforcement, event streaming, and audit logging.

**Where it lives:**

| Module | Role |
|---|---|
| `RediAI/registry/models.py` | Domain models (Workflow, StepRun, Finding) |
| `RediAI/registry/gates.py` | Gate definitions and evaluation |
| `RediAI/registry/gate_evaluator.py` | GateEvaluator: register, evaluate, summary |
| `RediAI/registry/events.py` | Domain event publishing |
| `RediAI/registry/orm_models.py` | SQLAlchemy ORM models |
| `RediAI/registry/data_validator.py` | Data validation |
| `RediAI/registry/recorder.py` | Run recording and artifact tracking |

**What it produces:** Workflow state objects, gate evaluation results, audit log entries, event stream messages (NATS/WebSocket).

### 4.5 Certification / Publication

**What it does:** Validates external artifact bundles (EPB v1.0.0) for schema integrity and hash correctness. Emits deterministic `CertificationVerdict` objects. Provides both CLI and programmatic interfaces. No EZRA imports; no runtime execution of external code.

**Where it lives:**

| Module | Role |
|---|---|
| `RediAI/certification/epb_validator.py` | EPB validation harness (schema + hash) |
| `RediAI/certification/epb_hash.py` | Canonical hash computation |
| `RediAI/certification/canonical_json.py` | Deterministic JSON serialization |
| `RediAI/certification/verdict.py` | `CertificationVerdict` data class |
| `RediAI/certification/api.py` | Stable programmatic API: `certify_bundle(path)` |
| `RediAI/certification/epb/schema/` | Vendored EPB JSON schemas |
| `RediAI/cli/certify.py` | CLI: `rediai certify` / `rediai verify` |

**What it produces:** `CertificationVerdict` with fields: `certified`, `schema_valid`, `hash_valid`, `errors`. Output is deterministic (sorted keys, no timestamps, no UUIDs, sorted error lists).

**Programmatic API:**

```python
from RediAI.certification.api import certify_bundle

verdict = certify_bundle("/path/to/bundle.epb")
assert verdict.certified is True
```

**CLI:**

```bash
rediai certify bundle.epb              # JSON verdict to stdout
rediai certify bundle.epb --pretty     # Pretty-printed
rediai certify bundle.epb --output v.json  # Write to file
rediai verify bundle.epb               # Alias for certify
```

**Exit codes:** 0 = certified, 1 = schema invalid, 2 = hash mismatch / tamper, 3 = bundle format error.

Certification Guarantee:

Given the same artifact bundle, RediAI will always produce the same CertificationVerdict.

### 4.6 Multi-Tenant Infrastructure

**What it does:** Enforces tenant isolation at the ORM level. Every database table includes `tenant_id`. All queries are scoped by tenant context extracted from JWT claims. RBAC is enforced at the port layer. Audit logs are immutable and append-only.

**Where it lives:**

| Module | Role |
|---|---|
| `RediAI/api/serving/tenant_middleware.py` | Extracts tenant_id from JWT |
| `RediAI/ports/auth.py` | `AuthContextPort`, `JWTClaimsProtocol`, `ClaimsProviderPort` |
| `RediAI/ports/rbac.py` | `RBACPort` |
| `RediAI/adapters/auth_fastapi.py` | FastAPI auth adapter |
| `RediAI/adapters/rbac_serving.py` | Serving RBAC adapter |
| `RediAI/auditing/audit_logger.py` | Audit event publisher |
| `RediAI/persistence/models.py` | ORM base with `tenant_id` on all models |

**What it produces:** Tenant-scoped query results, RBAC authorization decisions, immutable audit log entries.

### 4.7 Extension / Optional Capability Surfaces

These capabilities extend the core system via the plugin architecture:

| Capability | Module | Plugin Entry Point | What It Does |
|---|---|---|---|
| **FiLM Modulation** | `RediAI/modulation/film_adapter.py` | `rediai.plugins.tournament:film` | Feature-wise linear modulation for context-conditioned networks |
| **Personality System** | `RediAI/personality/manager.py` | `rediai.plugins.personalities:aggressive` | Agent trait adaptation |
| **Tournament Scheduling** | `RediAI/tournament/scheduler.py` | `rediai.plugins.tournament:round_robin`, `swiss` | Round-robin, Swiss-system tournament scheduling |
| **Rating Systems** | `RediAI/tournament/rating_systems.py` | `rediai.plugins.tournament:elo_rating`, `colley_rating` | Elo and Colley rating computation |
| **Academic Export** | `RediAI/academic/exporter.py` | `rediai.workflow.nodes:academic.*` | Workflow metrics → LaTeX tables, figures, BibTeX |
| **ONNX Export** | `RediAI/export/onnx_exporter.py` | — | PyTorch model → ONNX format |
| **Plugin System** | `RediAI/plugins/registry.py` | — | Runtime plugin discovery and loading via entry points |

Plugins are registered via `pyproject.toml` `[project.entry-points]` and discovered at runtime.

---

## 5. Execution Guide

### 5.1 Minimal Usage

**Certify an external bundle (CLI):**

```bash
rediai certify /path/to/bundle.epb
```

**Certify an external bundle (programmatic):**

```python
from RediAI.certification.api import certify_bundle

verdict = certify_bundle("/path/to/bundle.epb")
if verdict.certified:
    print("Bundle is valid")
else:
    print(f"Certification failed: {verdict.errors}")
```

**Execute a workflow (internal API):**

```python
# Pseudocode — workflow execution via API
POST /api/workflows
{
    "spec": { "nodes": [...], "seed": 42 },
    "tenant_id": "acme-corp"
}
# → 202 Accepted { "workflow_id": "wf-abc-123" }
```

### 5.2 Workflow Lifecycle

A workflow progresses through a deterministic lifecycle:

```
Submission → Validation → Scheduling → Execution → Gate Evaluation → Completion
```

| Phase | Status | What Happens | Artifacts Produced |
|---|---|---|---|
| **Submission** | `pending` | Workflow spec received, JWT validated, tenant scoped | DB row created |
| **Validation** | `pending` | Spec validated against JSON Schema contracts | Validation errors (if any) |
| **Scheduling** | `pending` | DAG parsed, nodes topologically sorted, task enqueued | Celery task ID |
| **Execution** | `running` | Nodes execute in DAG order; each node is an OTel span | Model checkpoints, metrics, artifacts (S3) |
| **Gate Evaluation** | `running` | Gates (exploitability, performance, data quality) evaluated | `GateResult` verdicts |
| **Completion** | `completed` or `failed` | Final status set; events published | `WorkflowCompleted` / `WorkflowFailed` event |

### 5.3 Internal Flow

**DAG execution:** The workflow engine parses `WorkflowSpec` into a DAG. Nodes are executed in topological order. Each node execution is wrapped in an OpenTelemetry span with attributes (`workflow_id`, `node_id`, `status`).

**Event emission:** Every state transition publishes a domain event via `EventPublisherPort`. Events are routed through NATS (production) or WebSocket (real-time UI). Events include: `WorkflowStarted`, `NodeCompleted`, `GateEvaluated`, `WorkflowCompleted`, `WorkflowFailed`.

**Artifact storage:** Node outputs (model checkpoints, evaluation results, exports) are stored in S3-compatible storage with keys structured as `s3://bucket/{workflow_id}/{node_id}-{artifact_type}`. Artifacts are versioned by workflow execution; the same workflow spec + seed produces identical artifact hashes.

**Gate evaluation:** Gates are registered on a workflow via `GateEvaluator.register_gate()`. After relevant nodes complete, `evaluate_gates()` compares computed metrics against thresholds. Gate failure transitions the workflow to `failed` status with a `GateResult` containing the reason and remediation suggestions.

### 5.4 Example: End-to-End Workflow

1. POST /api/workflows
2. Workflow inserted into database (status=pending)
3. Worker (Celery) dequeues task
4. DAG executes:
   - train → evaluate → export
5. Artifacts written to S3
6. Gates evaluated:
   - exploitability threshold checked
7. Workflow marked completed or failed
8. Event emitted: WorkflowCompleted / WorkflowFailed

---

## 6. Governance Model

### 6.1 Architecture Enforcement

Architecture is enforced by three mechanisms that run as CI checks:

| Mechanism | Tool | Location | CI Status |
|---|---|---|---|
| **Layer ordering** | import-linter | `pyproject.toml` `[tool.importlinter]` | Required check (`module-boundaries`) |
| **Layer ordering + domain independence + no circular deps** | pytest | `tests/architecture/test_module_boundaries.py` | Required |
| **Policy digest** | pytest | `tests/architecture/test_arch_policy_digest.py` | Required (M33+) |
| **Contracts independence** | import-linter | `pyproject.toml` (Contracts Independence contract) | Required |
| **Interface contracts** | pytest | `tests/architecture/test_interface_contracts.py` | Required |

**Policy digest test:** `test_arch_policy_digest.py` contains canonical constants (`CANONICAL_LAYER_GRAPH`, `CANONICAL_CROSS_CUTTING_CONCERNS`, `CANONICAL_PERMANENT_EXCEPTIONS`, `CANONICAL_TEMPORARY_EXCEPTIONS`) that must match the state declared in `ARCHITECTURE_POLICY.md`. Changing the architecture policy without updating the digest test fails CI.

### 6.2 Milestone System

Every unit of work follows the milestone lifecycle:

```
Plan → Execution → Summary → Audit
```

| Artifact | Purpose | Example |
|---|---|---|
| `Mxx_plan.md` | Scope, constraints, acceptance criteria | `docs/v3refactor/Milestones/Phase19/M82/M82_plan.md` |
| `Mxx_run1.md` | Execution log (tool calls, decisions, evidence) | Tool call trace of implementation |
| `Mxx_summary.md` | Outcome, CI evidence, final state (merge SHA, tag) | CI run IDs, test counts, coverage |
| `Mxx_audit.md` | Score (x/5.0), guardrail compliance, post-merge actions | Guardrail table, compliance checklist |

**Milestones are immutable.** Once a milestone is closed and its summary/audit are merged, the artifacts are not modified. If corrections are needed, a new corrective milestone is created (e.g., M45 was a Phase XI corrective for ARCH-INFRA-006).

**Governance is machine-readable.** Milestone artifacts follow consistent templates. Scores are numeric (x/5.0). Guardrails are tables with pass/fail columns. CI evidence includes run IDs that can be independently verified.

**Phase lifecycle:** Milestones are grouped into phases. A phase has a charter, executes milestones sequentially, and closes with a formal closeout document. Phase closure is immutable.

### 6.3 Deferred Issues Registry

All deferred work is tracked in `docs/v3refactor/audit/DeferredIssuesRegistry.md`.

**Structure of each deferred issue:**

| Field | Purpose |
|---|---|
| **ID** | Unique identifier (e.g., `CI-008`, `COMP-001`) |
| **Issue** | Description of the problem |
| **Discovered** | Milestone where the issue was found |
| **Deferred To** | Target milestone or phase for resolution |
| **Reason** | Why it was deferred (not ignored) |
| **Blocker?** | Whether it blocks other work |
| **Exit Criteria** | Testable condition for resolution |

**Rules:**
- Any issue deferred more than 2 milestones must be escalated or re-justified
- Exit criteria must be testable (not "fix when convenient")
- Resolved issues remain in the registry with resolution evidence (never deleted)

**Current state:** ~21 active deferred issues (Pylint debt, MyPy strict, Bandit findings, compliance stubs, infrastructure specs). 100+ resolved issues with documented resolutions.

### 6.4 CI Truthfulness

CI in RediAI v3 follows a strict truthfulness doctrine:

| Principle | Meaning |
|---|---|
| **No soft-fail** | Required checks must not use `continue-on-error: true` for enforcement steps |
| **Required checks are blocking** | PR merge is blocked by failed required checks; no human override |
| **Green = safe** | If CI is green, the system is in a known-good state. No hidden skips, no muted failures |
| **Thresholds from config** | Coverage `fail_under` is read from `pyproject.toml` (currently `60`), not hardcoded in workflow YAML |
| **No threshold gaming** | Coverage measures behavior, not lines. Thresholds reflect actual measurement, not aspirational targets |

---

## 7. Testing Philosophy

### 7.1 3-Tier CI

| Tier | Workflow(s) | Purpose | Speed | Required? |
|---|---|---|---|---|
| **Smoke** | `ci-simple.yml` | Basic Python validity, import checks | ~2 min | Yes (required check) |
| **Quality** | `ci.yml`, `quality-gate.yml`, `coverage-gates.yml` | Unit smoke, EPB certification, coverage, linting, architecture, import-linter | ~8–15 min | `ci.yml` is required; quality-gate and coverage-gates are informational |
| **Nightly** | `nightly-full-coverage.yml`, `nightly-scorecard.yml` | Full integration, e2e, performance, load, metrics, scorecard | ~30 min | Report-only |

**What runs in each tier:**

- **Smoke:** `pytest -m unit_smoke` (minimal test subset), import collection, basic syntax
- **Quality:** Unit tests (`tests/unit/`), EPB certification tests (`tests/certification/`), CLI tests (`tests/cli/`), architecture tests (`tests/architecture/`), Black formatting, Flake8, import-linter, coverage measurement
- **Nightly:** Full integration tests, e2e scenarios, performance benchmarks, load tests, trace coverage, FiLM validation

### 7.2 What to Test

**Behavior over coverage.** Tests verify behavior ("submitting a workflow with an invalid spec returns 400") not implementation ("function X calls function Y"). Coverage is a measurement, not a goal.

**Contracts over implementation.** Port interfaces are tested via adapter contracts, not internal wiring. If an adapter satisfies the port protocol, it is correct regardless of internal structure.

**End-to-end validation.** Behavioral spike tests (`tests/behavioral_spike/`) verify complete flows: multi-tenant isolation, queue telemetry, workflow lifecycle. These are the highest-value tests.

**Gate evaluation tests.** Gate tests verify that thresholds produce deterministic pass/fail results. Gate logic is pure (no I/O), making tests fast and reliable.

**Certification tests.** EPB certification tests (`tests/certification/`) verify schema validation, tamper detection, and the "no EZRA imports" boundary. These are deterministic and run in CI quality tier.

---

## 8. Integration Model

### 8.1 Artifact Boundary Rule

RediAI integrates with external systems exclusively through **artifacts**. There is no runtime coupling, no shared process space, no imported execution logic.

| Integration Type | Allowed? | Example |
|---|---|---|
| Artifact validation | Yes | RediAI certifies an EPB bundle produced by an external system |
| Shared contracts (JSON Schema) | Yes | External system validates against `rediai-contracts` schemas |
| Runtime code import | No | RediAI must not import EZRA modules or any external runtime |
| Shared database | No | External systems do not access RediAI's database |
| Shared event bus | Boundary only | External systems may produce events that RediAI validates, not co-processes |

### 8.2 External Systems (EZRA Example)

EZRA is an external runtime / perception producer. The integration pattern is:

```
EZRA (external)            RediAI (certification boundary)
─────────────────          ──────────────────────────────
Produces EPB bundle   →    certify_bundle(path) → CertificationVerdict
                           Schema validation (vendored schemas)
                           Hash integrity check (canonical hash)
                           No EZRA imports, no EZRA execution
```

RediAI's role is limited to:
1. Validating the bundle conforms to EPB v1.0.0 schema
2. Verifying the embedded hash matches recomputed canonical hash
3. Emitting a deterministic `CertificationVerdict`

RediAI does **not** build, execute, host, or interpret EZRA's runtime. The EPB schemas are vendored in `RediAI/certification/epb/schema/`. CI enforces the no-import boundary via `tests/certification/test_no_ezra_import.py`.

---

## 9. System Invariants

The following invariants are compiled from the current stabilized posture. They are authoritative and canonical.

### Architecture Invariants

| Invariant | Enforcement | Evidence |
|---|---|---|
| Higher layers may import from lower layers; lower layers must not import from higher layers | import-linter `Hexagonal Architecture Layers` contract (required CI check) | `pyproject.toml` lines 379–411 |
| Domain modules at Layer 3 are independent of each other | `test_domain_independence` in `tests/architecture/test_module_boundaries.py` | Architecture test suite |
| No circular dependencies between modules | `test_no_circular_dependencies` in `tests/architecture/test_module_boundaries.py` | Architecture test suite |
| `rediai_contracts` imports nothing from `RediAI` | import-linter `Contracts Independence` contract (forbidden type) | `pyproject.toml` lines 455–463 |
| Same-layer dependencies are unidirectional and documented | `ARCHITECTURE_POLICY.md` Section 2.4; import-linter ignore_imports | Queue → Persistence only |
| Architecture policy changes require digest test update | `test_arch_policy_digest.py` (M33) | `tests/architecture/test_arch_policy_digest.py` |

### Contract Invariants

| Invariant | Enforcement | Evidence |
|---|---|---|
| Pydantic models are source of truth for all contracts | `tools/generate_schema.py` codegen pipeline | `packages/rediai-contracts/src/` |
| Generated JSON Schema and TypeScript must be in sync with Pydantic models | `contracts-gen.yml` CI workflow | `.github/workflows/contracts-gen.yml` |
| Contract codegen is deterministic (no timestamps, no UUIDs) | M48 fix: removed `${new Date().toISOString()}` from generator | Deterministic output verified by CI diff |
| Breaking contract changes fail CI | JSON Schema diff detection in contracts guardrails | `.github/workflows/contracts-guardrails.yml` |

### CI Truthfulness Invariants

| Invariant | Enforcement | Evidence |
|---|---|---|
| Required checks are blocking; no `continue-on-error` on enforcement steps | Manual governance + M75e enforcement hardening | CI-ENFORCE-001, CI-ENFORCE-002 resolved |
| Coverage `fail_under` is read from `pyproject.toml`, not hardcoded in workflows | `quality-gate.yml` reads from config | `pyproject.toml` line 290: `fail_under = 60` |
| Green CI = safe to merge | All required checks must pass for PR merge | Branch protection rules |
| No threshold gaming — coverage measures behavior, not lines | Coverage margin policy: 2% safety margin required | `rediai-v3.md` Coverage Margin Policy |
| Unit test tier (`tests/unit/`) is blocking | M75e: `continue-on-error` removed from unit test step | CI-ENFORCE-002 resolved |

### Determinism / Certification Invariants

| Invariant | Enforcement | Evidence |
|---|---|---|
| `CertificationVerdict` output is deterministic (sorted keys, no timestamps, no UUIDs) | `verdict.to_json()` uses `sort_keys=True`, `sorted(errors)` | `RediAI/certification/verdict.py` |
| Workflow execution with same spec + seed produces same artifacts | Deterministic RNG seeding | Reproducibility tests |
| EPB certification uses vendored schemas only (no external fetching) | Schemas in `RediAI/certification/epb/schema/` | Static files in repo |
| No EZRA imports in RediAI codebase | `tests/certification/test_no_ezra_import.py` | CI certification test suite |

### Governance Invariants

| Invariant | Enforcement | Evidence |
|---|---|---|
| Milestones are immutable once closed | Governance discipline; corrective milestones for fixes | M45 corrective (ARCH-INFRA-006) |
| Deferred issues have testable exit criteria | `DeferredIssuesRegistry.md` structure | All active issues have Exit Criteria column |
| Issues deferred >2 milestones must be escalated or re-justified | Registry rules | `DeferredIssuesRegistry.md` header rules |
| Phase closure is immutable | Closeout documents merged and finalized | Phase closure docs (e.g., `PHASE_XVII_CLOSEOUT.md`) |
| Every milestone produces plan + summary + audit artifacts | Milestone template | `docs/v3refactor/Milestones/PhaseN/Mxx/` |

### Integration Boundary Invariants

| Invariant | Enforcement | Evidence |
|---|---|---|
| No runtime coupling with external systems | Architecture tests + `test_no_ezra_import.py` | Certification test suite |
| Integration is artifact-only (no shared DB, no shared process) | Design principle; certification harness validates bundles, does not execute them | `RediAI/certification/api.py` calls `validate_epb()` only |
| Tenant isolation is enforced at ORM level | `tenant_id` on all tables; ORM query filters | `RediAI/persistence/models.py` |
| Audit logs are append-only (no UPDATE, no DELETE) | Immutable audit_logs table | `RediAI/auditing/audit_logger.py` |

---

## 10. Guardrails (Anti-Patterns)

The following actions are **forbidden**:

| Anti-Pattern | Why It's Forbidden | How It's Caught |
|---|---|---|
| **Importing from a higher layer** | Violates hexagonal architecture; creates upward dependency | import-linter required check; architecture tests |
| **Bypassing CI** | Undermines CI truthfulness invariant; "green = safe" becomes meaningless | Branch protection requires status checks |
| **Introducing hidden state** | Non-deterministic behavior breaks reproducibility and certification | Certification tests verify deterministic output |
| **Modifying contracts without versioning** | Breaks downstream consumers; silent API drift | `contracts-gen.yml` and `contracts-guardrails.yml` CI checks |
| **Adding `continue-on-error: true` to enforcement steps** | Converts blocking checks into soft-fail; CI greenwashing | Governance review; CI-ENFORCE-001/002 precedent |
| **Lowering coverage threshold without ADR** | Threshold regression without justification | Coverage Margin Policy in `rediai-v3.md` |
| **Importing EZRA or external runtime code** | Violates artifact boundary rule | `test_no_ezra_import.py` CI check |
| **Deleting or modifying closed milestone artifacts** | Milestones are immutable governance records | Governance discipline |
| **Adding deferred issues without exit criteria** | Creates untracked debt | `DeferredIssuesRegistry.md` structure requires Exit Criteria |
| **Committing non-deterministic output to contracts** | Timestamps/UUIDs in codegen cause false diffs | M48 fix; `contracts-gen.yml` determinism check |

---

## 11. AI Agent Execution Guide

### 11.1 If Modifying the System

Follow this sequence exactly:

**Step 1 — Identify the layer.**
Determine which architectural layer your change affects. Consult the 8-layer model in Section 3.1. If the change spans multiple layers, identify the primary layer and verify that all cross-layer imports follow the dependency rules (higher → lower only).

**Step 2 — Validate dependencies.**
Before writing code, verify that your imports comply with the layer ordering. Run:
```bash
lint-imports --config pyproject.toml
```
If you need to import from a module in a different layer, check that the dependency direction is downward. If it requires an upward dependency, you must introduce a port interface (Layer 2) and adapter (Layer 7) instead.

**Step 3 — Check contracts.**
If your change affects cross-boundary types (request/response shapes, domain models, event payloads), update the Pydantic models in `packages/rediai-contracts/` first. Then regenerate:
```bash
python tools/generate_schema.py
cd packages/rediai-contracts && npm run generate:types
```
Verify generated files are deterministic and diff-clean.

**Step 4 — Implement.**
Write the implementation following existing patterns in the target layer. Use port interfaces for infrastructure access. Use the composition root (`RediAI/composition/providers.py`) for dependency injection wiring.

**Step 5 — Test.**
Add tests appropriate to the change:
- **Unit tests** in `tests/unit/` for domain logic
- **Architecture tests** if adding new modules or changing boundaries
- **Certification tests** if modifying the certification layer
- **Integration tests** if changing cross-module flows
Mark tests with appropriate pytest markers (`@pytest.mark.unit`, `@pytest.mark.unit_smoke`, etc.).

**Step 6 — Run CI locally.**
```bash
# Smoke
pytest -m unit_smoke -x

# Architecture
pytest tests/architecture/ -v

# Import-linter
lint-imports --config pyproject.toml

# Coverage
pytest --cov=. --cov-report=term
```

**Step 7 — Produce milestone artifacts.**
If the change is part of a milestone, create the standard artifact set:
```
docs/v3refactor/Milestones/PhaseN/Mxx/
├── Mxx_plan.md
├── Mxx_run1.md
├── Mxx_summary.md
└── Mxx_audit.md
```
Follow the template structure from recent milestones (e.g., `docs/v3refactor/Milestones/Phase19/M82/`).

### 11.2 If Debugging

Follow this diagnostic sequence:

**Step 1 — Check CI.**
Read the CI run output. Identify which check failed. CI failures are meaningful — they point to the broken invariant.

**Step 2 — Check architecture violations.**
```bash
lint-imports --config pyproject.toml
pytest tests/architecture/ -v
```
If import-linter fails, the error output identifies the specific forbidden import chain. Fix the import direction or introduce a port/adapter.

**Step 3 — Check contracts.**
```bash
python tools/generate_schema.py
```
If generated schemas differ from committed versions, contracts have drifted. Regenerate and commit.

**Step 4 — Check deferred issues.**
Consult `docs/v3refactor/audit/DeferredIssuesRegistry.md`. The issue may be a known deferred item with documented context and exit criteria.

**Step 5 — Check test markers.**
If tests fail unexpectedly, verify they have correct markers:
- `@pytest.mark.unit` for unit tests
- `@pytest.mark.unit_smoke` for the required CI subset
- `@pytest.mark.integration` for tests requiring infrastructure
Tests marked `integration`, `e2e`, `load`, `real_nats`, or `real_db` are not expected to pass in standard CI (they require external services).

---

## 12. Failure Modes

Common failure classes:

| Failure | Cause | Detection |
|--------|------|----------|
| Architecture violation | Invalid import direction | import-linter CI failure |
| Contract drift | Schema mismatch | contracts-gen CI diff |
| Gate failure | Threshold not met | GateResult fail |
| Certification failure | Schema/hash invalid | certify_bundle errors |
| Tenant leak | Missing tenant scoping | behavioral spike tests |

All failures are deterministic and reproducible.

---

## Appendix A: Port Interface Reference

| Port | Module | Key Methods | Adapter(s) |
|---|---|---|---|
| `AuthContextPort` | `RediAI/ports/auth.py` | `__call__() → JWTClaimsProtocol` | `FastAPIAuthAdapter` |
| `ClaimsProviderPort` | `RediAI/ports/auth.py` | `get_claims(token) → JWTClaimsProtocol` | `FastAPIClaimsProvider` |
| `CurrentUserPort` | `RediAI/ports/auth.py` | `.user_id`, `.tenant_id`, `.is_authenticated`, `has_permission()` | FastAPI auth adapter |
| `DatabaseSessionPort` | `RediAI/ports/persistence.py` | `__call__() → AsyncGenerator[session]` | SQLAlchemy async session |
| `WorkflowRepositoryPort` | `RediAI/ports/persistence.py` | `get()`, `save()`, `delete()`, `list_all()`, `exists()` | SQLAlchemy repository |
| `EntityRepositoryPort[T]` | `RediAI/ports/persistence.py` | `get_by_id()`, `get_many()`, `create()`, `update()`, `delete()`, `count()` | SQLAlchemy generic repository |
| `UnitOfWorkPort` | `RediAI/ports/persistence.py` | `__aenter__()`, `__aexit__()`, `commit()`, `rollback()` | SQLAlchemy UoW |
| `EventPublisherPort` | `RediAI/ports/events.py` | `publish(event_type, payload)`, `publish_batch()` | WebSocket, NATS |
| `EventSubscriberPort` | `RediAI/ports/events.py` | `subscribe(event_types, handler)`, `unsubscribe()` | NATS subscriber |
| `WebSocketBroadcasterPort` | `RediAI/ports/events.py` | `broadcast(message)`, `send_to_connection()` | WebSocket manager |
| `RBACPort` | `RediAI/ports/rbac.py` | Role/permission checking | Serving RBAC adapter |
| `TelemetryPort` | `RediAI/ports/telemetry.py` | `start_span(name, attrs) → ContextManager[SpanContext]`, `get_current_span()` | OpenTelemetry adapter, NoOp adapter |
| `MessageQueuePort` | `RediAI/ports/message_queue.py` | `.is_available`, `publish(subject, payload)` | NATS adapter, `NoOpMessageQueueAdapter` |
| `AuditPublisherPort` | `RediAI/ports/audit_publisher.py` | Audit event emission | Postgres audit publisher |
| `DataPort` | `RediAI/ports/data.py` | Data access interface | Data layer adapter |

## Appendix B: CI Workflow Map

| Workflow | File | Tier | Trigger | Required Check? |
|---|---|---|---|---|
| CI Simple | `ci-simple.yml` | Smoke | Push/PR | Yes |
| CI | `ci.yml` | Quality | Push/PR | Yes |
| Quality Gate | `quality-gate.yml` | Quality | Push/PR | Informational |
| Coverage Gates | `coverage-gates.yml` | Quality | Push/PR | Informational |
| Module Boundaries | `dependency-graphs.yml` | Quality | Push/PR | Yes |
| Contracts Generation | `contracts-gen.yml` | Quality | Contract changes | Informational |
| Contracts Guardrails | `contracts-guardrails.yml` | Quality | Contract changes | Informational |
| Nightly Full Coverage | `nightly-full-coverage.yml` | Nightly | Schedule | No |
| Nightly Scorecard | `nightly-scorecard.yml` | Nightly | Schedule | No |
| Security Scan | `security-scan.yml` | Quality | Push/PR | Informational |
| Release | `release.yml` | Release | Tag push | N/A |
| Frontend CI | `frontend-ci.yml` | Quality | Frontend changes | Informational |
| Trace Coverage | `trace-coverage.yml` | Quality | Push/PR | Informational |

## Appendix C: Active Deferred Issues (Snapshot)

Current active deferred issues as of stabilization. Consult `docs/v3refactor/audit/DeferredIssuesRegistry.md` for full details.

| ID | Issue | Impact | Blocker? |
|---|---|---|---|
| CI-005 | Keycloak integration test flakiness | Low | No |
| CI-008 | Pylint debt (score 8.05/10) | Low | No |
| CI-009 | MyPy strict violations | Low | No |
| CI-010 | Bandit security findings | Low | No |
| CI-011 | Safety dependency findings | Low | No |
| CI-012 | Pydocstyle debt | Low | No |
| CI-013 | Radon complexity thresholds | Low | No |
| CI-022 | FiLM test Windows DLL failures | Low | No |
| CI-SIGNAL-001 | Unit Smoke replaces Unit Tests (3.11) | Governance | No |
| COV-001 | Plugins coverage low (31.7%) | Low | No |
| COMP-001 | Compliance scripts are stubs (GDPR/HIPAA) | Medium | No |
| INFRA-001 | Codecov token not configured | Low | No |
| INFRA-002 | GHAS not enabled for SARIF | Low | No |
| INFRA-SPEC-001–007 | K8s/container security specs skipped | Low | No |

None of these are blockers. All have documented exit criteria in the registry.

## Appendix D: Documentation Authority Hierarchy

| Level | Document | Role |
|---|---|---|
| **Level 0** | Git tags (`v3.0.0-operational-lock`, etc.) | Immutable release markers |
| **Level 1** | `rediai-v3.md` | Canonical project state |
| **Level 2** | Phase closeout documents | Phase lifecycle records |
| **Level 3** | `docs/architecture/ARCHITECTURE_POLICY.md` | Architecture rules |
| **Level 4** | `docs/v3refactor/Milestones/...` | Milestone artifacts |
| **Level 5** | `README.md` | Entry point |
| **Operational** | `docs/OPERATING_MANUAL.md` (this document) | System manual and execution guide |

This document is subordinate to `rediai-v3.md` and `ARCHITECTURE_POLICY.md`. It synthesizes and compresses existing authoritative sources into a single operational reference. Where this document and a higher-authority source conflict, the higher-authority source governs.
