# Foundry Master Document
## Unified Context, Mental Model, and Operating Guide for Cursor or ChatGPT

**Purpose:** This document is a single, self-contained handoff for an agent that needs to understand what Foundry is, what exists today, how it was built, what constraints must not be violated, and how to extend it safely.

**Audience:** Cursor, ChatGPT, or any engineer/agent taking over design, refactoring, implementation, verification, or extension work inside the project.

**Scope:** This document focuses on the committed `foundry/` subtree and the runtime/architecture that emerges from it. It intentionally avoids showing non-committed or study-surface repository structure in the structure section.

**Working posture:** Treat this as a practical operating manual, not a marketing document.

---

## 1. Executive Summary

Foundry is an architectural research and engineering program that extracts recurring patterns from major distributed systems and implements them as **minimal, composable primitives**. The project is built around a clean-room rule: upstream systems are used to understand architecture, execution pipelines, and subsystem boundaries, but not as code sources.

The central thesis is:

> Complex distributed systems can be constructed by composing a small, stable set of primitives instead of repeatedly reimplementing large amounts of tightly coupled infrastructure.

Foundry has already moved beyond theory. It now includes:

- a **primitive kernel**
- a **system synthesis harness**
- **canonical platform wrappers**
- **composition validation**
- **runtime enforcement**
- **observability**
- **determinism and replay**
- **system instantiation and orchestration**

The current state of Foundry is best understood as an **in-process runtime substrate**: primitives compose into systems, systems become first-class runtime entities, and systems-of-systems can coordinate through allowed surfaces without direct coupling.

---

## 2. What Foundry Is

Foundry is all of the following at once:

1. **A primitive extraction program**  
   It studies mature systems to identify recurring architectural patterns.

2. **A clean-room implementation effort**  
   It turns validated patterns into implementation-agnostic primitives without copying upstream code.

3. **A composition framework**  
   It assembles primitives into larger systems such as controller platforms, DAG runtimes, and workflow engines.

4. **A runtime substrate**  
   It supports instantiation, configuration, orchestration, observation, replay, and control of synthesized systems.

5. **An audit-first engineering program**  
   It is designed to preserve behavior, maintain evidence, and support milestone-based verification.

---

## 3. What Foundry Is Not

Foundry is **not**:

- a copy of Kubernetes, Temporal, Kafka, Ray, or any other upstream system
- a wrapper around upstream code
- a greenfield framework driven by novelty over discipline
- a distributed cluster runtime today
- a persisted multi-process platform today
- a DSL-first system today
- a typed-contract or schema-first runtime today

At the current stage, Foundry is an **in-process, deterministic, composable kernel and runtime substrate** with explicit limitations documented later in this guide.

---

## 4. The Core Thesis

Modern distributed systems repeatedly converge on similar architectural patterns because they solve the same coordination problems.

Examples:

- Kubernetes converges on reconciliation control loops
- Temporal converges on durable workflow execution
- Bazel converges on dependency graph execution
- Ray converges on distributed task scheduling and DAG execution
- etcd converges on consensus-backed state and watch
- Kafka converges on partitioned append-only streams
- Raft converges on replicated log consensus

Foundry exists to turn those recurring patterns into a **small, stable, reusable architecture substrate**.

The project assumes:

- architecture matters more than implementation detail
- recurring patterns matter more than system-specific features
- composability is more valuable than monolithic completeness
- primitive isolation is more important than convenience coupling

---

## 5. Non-Negotiable Rules

### 5.1 Clean-Room Rule

Upstream systems are **study surfaces**, not implementation sources.

Allowed:
- reading architecture
- tracing execution pipelines
- studying subsystem boundaries
- validating patterns across systems

Not allowed:
- copying source code
- porting implementation directly
- reproducing upstream details without architectural necessity

**Short form:** capture the idea, never the code.

### 5.2 Architecture Over Implementation

The project is about **architectural concepts** first. Implementation exists to validate the architecture, not the other way around.

### 5.3 Cross-System Validation

A pattern should appear in multiple independent systems before it is elevated into a Foundry primitive. Single-system artifacts should be treated as system-specific until proven otherwise.

### 5.4 Minimality

Primitives should represent the smallest useful abstraction. Large subsystems should be decomposed into smaller architectural units whenever possible.

### 5.5 Composability

