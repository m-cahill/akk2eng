# DARIA Operating Manual v1.0.0

Deterministic AI Research Instrumentation & Architecture

This document is intended to be sufficient for an AI agent (Cursor, ChatGPT, or similar) to correctly operate DARIA without external context. When ambiguity exists, prefer deterministic, contract-aligned interpretations.

---

## Design Philosophy (Quick Reference)

- Determinism over convenience
- Contracts over implicit behavior
- Artifacts over in-memory state
- Composition over specialization
- Core stability over feature growth

---

## 1. System Overview

### What DARIA is

DARIA is a **deterministic runtime substrate** for reproducible AI research experiments. It orchestrates typed execution graphs (DAGs), produces canonical artifact bundles with deterministic hashes, and enforces reproducibility through immutable contracts.

DARIA is:

- **Deterministic** — identical inputs produce identical outputs, schedules, transcripts, and hashes.
- **Artifact-first** — every execution produces canonical, hashable output bundles.
- **Domain-agnostic** — supports agents, computer vision, volumetric instruments, and any ML workflow.
- **ML-agnostic** — orchestrates models via plugins; does not implement training or inference.
- **Plugin-based** — all domain logic lives in versioned plugins; the core is invariant.

### What DARIA is not

DARIA does not:

- Implement ML models or training loops
- Perform perception (handled by EZRA)
- Certify artifacts (handled by RediAI)
- Manage infrastructure or deployments
- Store raw datasets as a repository of record

### Relationship to EZRA and RediAI

```text
EZRA (perception runtime)
  │
  │  produces EPB bundles, frame embeddings, detection maps
  ▼
DARIA (experiment orchestration)
  │
  │  produces artifact bundles with deterministic root hashes
  ▼
RediAI (artifact certification)
```

- **EZRA → DARIA:** DARIA consumes EZRA outputs (e.g. EPB bundles) as input artifacts via adapter plugins. DARIA does not mutate EZRA artifacts.
- **DARIA → RediAI:** DARIA produces certifiable artifact bundles with root hashes. RediAI certifies those artifacts. DARIA does not embed certification logic; it invokes RediAI at the boundary via the `rediai_certify@0.1` plugin.

---

## 2. Core Mental Model

### The pipeline

Every DARIA experiment follows one deterministic pipeline:

```text
Manifest → ExecutionGraph → Normalize → Validate → Schedule → Execute → ArtifactBundle
```

### Key invariant

```text
Same manifest + same graph + same locked plugins + same canonicalization profile
  → same schedule
  → same transcript
  → same artifact hashes
  → same root hash
```

### Artifact-first design

Every node execution produces output that is:

1. Canonicalized (M04 profile: UTF-8, sorted keys, no whitespace, no NaN/Infinity)
2. Hashed (SHA-256 over canonical bytes)
3. Assembled into a hash tree (M05: lexicographic ordering, pairwise SHA-256, odd-node duplication)
4. Collapsed to a single root hash (the bundle identity)

The root hash is the artifact's identity for certification by RediAI.

---

## 3. Key Concepts

### Manifest

A declarative JSON specification of an experiment. Contains:

| Field | Type | Purpose |
|-------|------|---------|
| `manifest_version` | string | Schema version |
| `experiment_id` | string | Unique experiment identifier |
| `seed` | integer | Deterministic random seed |
| `created_by` | string | Creator identifier |
| `graph` | object | Embedded execution graph (nodes + edges) |

Schema: `schemas/manifest/runtime_manifest_v0.1.schema.json`

Manifests do not contain node `id` fields — the key in the `nodes` object serves as the node ID. The `pipeline_runner` injects `id` during graph compilation.

### ExecutionGraph

A typed directed acyclic graph (DAG) describing execution order and data dependencies. Contains:

| Field | Type | Purpose |
|-------|------|---------|
| `version` | `"0.1"` | Schema version (const) |
| `nodes` | object | Map of node ID → node definition |
| `edges` | array | Dependency edges (`from` → `to`) |

Schema: `schemas/graph/execution_graph_v0.1.schema.json`

Three typed representations exist in the pipeline:

| Type | Source | Properties |
|------|--------|------------|
| `ExecutionGraph` | Loader (M06) | Preserves insertion order; raw from JSON |
| `CanonicalExecutionGraph` | Normalizer (M07) | Nodes sorted by ID; edges sorted by (from, to); params canonicalized; frozen |
| `ValidatedExecutionGraph` | Validator (M08) | Same shape as canonical; guaranteed DAG, no self-edges, valid references |

### Node

A single execution unit in the graph:

| Field | Type | Required | Purpose |
|-------|------|----------|---------|
| `id` | string | yes | Unique node identifier (must equal key in `nodes`) |
| `plugin` | object | yes | Plugin reference: `name` + `version` |
| `parameters` | object | yes | Plugin-specific configuration |
| `inputs` | array of strings | yes | Upstream node IDs |
| `outputs` | object | yes | Contains `artifacts` array of declared output names |
| `node_type` | string | no | One of: perception, replay, simulation, evaluation, packaging, training, sweep |

### Plugin

A versioned, swappable execution unit that implements the `DariaPlugin` protocol:

```python
class DariaPlugin(Protocol):
    CONTRACT: PluginContract

    def execute(
        self,
        inputs: dict[str, Any],
        params: dict[str, Any],
        ctx: dict[str, Any],
    ) -> dict[str, Any]: ...
```

Plugins are identified by exact `name@version` matching. No `"latest"` or partial version matching is supported.

### PluginContract

Typed metadata for graph validation:

```python
@dataclass(frozen=True)
class PluginContract:
    plugin: str              # plugin name
    version: str             # plugin version
    category: str            # one of: replay, evaluation, analysis, adapter, experiment
    inputs: dict[str, str]   # port name → artifact type
    outputs: dict[str, str]  # port name → artifact type
    params: dict[str, str]   # param name → type hint (structural only)
```

When a registry is provided to graph validation, edge type compatibility is checked: producer output artifact type must exactly match consumer input artifact type.

### Artifact Types

DARIA produces several bundle types:

| Bundle Type | Milestone | Contents | Purpose |
|-------------|-----------|----------|---------|
| Execution bundle | M11 | Transcript + node payloads + hash tree + root hash | Primary certifiable output of a graph run |
| Dataset bundle | M24 | manifest.json, dataset_metadata.json, split files, hashes.json | Deterministic ML input artifact |
| Model bundle | M26 | manifest.json, model_metadata.json, weights/, optional tokenizer/, hashes.json | Packaged model output |
| Evaluation bundle | M26 | manifest.json, metrics.json (versioned), hashes.json | Metrics output |
| Submission bundle | M26 | manifest.json, predictions.csv, model_hash.txt, hashes.json | External evaluator submission |

All directory bundles use the same M05 per-file hashing and hash-tree semantics.

---

## 4. Execution Flow

### Step-by-step runtime pipeline