Primitives must be usable as building blocks. A primitive that cannot compose cleanly with others is suspect.

### 5.6 Behavior Preservation by Default

When changing existing code, preserve behavior unless a change is explicitly justified, documented, and verified.

### 5.7 Evidence Over Narration

Milestones should end with proof:
- tests
- CI
- artifact evidence
- audits
- summaries
- explicit closeout records

---

## 6. Primitive Extraction Method

Foundry’s extraction workflow is conceptually simple and should remain stable.

### Step 1 — Analyze System Architecture
Identify the major subsystems:
- where state lives
- what drives execution
- how components communicate
- where control and data boundaries lie

### Step 2 — Trace Execution Pipelines
Follow the runtime path that actually does work. Hidden primitives often appear only when the execution path is made explicit.

Examples:
- request → log append → replication → visibility
- desired state → watch → reconcile → schedule
- DAG submission → dependency resolution → execution

### Step 3 — Identify Clean Boundaries
Look for subsystem seams that could support a generic interface.

### Step 4 — Recognize the Pattern
Ask:
- does this solve a general infrastructure problem?
- does it appear elsewhere?
- does it have stable inputs, outputs, and lifecycle?

### Step 5 — Model the Primitive
Define the minimal interface and operational role.

### Step 6 — Integrate into Taxonomy
Place the primitive in the correct domain.

### Anti-Patterns
Do **not** extract:
- pure implementation artifacts
- system-specific configuration formats
- UI logic
- deployment scripts
- one-off features that do not generalize

---

## 7. Primitive Taxonomy

Foundry’s taxonomy is locked around **8 domains**.

### Core Domains

- **events** — asynchronous communication
- **stream** — ordered append-only logs
- **state** — persistent state and state machines
- **consensus** — distributed agreement

### Control Domains

- **scheduler** — task placement and resource-aware assignment
- **workflow** — durable multi-step process execution
- **graph** — dependency-driven execution
- **reconcile** — desired-state convergence

### Domain Boundaries

Use these rules when deciding where something belongs:

- If messages are fire-and-forget, it belongs in **events**
- If records are ordered, addressable, and replayable, it belongs in **stream**
- If the concern is persistence and deterministic transitions, it belongs in **state**
- If the concern is multi-node agreement, it belongs in **consensus**
- If the concern is where work runs, it belongs in **scheduler**
- If the concern is long-running process progression, it belongs in **workflow**
- If execution order is dependency-driven, it belongs in **graph**
- If a loop continuously drives actual state toward desired state, it belongs in **reconcile**

### Canonical Compositions

- **Event platform**  
  `events → stream → state`

- **Distributed database**  
  `events → consensus → state`

- **Cloud control plane**  
  `state → reconcile → scheduler`

- **Build or DAG executor**  
  `graph → scheduler`

- **Durable workflow platform**  
  `events → workflow → state`

---

## 8. Source Systems and What They Contribute

Foundry’s architectural research draws from major production systems. Treat them as pattern sources, not implementation targets.

| Source System | Main Architectural Signals for Foundry |
|---|---|
| Kubernetes | reconciliation loops, watch/state-cache patterns, scheduler framework, object/state patterns |
| Envoy | runtime substrate ideas, filter-chain pipeline model, dynamic config distribution, dispatcher/thread-local concepts |
| etcd | MVCC state, watch semantics, lease model, coordination-backed state |
| Temporal | durable workflow execution, task queues, replay and event-history ideas |
| Bazel | DAG/incremental graph execution, interpreter boundaries, dependency evaluation |
| PostgreSQL | WAL/page formats, buffer manager ideas, execution model patterns |
| RocksDB | storage engine primitives, caching, WAL/log-structured storage concepts |
| Ray | scheduling, DAG execution, backpressure, task runtime concepts |
| Kafka | append-only logs, partitioned stream model, coordinator patterns |
| Raft | replicated log consensus, leader election, quorum-driven commitment |

### Practical Reading Rule

When extending Foundry:
- borrow architecture
- borrow invariants
- borrow boundary logic
- never borrow code

---

## 9. Phase-by-Phase Evolution

This section is the shortest reliable way to understand the project’s evolution.

### Phase I — Foundations
Established:
- project vision
- clean-room rule
- primitive extraction philosophy
- milestone governance

### Phase II — Taxonomy and System Analysis
Established:
- primitive taxonomy
- domain boundaries
- cross-system analysis of 10 target systems
- composition patterns