```text
Step 1: Load manifest JSON
          ↓
Step 2: Validate manifest against runtime_manifest_v0.1.schema.json (jsonschema)
          ↓
Step 3: Compile manifest → ExecutionGraph dict
         (pipeline_runner.manifest_to_execution_graph_dict: injects node id, bundle_root)
          ↓
Step 4: Load ExecutionGraph (M06 — graph/loader.py)
         - Read JSON, validate against execution_graph_v0.1.schema.json
         - Build typed Node/Edge/Plugin objects
         - Check key==id, edge refs exist
         - Preserve insertion order (OrderedDict)
          ↓
Step 5: Normalize → CanonicalExecutionGraph (M07 — graph/normalize.py)
         - Sort nodes lexicographically by id
         - Sort edges by (from_node, to_node)
         - Canonicalize parameters (sorted keys, reject NaN/Infinity, normalize -0.0)
         - Idempotent: normalize(normalize(g)) == normalize(g)
          ↓
Step 6: Validate → ValidatedExecutionGraph (M08 — graph/validate.py)
         - Unique node IDs
         - Edge references valid
         - No self-edges
         - Acyclic (topological sort)
         - Sweep node constraints (M25)
         - Plugin contract type matching (M12, when registry provided)
         - Errors sorted deterministically by (node_id, edge_index, error_type)
          ↓
Step 7: Build ExecutionSchedule (M09 — runtime/executor.py)
         - Kahn's algorithm with lexicographic tie-breaking
         - Same graph → same execution order
          ↓
Step 8: Execute nodes in schedule order (M10 — runtime/node_runner.py)
         - For each node: resolve plugin via registry, build inputs from upstream outputs
         - Call plugin.execute(inputs, params, ctx)
         - Record node_started/node_finished/node_failed events
         - Sweep nodes: expand grid deterministically, inject _sweep_combinations
         - Produce ExecutionTranscript (no timestamps, no UUIDs)
          ↓
Step 9: Create ArtifactBundle (M11 — artifacts/writer.py)
         - Fail-fast if any node_failed in transcript
         - Canonicalize transcript + all node outputs
         - Compute artifact hashes (SHA-256 of canonical bytes)
         - Build hash tree (lexicographic by path: "transcript", "node:<id>")
         - Compute root hash
          ↓
Step 10: Save bundle + sidecars (M11, M22, M23)
          - Write bundle JSON
          - Write artifact_manifest.json (M22)
          - Write artifact_lineage.json when graph provided (M23)
```

### What `pipeline_runner.py` does

`daria/pipeline_runner.py` is thin composition glue (not part of the core execution kernel). It provides two entry points:

- `run_manifest_pipeline(manifest_path, work_dir, ...)` — validates manifest, compiles graph, executes
- `run_execution_graph_file_pipeline(graph_path, work_dir, ...)` — loads graph JSON, injects bundle_root, executes

Both accept `prepare_registry`: a callback to register plugins outside core (e.g. `register_builtins`).

---

## 5. Artifact System

### Execution bundle (M11)

The primary output of a graph run. Contains:

| Field | Type | Purpose |
|-------|------|---------|
| `bundle_version` | string | `"0.1"` |
| `runtime_version` | string | `"0.1"` |
| `transcript_hash` | string | SHA-256 of canonical transcript bytes |
| `artifacts` | object | Map of node_id → artifact hash |
| `hash_tree` | array | Ordered leaf hashes |
| `root_hash` | string | Bundle identity (Merkle root) |
| `transcript` | object | Full execution transcript (optional in serialization) |
| `artifact_payloads` | object | Node outputs (optional serialization of node outputs; canonical bytes are used for hashing regardless of serialization choice) |

### Hash tree construction (M05)

1. Collect all artifacts: transcript bytes + each node output (canonical JSON bytes)
2. Sort paths lexicographically (`"node:eval"`, `"node:train"`, `"transcript"`)
3. Compute SHA-256 of each artifact's canonical bytes → leaf hashes
4. Build Merkle tree: if odd count, duplicate last; pairwise SHA-256(left_bytes + right_bytes); repeat until one node
5. The final node is the root hash (64-char lowercase hex)

### Root hash meaning

The root hash is the **identity of the artifact bundle**. It represents:

- All node outputs
- The execution transcript
- The canonicalization profile used

Same logical content → same root hash. The root hash is what RediAI certifies.

### Directory bundle layout (M24–M26)

All directory bundles share a common layout:

```text
<bundle_dir>/
  manifest.json          ← bundle metadata (bundle_type, version, etc.)
  hashes.json            ← per-file SHA-256 hashes + root_hash
  artifact_manifest.json ← introspection sidecar
  <type-specific files>
```

Type-specific contents:

| Type | Additional Files |
|------|-----------------|
| dataset_bundle | `dataset_metadata.json`, `train.jsonl`, `validation.jsonl`, `test.jsonl` |
| model_bundle | `model_metadata.json`, `weights/` (required, opaque), `tokenizer/` (optional) |
| evaluation_bundle | `metrics.json` (versioned: `{"version":"0.1","metrics":{...}}`) |
| submission_bundle | `predictions.csv` (opaque), `model_hash.txt` (upstream root_hash) |

### Introspection surfaces (M22–M24, M26)

| Surface | File / API | Purpose |
|---------|-----------|---------|
| Manifest | `artifact_manifest.json` | Bundle summary without full load |
| Lineage | `artifact_lineage.json` | Node/plugin/input provenance |
| Inspection | `daria.artifacts.introspection.inspect_bundle` | Typed dispatch for all bundle types |

---

## 6. Plugin System

### The execute contract

Every plugin implements exactly one method:

```python
def execute(
    self,
    inputs: dict[str, Any],
    params: dict[str, Any],
    ctx: dict[str, Any],
) -> dict[str, Any]
```

| Argument | Content |
|----------|---------|
| `inputs` | Map of input port names to values derived from upstream node outputs |
| `params` | Node parameters from the graph (canonicalized) |
| `ctx` | Execution context (opaque; may carry run metadata) |
| **return** | Map of output port names to JSON-serializable values |

`execute` must be **deterministic** for identical `(inputs, params)`.

### PluginContract

Each plugin exposes a `CONTRACT` class attribute of type `PluginContract`:

```python
CONTRACT = PluginContract(
    plugin="my_plugin",
    version="0.1.0",
    category="experiment",       # replay | evaluation | analysis | adapter | experiment
    inputs={"data": "dataset_bundle"},
    outputs={"model": "model_ref"},
    params={"epochs": "int", "lr": "float"},
)
```

### PluginRegistry

In-process registry with deterministic resolution:

```python
registry = PluginRegistry()
registry.register(PluginId(name="my_plugin", version="0.1.0"), plugin_instance, contract)

plugin, contract = registry.resolve(PluginId(name="my_plugin", version="0.1.0"))
```

- Resolution is **exact match** only: `(name, version)`.
- `"latest"` is disallowed.
- `list_contracts()` returns all contracts sorted by `(name, version)`.

### Core/plugin boundary (M28)

Core code (`daria/runtime/`, `daria/graph/`, `daria/artifacts/`, `daria/utils/`, `daria/pipeline_runner.py`) may import only:

- `daria.plugins.registry` — `PluginRegistry`
- `daria.plugins.interfaces` — re-exports `PluginId`, `PluginResolutionError`, `PluginContract`

Core must **never** import plugin implementations (`builtins`, `m27_demo_pipeline`, concrete plugin packages). Plugin registration happens outside core via `prepare_registry` callbacks.

This boundary is enforced by `scripts/check_boundaries.py` and CI job `boundary-check`.

---

## 7. End-to-End Pipeline Example

### Kaggle-style ML pipeline (M27)

```text
dataset_bundle → training → model_bundle → evaluation → evaluation_bundle → submission → submission_bundle
```

#### Graph structure

```text
Nodes:
  dataset_fixture   → writes dataset_bundle/
  training_stub     → reads dataset ref, writes model_bundle/
  evaluation_stub   → reads model ref, writes evaluation_bundle/
  submission_stub   → reads eval ref, writes submission_bundle/

Edges:
  dataset_fixture → training_stub
  training_stub → evaluation_stub
  evaluation_stub → submission_stub
```

#### Running it

```bash
# From manifest
python scripts/run_pipeline.py \
  --manifest manifests/examples/kaggle_pipeline_manifest.json \
  --work-dir ./output

# From graph directly
python scripts/run_pipeline.py \
  --graph graphs/examples/kaggle_pipeline.json \
  --work-dir ./output
```

#### What happens

1. Manifest is validated against `runtime_manifest_v0.1.schema.json`
2. Graph is compiled (node IDs injected, `bundle_root` injected into params)
3. Graph is loaded → normalized → validated → scheduled
4. Nodes execute in topological order; each toy plugin writes a directory bundle
5. Execution bundle (M11) is created with transcript + node outputs + hash tree
6. `artifact_manifest.json` and `artifact_lineage.json` are written alongside the bundle

#### Demo plugins

| Plugin ID | Role |
|-----------|------|
| `m27_dataset_fixture@0.1.0` | Writes a tiny dataset_bundle |
| `m27_training_stub@0.1.0` | Consumes dataset ref, writes model_bundle |
| `m27_evaluation_stub@0.1.0` | Consumes model ref, writes evaluation_bundle |
| `m27_submission_stub@0.1.0` | Consumes eval ref, writes submission_bundle |