### Phase III — Primitive Modeling
Established:
- interfaces
- contracts
- consistency model
- operational semantics
- execution model

### Phase IV — Primitive Kernel
Implemented the kernel and validated basic composition.

Implemented primitives:
- `event_bus`
- `append_only_log`
- `versioned_state_store`
- `reconciliation_loop`
- `task_scheduler`
- `task_executor`
- `workflow_runtime`
- `graph_executor`

### Phase V — System Synthesis
Added:
- synthesis harness
- canonical systems
- runtime host
- canonical platform wrappers

Canonical systems:
- `ControllerPlatform`
- `DagRuntimePlatform`
- `WorkflowEnginePlatform`

### Phase VI — Composition Validation
Validated:
- additional blueprints
- systems-of-systems
- cross-system coordination via shared primitives
- composition generality without primitive modification

### Phase VII — Runtime and Operational Hardening
Added:
- boundary enforcement
- observability
- determinism and replay
- failure semantics
- scheduling policies
- stress validation

### Phase VIII — System Instantiation and Orchestration
Added:
- `SystemInstance`
- `SystemCatalog`
- configuration layer
- `SystemAPI`
- `SystemGraph`
- `SystemOrchestrator`

At this point, systems are first-class runtime entities.

### Phase IX — Interface and Usability Layer
Added:
- `SystemDefinition` and inspection helpers
- typed contracts (`contracts.py`, `validation.py`, `ContractValidationError`)
- declarative system definition DSL (`dsl.py`, `compiler.py`)
- visualization and introspection layer (`visualization.py`)

### Phase X — Proof of Value
Validated Foundry through a real-world refactor:
- captured a baseline trading pipeline (`baseline_system/`)
- mapped stages to primitives
- rebuilt it using Foundry primitives (`refactored_system/`) with identical behavior
- published quantified proof of value and a case study (`case_study/`)

### Phase XI — Audit Closure and Enterprise Hardening
Elevated CI/CD and supply-chain posture:
- coverage enforcement (≥ 87%, blocking on Python 3.11)
- Ruff lint + format (blocking)
- hashed dependency pins (`pip-compile`)
- supply-chain scanners: Gitleaks, pip-audit (strict), Bandit (HIGH), CycloneDX SBOM
- GitHub Actions pinned to full commit SHAs
- release packaging: version **1.0.0**, wheel + sdist built in CI, `CHANGELOG.md`, `CONTRIBUTING.md`
- artifact-level provenance target (`dist/*.whl`, non-blocking where GitHub attestations are unavailable)
- git tag **`v1.0.0`** on `main`

---

## 10. The Primitive Kernel (What Exists Today)

The current implemented kernel consists of **8 primitives across 7 implemented domains**.

| Primitive | Domain | Responsibility |
|---|---|---|
| `event_bus` | events | asynchronous event routing |
| `append_only_log` | stream | ordered append-only event history |
| `versioned_state_store` | state | MVCC-style versioned key/value state |
| `reconciliation_loop` | reconcile | declarative state convergence |
| `task_scheduler` | scheduler | FIFO scheduling substrate |
| `task_executor` | workflow | task execution substrate |
| `workflow_runtime` | workflow | durable multi-step execution model |
| `graph_executor` | graph | DAG dependency execution |

### Important Clarification
The taxonomy contains a **consensus** domain, but a consensus primitive is **not yet implemented** in the current kernel. Consensus remains conceptually modeled and architecturally grounded, but implementation has been intentionally deferred.

---

## 11. Kernel Invariants

These invariants must be treated as binding unless explicitly changed through a well-scoped and well-verified milestone.

### 11.1 Scheduler Invariant
The scheduler is **dependency-agnostic**.

That means:
- it does not interpret graph structure
- it does not understand workflow semantics
- it does not own reconciliation logic

Dependency and orchestration logic belong to:
- `graph_executor`
- `workflow_runtime`
- `reconciliation_loop`

### 11.2 Executor Invariant
The executor is **orchestration-agnostic**.

That means:
- it executes work
- it does not understand graphs
- it does not understand workflows
- it does not own scheduling policy beyond what is explicitly passed to it

### 11.3 Primitive Isolation
Each primitive should have a single responsibility and should not reach into another primitive’s internal responsibilities.