These are deterministic toy implementations — no real ML logic. They demonstrate the full artifact pipeline using existing primitives.

#### Files

| Artifact | Path |
|----------|------|
| Kaggle-style graph | `graphs/examples/kaggle_pipeline.json` |
| Kaggle-style manifest | `manifests/examples/kaggle_pipeline_manifest.json` |
| Minimal training graph | `graphs/examples/minimal_training_pipeline.json` |
| Minimal training manifest | `manifests/examples/minimal_training_manifest.json` |

---

## 8. Determinism Rules

### What must be stable (same inputs → same output)

| Component | Guarantee |
|-----------|-----------|
| Canonicalization | UTF-8, sorted keys, no whitespace, no NaN/Infinity → identical bytes |
| Hashing | SHA-256 over canonical bytes → identical artifact hashes |
| Hash tree | Lexicographic path ordering, pairwise SHA-256, odd-node duplication → identical root hash |
| Normalization | Nodes sorted by ID, edges sorted by (from, to), params canonicalized → identical canonical graph |
| Validation | Errors sorted by (node_id, edge_index, error_type) → identical error output |
| Scheduling | Kahn's algorithm with lexicographic tie-breaking → identical execution order |
| Transcript | Monotonic seq counter, no timestamps/UUIDs → identical event sequence |
| Plugin execution | `execute(inputs, params, ctx)` must be deterministic for identical (inputs, params) |

### What can vary

| Component | Variation allowed |
|-----------|-------------------|
| Absolute file paths | Bundle payloads may embed host-specific paths (deferred hardening) |
| Execution wall-clock time | Not recorded in transcripts |
| Python version | Must not affect canonical bytes (v0.1 profile is version-independent) |
| OS | Must not affect canonical bytes |

### Hidden state prohibition

Plugins must not rely on external mutable state (filesystem, network, global variables) unless explicitly provided through inputs or parameters. Any hidden state breaks determinism and is not permitted in v1.

---

## 9. Boundary Rules (M28)

### Core vs plugin separation

**Core** (invariant runtime kernel):

| Path | Role |
|------|------|
| `daria/runtime/` | Scheduling, node execution, transcript |
| `daria/graph/` | Loader, normalizer, validator |
| `daria/artifacts/` | Artifact engine, bundle types, introspection |
| `daria/utils/` | Canonicalization, hashing, sweep expansion |
| `daria/pipeline_runner.py` | Thin composition glue |

**Plugin ecosystem** (everything domain-facing):

| Path | Role |
|------|------|
| `daria/plugins/builtins.py` | Registration of toy plugins |
| `daria/plugins/m27_demo_pipeline.py` | M27 demo pipeline plugins |
| `daria/plugins/<plugin_name>/` | Concrete plugin packages |

### Allowed imports from plugins (core only)

| Module | What core may import |
|--------|---------------------|
| `daria.plugins.registry` | `PluginRegistry` |
| `daria.plugins.interfaces` | `PluginId`, `PluginResolutionError`, `PluginContract` |

### Forbidden imports from core

Core must not import:

- `daria.plugins.builtins`
- `daria.plugins.m27_demo_pipeline`
- Any concrete plugin package (`tick_replay`, `evaluation_metrics`, etc.)
- `daria.plugins.protocol`, `daria.plugins.models`, `daria.plugins.contracts` (use `interfaces` instead)

### Composition pattern

```python
from daria.plugins.builtins import register_builtins

# Outside core: scripts/run_pipeline.py or tests
root_hash, outputs = run_manifest_pipeline(
    manifest_path,
    work_dir,
    prepare_registry=register_builtins,
)
```

`prepare_registry` is a callback `Callable[[PluginRegistry], None]` invoked with a fresh registry before validation. This keeps plugin registration outside core.

---

## 10. How to Use DARIA

### Running a pipeline

**From a manifest:**

```bash
python scripts/run_pipeline.py \
  --manifest manifests/examples/kaggle_pipeline_manifest.json \
  --work-dir ./output
```