### 11.4 Explicit Wiring
Composition must happen through explicit wiring, not hidden shared state.

### 11.5 Additive Runtime Layers
Later runtime layers should wrap or coordinate primitives without altering primitive behavior unless explicitly intended and verified.

---

## 12. System Synthesis Model

Foundry’s system model is:

> primitives → synthesis harness → assembled systems → runtime host

### Canonical Architectures

#### Event-Driven Control Plane
```text
state → reconcile → scheduler → executor
```

#### DAG Execution Engine
```text
graph → scheduler → executor
```

#### Durable Workflow Engine
```text
workflow → scheduler → executor
```

### Canonical Platform Wrappers

The project defines three canonical synthesized systems:

- `ControllerPlatform`
- `DagRuntimePlatform`
- `WorkflowEnginePlatform`

These are not new primitives. They are system-level compositions of the kernel.

### Synthesis Principle

A system should be created by **wiring existing primitives together**. If a desired system can be expressed through existing primitives, do that first. Do not create a new primitive when composition is enough.

---

## 13. Composition Validation Model

Phase VI validated that the kernel is general enough to produce multiple distinct compositions.

### Example blueprints
- `event_pipeline`
- `event_platform`
- `state_convergence_system`
- `stream_processing_pipeline`
- `control_plane_system`
- `graph_workflow_system`
- `cross_system_coordinator`

### Meaning of This Phase
Phase VI proved that:
- multiple systems can emerge from the same primitive kernel
- no primitive changes are required to validate new compositions
- systems can coordinate through allowed shared surfaces
- multiple execution models can coexist on shared substrate

### Key Interpretation
Foundry is not just a single architecture. It is a **small architecture substrate** that can synthesize multiple higher-level systems.

---

## 14. Boundary Enforcement Model

Foundry explicitly prevents certain kinds of coupling.

### Allowed Coordination Surfaces
Cross-system coordination must flow through:
- `event_bus`
- `versioned_state_store`

### Allowed Shared Substrate
Shared execution substrate inside composed systems may include:
- `task_scheduler`
- `task_executor`

### Forbidden Behavior
Do **not** introduce:
- direct object references across system-role primitives
- direct method calls between system-role primitives
- hidden bypass paths around allowed surfaces

System-role primitives include:
- `reconciliation_loop`
- `append_only_log`
- `graph_executor`
- `workflow_runtime`

### Enforcement Scope
Boundary validation is performed during composition validation, not as an ad hoc coding convention.

### Operational Meaning
If you need one system to influence another:
- publish an event
- write state
- route through orchestrated, validated surfaces

Do **not** simply call into another system directly because it is convenient.

---

## 15. Observability, Determinism, and Replay

These layers are part of the runtime model, not optional extras.

### Observability
Foundry supports per-system trace capture.

Representative trace event types include:
- `EVENT_PUBLISHED`
- `TASK_SCHEDULED`
- `TASK_EXECUTED`
- `WORKFLOW_STEP`
- `GRAPH_NODE_EXECUTED`
- `STATE_UPDATED`

Important properties:
- per-system collector
- ordered sequence numbers
- no required global singleton
- instrumentation attached without changing primitive behavior

### Determinism
Foundry treats deterministic execution as a first-class goal.

Practical interpretation:
- same inputs should produce the same trace shape
- replay should validate that runtime behavior is reproducible
- deterministic surfaces matter more than incidental runtime timing

### Replay
Foundry uses causal replay:
- root events are republished
- downstream behavior is validated against trace expectations
- payloads can be preserved for reconstruction

### Why This Matters
These features are not “nice to have.” They are what make the architecture provable, testable, and auditable under change.

---

## 16. Failure Semantics

Foundry defines deterministic failure handling rather than allowing failure to remain an informal side effect.

### Intended properties
- explicit
- traceable
- replayable
- deterministic

Representative failure types include:
- task failures
- workflow failures
- graph failures
- scheduling failures
- state conflicts
- timeouts

### Engineering rule
When extending runtime behavior, do not introduce silent or ambiguous failure paths. Failures should be normalized, surfaced, and captured in traceable form.

---

## 17. Scheduling Policy Model

The scheduler supports policy as a runtime concern while preserving its fundamental invariant.

Representative policy types include:
- **FIFO** — preserves baseline behavior
- **Quota** — deterministic submission limiting
- **Priority** — deterministic priority ordering
- **QueueSize** — bounded queue rejection with explicit failure