**From a graph:**

```bash
python scripts/run_pipeline.py \
  --graph graphs/examples/kaggle_pipeline.json \
  --work-dir ./output
```

**Programmatically:**

```python
from pathlib import Path
from daria.pipeline_runner import run_manifest_pipeline
from daria.plugins.builtins import register_builtins

root_hash, node_outputs = run_manifest_pipeline(
    Path("manifests/examples/kaggle_pipeline_manifest.json"),
    Path("./output"),
    prepare_registry=register_builtins,
)
print(f"Root hash: {root_hash}")
```

### Writing a manifest

A manifest is a JSON file with this structure:

```json
{
  "manifest_version": "0.1",
  "experiment_id": "my-experiment-001",
  "seed": 42,
  "created_by": "researcher-name",
  "graph": {
    "nodes": {
      "load_data": {
        "plugin": { "name": "my_loader", "version": "1.0.0" },
        "parameters": { "dataset": "train.csv" },
        "inputs": [],
        "outputs": { "artifacts": ["dataset"] }
      },
      "train_model": {
        "plugin": { "name": "my_trainer", "version": "1.0.0" },
        "parameters": { "epochs": 10 },
        "inputs": ["load_data"],
        "outputs": { "artifacts": ["model"] }
      }
    },
    "edges": [
      { "from": "load_data", "to": "train_model" }
    ]
  }
}
```

Rules:

- Node keys are the node IDs (do not repeat `id` inside the node)
- `plugin.version` must not be `"latest"`
- `inputs` lists upstream node IDs
- `outputs.artifacts` lists declared artifact names
- Optional: `node_type` (perception, replay, simulation, evaluation, packaging, training, sweep)

### Adding a plugin

1. Create a plugin class implementing `DariaPlugin`:

```python
from daria.plugins.contracts import PluginContract
from typing import Any

class MyPlugin:
    CONTRACT = PluginContract(
        plugin="my_plugin",
        version="1.0.0",
        category="experiment",
        inputs={"data": "dataset_bundle"},
        outputs={"result": "model_ref"},
        params={"epochs": "int"},
    )

    def execute(
        self,
        inputs: dict[str, Any],
        params: dict[str, Any],
        ctx: dict[str, Any],
    ) -> dict[str, Any]:
        data = inputs.get("data", {})
        epochs = params.get("epochs", 1)
        return {"result": {"model_name": "trained", "epochs": epochs}}
```

2. Register it in a registration function (outside core):

```python
from daria.plugins.models import PluginId
from daria.plugins.registry import PluginRegistry

def register_my_plugins(registry: PluginRegistry) -> None:
    plugin = MyPlugin()
    registry.register(
        PluginId(name="my_plugin", version="1.0.0"),
        plugin,
        plugin.CONTRACT,
    )
```

3. Pass the registration function to `pipeline_runner`:

```python
root_hash, outputs = run_manifest_pipeline(
    manifest_path,
    work_dir,
    prepare_registry=register_my_plugins,
)
```

### Inspecting bundles

```bash
# Inspect any bundle type (execution, dataset, model, evaluation, submission)
python scripts/inspect_bundle.py path/to/bundle/
```

Programmatically:

```python
from daria.artifacts.introspection import inspect_bundle
doc = inspect_bundle(Path("path/to/bundle/"))
print(doc)
```

---

## 11. Debugging Guide

### Common failure modes

| Error | Type | Cause | Resolution |
|-------|------|-------|------------|
| `GraphLoadError` | Load | Invalid JSON, schema failure, key/id mismatch, missing edge refs | Check JSON syntax; ensure `node.id == key`; verify edge node refs |
| `NormalizationError` | Normalize | NaN, Infinity, or unsupported type in parameters | Remove NaN/Infinity; ensure params are JSON-safe |
| `GraphValidationError` | Validate | Duplicate nodes, invalid edges, self-edges, cycles, contract mismatches | Check graph structure; fix cycles; align plugin contracts |
| `SchedulingError` | Schedule | Unreachable nodes after validation | Should not occur after validation; indicates internal bug |
| `PluginResolutionError` | Execute | Plugin not found in registry | Register the plugin before execution; check name+version |
| `ExecutionError` | Execute | Plugin raised an exception | Check plugin logic; inspect error_message in transcript |
| `ArtifactBuildError` | Bundle | node_failed in transcript, or canonicalization failure | Fix plugin errors first; ensure outputs are JSON-serializable |
| `CanonicalizationError` | Hashing | NaN, Infinity, or duplicate keys in input | Sanitize data; avoid special float values |