### Constraint
Adding policy must not turn the scheduler into a graph engine or workflow engine. Policy shapes queue behavior; it does not absorb higher-level orchestration responsibilities.

---

## 18. Runtime Substrate (Current End-State)

The most important mental model for the current project state is the full runtime substrate stack:

```text
primitive kernel
    ↓
synthesis harness
    ↓
SystemInstance
    ↓
Configuration Layer
    ↓
System API
    ↓
System Graph
    ↓
SystemOrchestrator
    ↓
SystemCatalog
    ↓
runtime host
```

### Layer Responsibilities

#### Primitive Kernel
Implements the core building blocks.

#### Synthesis Harness
Instantiates systems from blueprints.

#### SystemInstance
Wraps an assembled system and gives it first-class runtime identity:
- `system_id`
- `blueprint_id`
- `metadata`

#### Configuration Layer
Validates and normalizes system configuration before builders consume it.

#### System API
Provides typed control surfaces such as:
- get
- invoke
- inspect

#### System Graph
Represents system-to-system relationships as edges:
- `(source_system_id, event_type, target_system_id)`

#### SystemOrchestrator
Wires allowed event-driven interactions between systems.

#### SystemCatalog
Registers, retrieves, and lists instantiated systems.

#### Runtime Host
Owns lifecycle and serves as the control plane for instantiated systems.

---

## 19. System-of-Systems Orchestration

Foundry now supports coordinated systems-of-systems while preserving no-coupling rules.

### Core rule
Systems do **not** hold direct references to each other for coordination.

### Coordination flow
Coordination proceeds through:
- event publication
- validated orchestration wiring
- host-mediated invocation

### Example mental model
A controller system can publish an event such as `controller.reconciled`, which the orchestrator routes to a target runtime through the `SystemAPI`, rather than by direct method call.

### Invariants preserved by orchestration
- no direct coupling
- determinism preserved
- replay remains valid
- primitive isolation preserved
- runtime layers remain additive

---

## 20. Current Capabilities

As of the current architecture, Foundry can credibly do the following:

### Primitive Level
- provide a minimal kernel of reusable infrastructure primitives
- validate composition without primitive mutation
- preserve core invariants through system assembly

### System Level
- synthesize canonical controller, DAG, and workflow systems
- run multiple synthesized systems in one runtime host
- validate systems-of-systems compositions

### Runtime Level
- instantiate systems as first-class runtime entities
- catalog them
- configure them
- inspect and invoke them
- route orchestration through validated event-driven paths

### Operational Level
- trace execution
- validate deterministic replay
- surface failures explicitly
- apply scheduling policies
- stress test runtime behavior

### Release and Packaging Level
- version **1.0.0** in `pyproject.toml`
- CI-built wheel and sdist (GitHub Actions artifact)
- artifact-level provenance target (non-blocking where attestations are unavailable)
- `CHANGELOG.md` and `CONTRIBUTING.md` in the repository
- git tag **`v1.0.0`** on `main`

---

## 21. Known Limitations

These limitations are explicit and should be preserved in any honest description of the current project state.

### 21.1 No Distributed Orchestration Yet
Everything runs in a single process today.

### 21.2 No Durable Cross-Process Persistence Yet
State is in-memory at runtime; restart persistence is not the current operating model.

### 21.3 No External Interface Layer Yet
There is no mature DSL, schema-rich interface layer, or external control surface intended as the final user-facing model.

### 21.4 Event Contracts Are Still Lightweight
Event types and payloads are not yet represented as a formal typed contract system.

### 21.5 Consensus Is Deferred
Consensus is part of the taxonomy but not yet implemented as a primitive in the active kernel.

### 21.6 No PyPI Distribution Yet
The project produces CI artifacts and a git tag (`v1.0.0`) but has not been published to PyPI or TestPyPI. Distribution is currently installation from source or the CI-built wheel.

### 21.7 Foundry Is a Substrate, Not a Complete Product
It is designed to enable systems, not to masquerade as a finished infrastructure platform in every respect.

---

## 22. How to Work on Foundry Safely

This is the operational guidance section for Cursor or any other implementation agent.

### 22.1 Start by Classifying the Task
Every change should first be categorized as one of:

1. **Primitive work**
2. **System synthesis work**
3. **Composition validation work**
4. **Runtime layer work**
5. **Documentation / audit / evidence work**

Do not treat these as interchangeable.

### 22.2 When to Add a Primitive
Add a new primitive only when:
- the concept is architectural, not incidental
- it appears across multiple systems
- it cannot be represented by existing primitives plus composition
- its interface can remain minimal and stable

### 22.3 When to Add a System
Add a new system when:
- existing primitives can already express it
- the change is primarily wiring
- no primitive behavior change is needed

### 22.4 When to Add a Runtime Layer
Add a runtime layer when:
- you need control, orchestration, inspection, or validation around systems
- you can preserve primitive behavior
- the new behavior is additive

### 22.5 Preserve These Invariants
Never casually break:
- scheduler dependency-agnostic posture
- executor orchestration-agnostic posture
- primitive isolation
- no-coupling boundary rules
- deterministic replay assumptions

### 22.6 Prefer Small, Verifiable Changes
Changes should be:
- narrow in scope
- reversible
- supported by tests
- supported by evidence
- documented in milestone artifacts if they are meaningful enough

---

## 23. How to Evaluate New Work

Before accepting a change, ask:

### Primitive Questions
- Is this truly a primitive?
- Is it architectural?
- Is it minimal?
- Is it composable?
- Is there cross-system evidence?

### System Questions
- Could this be done by synthesis instead of new primitive logic?
- Does it preserve primitive isolation?
- Does it keep coupling explicit?

### Runtime Questions
- Is the layer additive?
- Does it preserve determinism?
- Does it preserve replayability?
- Does it respect allowed surfaces?

### Refactoring Questions
- Does behavior stay the same by default?
- Is there evidence?
- Is there a rollback path?
- Does this increase auditability?

---

## 24. Repository Structure (Committed Subtree Only)

Only the committed `foundry/` subtree is shown here.

```text
foundry/
├── primitives/
│   ├── events/
│   ├── stream/
│   ├── state/
│   ├── consensus/
│   ├── scheduler/
│   ├── workflow/
│   ├── graph/
│   └── reconcile/
├── synthesis/
├── systems/
├── composition/
├── runtime/
├── observability/
├── baseline_system/
├── refactored_system/
├── case_study/
├── research/
├── examples/
├── tests/
├── CHANGELOG.md
├── CONTRIBUTING.md
├── MANIFEST.in
└── pyproject.toml
```

### How to read this structure