### How to inspect artifacts

**Execution bundle:**

```python
from daria.artifacts import load_artifact_bundle
bundle = load_artifact_bundle(Path("path/to/bundle.json"))
print(bundle.root_hash)
print(bundle.artifacts)  # node_id → hash
```

**Manifest sidecar:**

```python
from daria.artifacts import load_manifest
manifest = load_manifest(Path("path/to/artifact_manifest.json"))
# Returns dict with root_hash, artifact_count, node_ids, plugin info
```

**Lineage sidecar:**

```python
from daria.artifacts import load_lineage
lineage = load_lineage(Path("path/to/artifact_lineage.json"))
# Returns dict with node_id → plugin + inputs + artifact_hash
```

**Directory bundles:**

```python
from daria.artifacts import (
    load_dataset_bundle, validate_dataset_bundle,
    load_model_bundle, validate_model_bundle,
    load_evaluation_bundle, validate_evaluation_bundle,
    load_submission_bundle, validate_submission_bundle,
)

ds = load_dataset_bundle(Path("path/to/dataset_bundle/"))
validate_dataset_bundle(ds)  # raises on invalid
```

### How to trace execution

1. **Read the transcript** — `bundle.transcript_doc["events"]` lists all events in sequence order. Each event has `seq`, `event_type` (node_started/node_finished/node_failed), `node_id`, and `payload`.

2. **Check the schedule** — Build a schedule from a validated graph to see execution order:

```python
from daria.runtime import build_execution_schedule
schedule = build_execution_schedule(validated_graph)
print(schedule.order)  # ['node_a', 'node_b', 'node_c']
```

3. **Compare root hashes** — If two runs should be identical, compare root hashes. If they differ, compare per-node artifact hashes (`bundle.artifacts`) to find the divergent node.

4. **Check boundary violations** — Run `python scripts/check_boundaries.py` to verify no core → plugin implementation imports.

---

## 12. Extension Guide

### Adding new plugins

Follow the pattern in section 10 ("Adding a plugin"):

1. Implement `DariaPlugin` protocol with `CONTRACT` and `execute`
2. Register via a function passed as `prepare_registry`
3. Reference in graph nodes by exact `name@version`
4. Declare `inputs`/`outputs` artifact types in the contract for edge validation

Plugin categories: `replay`, `evaluation`, `analysis`, `adapter`, `experiment`.

### Adding new artifact types (future)

New artifact types would require:

1. A new `create_*_bundle` / `load_*_bundle` / `validate_*_bundle` / `write_*_bundle` module under `daria/artifacts/`
2. Registration in `KNOWN_DIRECTORY_BUNDLE_TYPES` (`daria/artifacts/constants.py`)
3. A new `inspect_*_bundle` function and dispatch case in `daria/artifacts/introspection.py`
4. Hash computation using the same M05 hash-tree semantics

This is **out of scope for v1.0.0** — it would require a minor version bump (v1.1+).

### Adding new node types (future)

The `node_type` enum may be extended by adding values to the schema and implementing corresponding validation logic in `daria/graph/validators/`. Existing graphs without the new type remain valid.

This is **out of scope for v1.0.0** — it would require a minor version bump.

### What NOT to change

These are frozen for v1.0.0 and must not be modified without a major version bump:

| Component | What is frozen |
|-----------|---------------|
| Plugin entrypoint | `execute(inputs, params, ctx) -> dict[str, Any]` |
| Registry resolution | Exact `name@version` match; no floating versions |
| Canonicalization | M04 profile: UTF-8, sorted keys, no whitespace, no NaN/Infinity |
| Hashing | M05: SHA-256, lexicographic ordering, pairwise combination, odd-node duplication |
| Schema fields | All required fields in `runtime_manifest_v0.1` and `execution_graph_v0.1` |
| Bundle fields | All required fields in execution bundles and M24–M26 directory bundles |
| Validation rules | Structural validators (uniqueness, edge refs, acyclicity, self-edge, sweep constraints) |
| Introspection returns | Stable return shapes; additive fields allowed, breaking renames require version bump |

---

## 13. v1 Guarantees

### What is frozen

| Surface | Document | Status |
|---------|----------|--------|
| ExecutionGraph schema v0.1 | `schemas/graph/execution_graph_v0.1.schema.json` | Frozen |
| Runtime Manifest schema v0.1 | `schemas/manifest/runtime_manifest_v0.1.schema.json` | Frozen |
| Plugin contract | `docs/architecture/plugin_contract_v1.md` | Frozen |
| Artifact contract | `docs/architecture/artifact_contract_v1.md` | Frozen |
| Core/plugin boundary | `docs/architecture/boundary_audit.md` | Frozen |
| Canonicalization profile v0.1 | `docs/architecture/canonicalization_profile_v0.1.md` | Frozen |
| Hash tree v0.1 | `docs/architecture/hash_tree_v0.1.md` | Frozen |

### What requires a version bump

| Change type | Required version bump |
|-------------|----------------------|
| New optional schema field | Minor (v1.1+) |
| New node_type enum value | Minor (v1.1+) |
| New bundle type | Minor (v1.1+) |
| New plugin category | Minor (v1.1+) |
| Remove/rename required field | Major (v2.0+) |
| Change execute() signature | Major (v2.0+) |
| Change resolution semantics | Major (v2.0+) |
| Change canonicalization rules | Major (v2.0+) |
| Change hash tree construction | Major (v2.0+) |

### Compatibility summary

- **Backward compatible:** existing manifests, graphs, bundles, and plugins continue to work across all v1.x releases.
- **Forward compatible:** additive changes (new optional fields, new enum values, new bundle types) are allowed in minor versions. Existing consumers that ignore unknown fields are unaffected.
- **Breaking changes:** require explicit major version bump, migration guide, and updated schema version identifiers.

---

## Appendix A: Repository Structure

```text
daria/
  graph/                     ← loader, normalizer, validator, models
  runtime/                   ← scheduling, node runner, transcript
  artifacts/                 ← artifact engine, bundle types, introspection
  plugins/                   ← plugin protocol, registry, contracts, builtins
  pipeline_runner.py         ← thin composition (not core kernel)
  utils/                     ← canonicalization, hashing, sweep expansion

schemas/
  manifest/                  ← runtime_manifest_v0.1.schema.json
  graph/                     ← execution_graph_v0.1.schema.json

graphs/examples/             ← example execution graphs
manifests/examples/          ← example manifests

scripts/
  run_pipeline.py            ← CLI for running pipelines
  run_graph.py               ← CLI for running graphs
  check_boundaries.py        ← core/plugin boundary enforcement
  inspect_bundle.py          ← bundle inspection CLI
  validate_manifest.py       ← manifest validation CLI
  validate_execution_graph.py ← graph validation CLI

tests/
  integration/               ← end-to-end pipeline tests (M27)
  artifacts/                 ← artifact engine tests (M24, M26)

docs/
  daria.md                   ← project source of truth + milestone ledger
  daria_operating_manual_v1.md ← this document
  architecture/              ← all architecture specs and contracts
```

## Appendix B: Quick Reference Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Lint entire repo
ruff check .

# Check core/plugin boundary
python scripts/check_boundaries.py

# Run Kaggle-style pipeline
python scripts/run_pipeline.py \
  --manifest manifests/examples/kaggle_pipeline_manifest.json \
  --work-dir ./output

# Inspect a bundle
python scripts/inspect_bundle.py path/to/bundle/

# Validate a manifest
python scripts/validate_manifest.py manifests/examples/kaggle_pipeline_manifest.json

# Validate an execution graph
python scripts/validate_execution_graph.py graphs/examples/kaggle_pipeline.json
```