- **primitives/**  
  The kernel. This is the architectural core.

- **synthesis/**  
  Blueprint-driven assembly of systems from primitives.

- **systems/**  
  Canonical platform wrappers and runtime host surfaces.

- **composition/**  
  Validation harnesses and experimental composition logic.

- **runtime/**  
  Instantiation, catalog, API, graph, orchestrator, and related runtime substrate layers.

- **observability/**  
  Trace capture and instrumentation helpers.

- **baseline_system/**  
  Pre-Foundry trading pipeline used as the Phase X refactoring source.

- **refactored_system/**  
  Foundry-primitive rebuild of `baseline_system/` with identical behavior (Phase X proof of value).

- **case_study/**  
  Quantified comparison and published case study of the refactor.

- **research/**  
  Refactor baseline analyses (value scorecard, testability, mapping).

- **examples/**  
  Demonstrations of canonical and composed architectures.

- **tests/**  
  Verification across primitives, systems, composition, runtime, replay, failure semantics, and stress behavior.

---

## 25. Practical Operating Instructions for Cursor or ChatGPT

If you are taking over work in Foundry, operate with the following defaults.

### First, orient yourself
Understand:
- which phase introduced the behavior you are touching
- whether the behavior belongs to a primitive, a system, or a runtime layer
- what invariants apply

### Second, preserve architecture boundaries
Do not shortcut through direct calls between higher-level systems. Use the approved surfaces.

### Third, prefer synthesis over invention
If the system can be assembled from existing primitives, do not add new primitives.

### Fourth, preserve determinism
Any new runtime behavior should be explainable under replay and observability.

### Fifth, keep work auditable
Prefer changes that are easy to verify and easy to explain in milestone artifacts.

### Sixth, be explicit about deferrals
If something is outside current scope, say so and leave a documented hook rather than smuggling in partial behavior.

---

## 26. Recommended Next-Step Heuristics

If you need to push Foundry forward, the likely decision tree is:

### Path A — Improve Documentation
Choose this when the architecture exists but is too implicit for new contributors or agents.

### Path B — Extend Runtime Ergonomics
Choose this when the kernel and runtime are sound but hard to inspect, configure, or invoke.

### Path C — Add Typed Contracts
Choose this when event surfaces and API surfaces need stronger explicitness.

### Path D — Add Deferred Primitive(s)
Choose this only when the absence is architectural and well-evidenced — for example, consensus.

### Path E — Validate More Synthesized Systems
Choose this when you want to prove broader composability without altering the kernel.

---

## 27. Short Mental Model

If you remember nothing else, remember this:

### Foundry in one sentence
Foundry is a clean-room, audit-first runtime substrate built from minimal infrastructure primitives that can synthesize and orchestrate multiple systems without direct coupling.

### Foundry in one diagram
```text
upstream architectures
    ↓
primitive extraction
    ↓
minimal primitives
    ↓
system synthesis
    ↓
runtime substrate
    ↓
instantiated, orchestrated systems
```

### Foundry in one rule
Do not solve a synthesis problem by inventing a primitive, and do not solve a boundary problem by violating one.

---

## 28. Final Guidance for an Implementation Agent

Treat Foundry as a **disciplined architecture program**.

Do not:
- inflate primitives
- blur domain boundaries
- collapse systems into primitives
- collapse runtime layers into system logic
- bypass event/state mediation
- make undocumented behavioral changes

Do:
- preserve the architecture
- preserve explicit composition
- preserve determinism
- preserve evidence
- preserve the clean-room rule

If you need to extend Foundry, extend it in the layer where the responsibility naturally belongs.

That is the single most important implementation heuristic in the project.

---

## 29. Appendix: Quick Reference

### Implemented primitives
- `event_bus`
- `append_only_log`
- `versioned_state_store`
- `reconciliation_loop`
- `task_scheduler`
- `task_executor`
- `workflow_runtime`
- `graph_executor`

### Canonical systems
- `ControllerPlatform`
- `DagRuntimePlatform`
- `WorkflowEnginePlatform`

### Runtime substrate layers
- `SystemInstance`
- configuration layer
- `SystemAPI`
- `SystemGraph`
- `SystemOrchestrator`
- `SystemCatalog`
- runtime host

### Allowed coordination surfaces
- `event_bus`
- `versioned_state_store`

### Shared execution substrate
- `task_scheduler`
- `task_executor`

### Key non-goals right now
- distributed runtime
- persisted multi-process orchestration
- mature DSL
- full typed contract layer
- implemented consensus primitive
- PyPI / TestPyPI distribution

---

## 30. Suggested Verification Standard

A strong verification pass for this document should confirm:

1. The structure section shows only `foundry/`
2. The kernel matches implemented primitives
3. The canonical systems match synthesized systems
4. Runtime substrate layers match the current runtime model
5. Boundary rules match the enforcement model
6. Limitations are explicit and honest
7. No statements imply copied upstream code
8. No statements imply consensus is implemented when it is not

If any of those fail, correct the document conservatively rather than expanding scope.

---

## Change Log

### 2026-03-20 — Post-M77 Verification Pass

| What | Detail |
|------|--------|
| **Added** §9 Phases IX–XI | Document stopped at Phase VIII; three completed phases were missing. Phase IX (interface/usability), Phase X (proof of value / real-world refactor), Phase XI (audit closure, CI hardening, release packaging) now documented. |
| **Added** §24 directories | `baseline_system/`, `refactored_system/`, `case_study/`, `research/` (Phase X artifacts), plus `CHANGELOG.md`, `CONTRIBUTING.md`, `MANIFEST.in`, `pyproject.toml` (Phase XI / M77). |
| **Added** §20 Release capability | New "Release and Packaging Level" block reflecting version 1.0.0, CI-built artifacts, provenance, CHANGELOG, tag. |
| **Added** §21.6 PyPI limitation | Explicit note that no PyPI/TestPyPI publish exists yet. |
| **Added** §29 non-goal | "PyPI / TestPyPI distribution" appended to key non-goals. |
| **Why** | A handoff agent reading the document would have no awareness of Phases IX–XI, the proof-of-value artifacts, or the release surface without these additions. All claims verified against the committed `foundry/` subtree. |
