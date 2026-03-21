# EZRA Operating Manual v1.0.0

Extensible Zone-Based Runtime Architecture

This document is intended to be sufficient for an AI agent (Cursor, ChatGPT, or similar) to correctly operate EZRA without external context. When ambiguity exists, prefer deterministic, contract-aligned interpretations.

---

## Design Philosophy (Quick Reference)

- Determinism over convenience
- Contracts over implicit behavior
- Artifacts over in-memory state
- Boundaries over features
- Replaceability over optimization
- Explicit interfaces over cleverness

---

## 0. Purpose & AI-Agent Instructions

This document is the **runtime operating manual** for EZRA. It describes:

- What EZRA is and is not
- The current implemented runtime surface
- Plugin contracts and boundaries
- EPB bundle construction rules
- How to use EZRA programmatically
- Debugging and extension patterns

### Interpretation Rules

1. **Determinism over convenience** — prefer interpretations that produce deterministic, reproducible results.
2. **Contracts over assumptions** — do not assume behavior that is not documented in this manual or proven by code.
3. **No hidden behavior** — EZRA has no hidden state, no implicit side effects, no ambient configuration.
4. **Code wins over intent** — if this document and `VISION.md` disagree on current behavior, this document and actual code take precedence. `VISION.md` describes architectural intent, not guaranteed implemented state.

### Honesty Markers Used in This Document

- **Implemented** — feature exists in current code and is tested
- **Not Yet Implemented** — declared in `VISION.md` as architectural target but not present in code
- **UNKNOWN** — insufficient evidence to determine current status

### Related Documents

| Document | Role |
|----------|------|
| `docs/ezra.md` | Governance ledger, milestone record, repo source of truth |
| `docs/VISION.md` | Architectural intent and boundaries (non-goals) |
| `docs/specs/epb_v1/EPB_V1_SPEC.md` | EPB v1.0.0 artifact specification |
| `docs/phase_v_completion_declaration.md` | Phase V freeze declaration |
| This document | Runtime operating manual, AI-agent execution guide |

If this document and `docs/ezra.md` disagree on governance or milestones, `docs/ezra.md` wins. If they disagree on runtime behavior, this document wins (it is derived from code).

---

## 1. System Overview

### What EZRA Is

EZRA is a **modular runtime perception engine** that converts raw pixels (screenshots, frames) into structured, interpretable state for interactive systems.

EZRA is:

- **Runtime-only** — it loads models and runs inference. No training logic.
- **ML-agnostic at core** — the core engine (`src/ezra/core/`) contains no ML code. ML is loaded via plugins.
- **Plugin-driven** — perception backends (EasyOCR, Tesseract, etc.) are swappable plugins behind a stable interface.
- **Artifact-producing** — EZRA emits EPB (EZRA Perception Bundle) v1.0.0 bundles: deterministic, hashable, certifiable output artifacts.
- **Deterministic** — all non-ML components produce identical output for identical input. ML nondeterminism is contained at the detection level.

### What EZRA Is Not

EZRA does not:

- Train ML models (training belongs to external pipelines / RediAI-v3)
- Annotate data (annotation tools like CVAT are upstream)
- Orchestrate experiments (orchestration is a separate concern)
- Certify artifacts (certification is an external consumer responsibility)
- Provide real-time performance guarantees
- Include a CLI entry point (**Not Yet Implemented**)

---

## 2. Core Mental Model

### The Pipeline (Architectural Target)

```text
Image → Preprocessing → Plugins → Detections → State → EPB Bundle
```

### Current Implemented Surface

The implemented pipeline is:

```text
Image → Plugin.infer() → Detections → EPB Bundle (optional)
```

Specifically:

| Stage | Status | Implementation |
|-------|--------|----------------|
| Image input | **Implemented** | Any format accepted by plugin (numpy array, PIL Image, file path) |
| Preprocessing | **Not Yet Implemented** | No core-level preprocessing (color normalization, resizing, tiling). Plugins handle their own preprocessing internally. |
| Plugin inference | **Implemented** | `OCRPlugin.infer(image)` returns `{"detections": [...]}` |
| Detection aggregation | **Implemented** | Detections are passed through from single plugin. Multi-plugin aggregation is **Not Yet Implemented**. |
| Structured state | **Partially Implemented** | `state.json` is emitted with minimal structure (version + timestamp). Domain-specific state reconstruction (e.g., chess FEN) is **Not Yet Implemented**. |
| EPB bundle emission | **Implemented** | Full EPB v1.0.0 bundle emission with canonical JSON, hashing, schema validation, and hash verification. |
| Zone-scoped projection | **Implemented** | Optional `zones.json` emission via adapter-gated wiring. Zone-scoped state projection utility available. |

### Key Invariant

```text
Same image + same plugin + same configuration
  → same detections (modulo ML nondeterminism, contained by canonicalization)
  → same EPB bundle
  → same bundle hash
```

---

## 3. Core Concepts

### Image / Frame

The input to EZRA's perception pipeline. Currently accepted as any format the active plugin supports (numpy array, PIL Image, or file path). The `ImageInput` frozen dataclass (`src/ezra/types.py`) defines the canonical type: `data` (bytes), `width`, `height`, `channels`, `metadata`.

### Detection

A single perception result from a plugin. Canonical schema:

```json
{
  "text": "string",
  "confidence": 0.99,
  "bbox": [10.0, 20.0, 50.0, 40.0]
}
```

Where `bbox` is `[x1, y1, x2, y2]` (axis-aligned bounding box, float coordinates). The `OCRResult` frozen dataclass (`src/ezra/types.py`) defines the canonical type.

### Zone

A named visual region mapped to a tensor channel with persistence semantics. Defined by `ZoneSchema` (`src/ezra/zones/schema.py`):

- `id`: unique zone identifier
- `kind`: zone category (free-form string)
- `channel_index`: tensor channel assignment (globally unique integer >= 0)
- `bbox_norm`: normalized bounding box (0-1 range)
- `persistence`: sticky flag controlling cross-frame behavior

Zones are managed via `ZoneRegistry` (`src/ezra/zones/registry.py`) with freeze-after-init semantics. Once frozen, no further registrations are allowed.

### State

Domain-agnostic structured state emitted in `state.json`. Currently minimal (version + timestamp). Domain-specific state reconstruction (chess board, card hand, UI elements) is **Not Yet Implemented**.

### Plugin

An ML backend wrapped behind the `OCRPlugin` abstract interface. Plugins are loaded via a static registry and resolved lazily to avoid importing heavy ML modules at startup.

### EPB Bundle

EZRA Perception Bundle v1.0.0 — the primary output artifact. A directory containing deterministic, canonical JSON files with SHA256 hashes. See Section 6 for full specification.

---

## 4. Execution Flow (Step-by-Step)

### Current Implemented Pipeline

The entry point is `EzraEngine.process_image()` (`src/ezra/core/engine.py`).

```text
Step 1: Instantiate plugin via registry
          get_plugin("easyocr", device="cpu") → OCRPlugin instance
            ↓
Step 2: Load model artifacts
          plugin.load(artifact_path)
            ↓
Step 3: Create engine
          engine = EzraEngine(plugin)
            ↓
Step 4: Process image
          result = engine.process_image(image, emit_epb=True, epb_output_dir=Path("./output"))
            ↓
Step 4a: Plugin inference
           plugin.infer(image) → {"detections": [...]}
            ↓
Step 4b: (If emit_epb=True) Build EPB bundle
           build_epb_bundle(detections, plugin_name, plugin_version, input_metadata)
            ↓
Step 4c: (If emit_epb=True) Validate bundle against JSON schemas
            ↓
Step 4d: (If emit_epb=True) Compute SHA256 hashes
            ↓
Step 4e: (If emit_epb=True) Write bundle to disk
           write_epb_bundle(bundle, output_dir)
            ↓
Step 4f: (If emit_epb=True) Verify bundle integrity (recompute hashes from disk)
            ↓
Step 5: Return detection result dict
```

### What Is NOT in the Pipeline

The following stages from `VISION.md` are **Not Yet Implemented**:

- Core-level preprocessing (color normalization, resizing, tiling, batching)
- Multi-plugin composition / aggregation
- Domain-specific state reconstruction
- Temporal delta computation between frames
- Device management / scheduling beyond what plugins handle internally

---

## 5. Plugin System

### Plugin Interface (Implemented)

All plugins implement the `OCRPlugin` ABC (`src/ezra/plugins/interface.py`):

```python
class OCRPlugin(ABC):
    @abstractmethod
    def load(self, artifact_path: str) -> None: ...

    @abstractmethod
    def infer(self, image: Any) -> dict[str, Any]: ...

    @abstractmethod
    def describe_capabilities(self) -> dict[str, Any]: ...
```

| Method | Purpose | Returns |
|--------|---------|---------|
| `load(artifact_path)` | Load model artifact from path | None |
| `infer(image)` | Run inference on input image | `{"detections": [{"text": str, "confidence": float, "bbox": [x1, y1, x2, y2]}]}` |
| `describe_capabilities()` | Report plugin metadata | Dict with `version`, `supported_formats`, `input_requirements`, `output_schema` |

### Plugin Registry (Implemented)

Static registry in `src/ezra/plugins/registry.py`:

```python
_PLUGIN_REGISTRY: dict[str, str] = {
    "easyocr": "ezra.plugins.easyocr_plugin:EasyOCRPlugin",
    "tesseract": "ezra.plugins.tesseract_plugin:TesseractPlugin",
}
```

Resolution is lazy (imports happen at `get_plugin()` call time, not at import time).

| Function | Purpose |
|----------|---------|
| `get_plugin(name, **kwargs)` | Resolve and instantiate a plugin by name |
| `get_plugin_from_config(config)` | Resolve from `{"name": "...", "kwargs": {...}}` dict |
| `list_plugins()` | Return sorted list of registered plugin names |
| `validate_registry()` | Verify all entries are correctly formatted and resolvable (does not instantiate) |

### Current Plugins

| Name | Class | Status | Dependencies |
|------|-------|--------|--------------|
| `easyocr` | `EasyOCRPlugin` | **Implemented** (functional) | Requires `pip install -e ".[easyocr]"` |
| `tesseract` | `TesseractPlugin` | **Implemented** (stub — returns empty detections) | No external dependencies |

### Plugin Constraints

- Registry is **static** — no dynamic discovery, no entry-point scanning
- Resolution is **exact match** by name — no version negotiation, no "latest"
- No environment variable resolution
- Plugins must not modify core engine state
- Plugins must not assume GPU availability
- Plugin output must conform to the detection schema

### EasyOCR Plugin Architecture

The EasyOCR plugin uses a two-layer design:

- `EasyOCRAdapter` (`src/ezra/plugins/easyocr_adapter.py`) — encapsulates all direct EasyOCR framework calls. Returns raw EasyOCR output unchanged.
- `EasyOCRPlugin` (`src/ezra/plugins/easyocr_plugin.py`) — implements `OCRPlugin`, delegates to adapter, transforms raw output to EZRA canonical detection format via `transform_easyocr_output()`.

This separation isolates third-party ML framework calls from plugin orchestration.

---

## 6. EPB Bundle Construction

### EPB v1.0.0 Directory Structure

An EPB bundle is a directory:

```text
epb/
  manifest.json       ← Bundle metadata, version, provenance
  detections.json     ← Raw OCR/detection results
  state.json          ← Domain-agnostic structured state
  delta.json          ← Optional: incremental state changes
  zones.json          ← Optional: zone schema definitions
  hashes.json         ← Deterministic SHA256 hashes for all components
```

### File Descriptions

| File | Required | Content |
|------|----------|---------|
| `manifest.json` | Yes | EPB version, EZRA version, timestamp, plugin versions, input metadata, platform, Python version |
| `detections.json` | Yes | `{"detections": [...]}` — raw plugin output in canonical form |
| `state.json` | Yes | `{"version": "1.0.0", "timestamp": "..."}` — currently minimal. This is a structural placeholder and should not be used for domain logic in v1.0.0. |
| `delta.json` | No | Incremental state changes (emitted only if delta data provided) |
| `zones.json` | No | Zone registry export (emitted only if `zone_registry` provided to writer) |
| `hashes.json` | Yes | Per-file SHA256 hashes + `bundle_hash` |

### Canonical JSON Rules (EPB v1.0.0)

All JSON files in an EPB bundle conform to:

| Rule | Value |
|------|-------|
| Encoding | UTF-8 |
| Line endings | LF only |
| Key ordering | Sorted alphabetically (case-sensitive) |
| Indentation | 2 spaces |
| Float precision | 8 decimal places (EPB canonical); 6 decimal places for `zones.json` (zone contract) |
| Forbidden values | NaN, Infinity, -Infinity |
| ASCII | `ensure_ascii=False` |

Implementation: `src/ezra/epb/canonical.py` (`to_canonical_json()`)

### Hashing Rules

| Rule | Implementation |
|------|----------------|
| Algorithm | SHA256 |
| Input | Canonical JSON string (UTF-8 encoded) |
| Output | Lowercase hexadecimal, 64 characters |
| Bundle hash | Sort file names alphabetically → concatenate hashes → SHA256 of concatenated string |
| Excluded from bundle hash | `hashes.json` itself (circular dependency) |
| Included in bundle hash | `zones.json` (if present) |

Implementation: `src/ezra/epb/hasher.py`

### Schema Validation

EPB bundles are validated against JSON Schema before writing. Invalid bundles fail fast with `EPBValidationError`.

Implementation: `src/ezra/epb/schema_validator.py`

Schemas: `docs/specs/epb_v1/schemas/` (manifest, detections, state, delta, hashes)

### Hash Verification

After writing, the bundle is verified by recomputing hashes from disk and comparing against `hashes.json`. Tampered bundles fail with `EPBHashError`.

Implementation: `src/ezra/epb/hash_verifier.py`

### Bundle Construction API

```python
from ezra.epb import build_epb_bundle, write_epb_bundle

bundle = build_epb_bundle(
    detections=[{"text": "Hello", "confidence": 0.99, "bbox": [10.0, 20.0, 50.0, 40.0]}],
    plugin_name="easyocr",
    plugin_version="1.7.2",
    input_metadata={"width": 640, "height": 480, "channels": 3},
)

write_epb_bundle(bundle, Path("./output/epb"))
```

The returned bundle is sealed with `MappingProxyType` for runtime immutability.

---

## 7. Relationship to External Systems

### EZRA's Role

EZRA is a **runtime perception engine** that produces EPB bundles. Those bundles may be consumed by downstream orchestration, evaluation, or certification systems.

### RediAI (Artifact Certification)

RediAI v3 can certify EPB bundles at the artifact boundary:

1. EZRA emits EPB bundle (deterministic, canonicalized per EPB v1.0.0)
2. RediAI validates bundle against JSON schemas
3. RediAI verifies hash integrity (`hashes.json`)
4. RediAI certifies bundle (or rejects with validation errors)

**No runtime integration.** No shared code, no shared modules, no imports in either direction. Integration is artifact-boundary-only.

### Artifact Trust Model

After M26, EPB bundles can be:

1. Structurally validated (JSON Schema)
2. Canonically serialized (deterministic JSON)
3. Hash-self-consistent (SHA256 verification)
4. Deterministically reproducible (identical inputs → identical bundles)
5. Validated via stdlib-only tool (`ezra.epb_tools.epb_certify`)
6. Cryptographically signed (optional Ed25519 detached signature via `ezra.epb_tools.epb_sign`). Signature support is an optional extension and is not part of the EPB v1.0.0 core contract.

### EPB Tools (Runtime-Independent)

The `ezra.epb_tools` namespace (`src/ezra/epb_tools/`) provides validation tools that do not import the EZRA runtime, plugins, or ML dependencies:

| Tool | Purpose |
|------|---------|
| `epb_certify` | Validate bundle structure, hash integrity, bundle hash (stdlib-only) |
| `epb_verify` | Verify detached Ed25519 signature (`bundle.sig`) |
| `epb_generate_cert_metadata` | Generate `bundle.cert.json` certification metadata envelope |

These tools are physically isolated from the runtime and can be used by external consumers.

---

## 8. Determinism Rules

### What Must Be Deterministic

| Component | Guarantee |
|-----------|-----------|
| Canonical JSON serialization | UTF-8, sorted keys, 8dp floats, no NaN/Infinity → identical bytes |
| SHA256 hashing | Hash of canonical bytes → identical artifact hashes |
| Bundle hash computation | Sorted file names, concatenated hashes → identical bundle hash |
| EPB bundle emission | Same detections + same metadata → identical bundle directory |
| Zone registry export | Sorted by (channel_index, id) → identical `zones.json` |
| Zone-scoped projection | Deterministic projection from zones + detections |

### What May Vary

| Component | Variation |
|-----------|-----------|
| ML inference output | GPU nondeterminism, floating-point precision differences |
| Timestamps | `manifest.json` and `state.json` contain wall-clock timestamps |
| Platform metadata | `manifest.json` records `platform` and `python_version` |

### ML Nondeterminism Containment

ML nondeterminism is **contained** at the detection level:

- Floats are rounded to 8 decimal places before serialization
- Detections are included as-is from plugin output (ordering preserved)
- Once canonicalized, the EPB bundle is fully deterministic

Detection arrays preserve plugin output ordering; no sorting is applied by EZRA. Plugins are responsible for deterministic ordering if required.

For determinism testing, EZRA provides a fixed timestamp injection via `build_epb_bundle(timestamp=...)` to eliminate timestamp variation.

### Hidden State Prohibition

EZRA has no hidden state. All behavior is determined by:

- The input image
- The plugin name and configuration
- The zone registry (if provided)
- The explicit function arguments

Core runtime does not rely on environment variables; plugins must not introduce hidden state.

---

## 9. How to Use EZRA

### Installation

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

pip install -e ".[dev]"
```

For EasyOCR plugin (requires ML dependencies):

```bash
pip install -e ".[easyocr]"
```

### CLI

**Not Yet Implemented.** EZRA does not have a CLI entry point. All usage is programmatic.

### Programmatic Usage (Implemented)

#### Basic perception with EPB emission

```python
from pathlib import Path
from ezra.plugins.registry import get_plugin
from ezra.core.engine import EzraEngine

plugin = get_plugin("easyocr", device="cpu", languages=["en"])
plugin.load("")

engine = EzraEngine(plugin)
result = engine.process_image(
    image,
    emit_epb=True,
    epb_output_dir=Path("./output/epb"),
)
# result == {"detections": [{"text": "...", "confidence": 0.99, "bbox": [...]}]}
```

#### Direct EPB bundle construction (without engine)

```python
from pathlib import Path
from ezra.epb import build_epb_bundle, write_epb_bundle

bundle = build_epb_bundle(
    detections=[{"text": "Hello", "confidence": 0.99, "bbox": [10.0, 20.0, 50.0, 40.0]}],
    plugin_name="easyocr",
    plugin_version="1.7.2",
    input_metadata={"width": 640, "height": 480, "channels": 3},
)

write_epb_bundle(bundle, Path("./output/epb"))
```

#### Plugin resolution from config

```python
from ezra.plugins.registry import get_plugin_from_config

config = {
    "name": "easyocr",
    "kwargs": {"device": "cpu", "languages": ["en"]},
}
plugin = get_plugin_from_config(config)
```

#### EPB bundle certification (stdlib-only, no runtime imports)

```python
from ezra.epb_tools.epb_certify import certify

result = certify(Path("./output/epb"))
# result is a dict with certification status
```

#### Zone registry with EPB emission

```python
from ezra.zones.schema import ZoneSchema, BBoxNorm, ZonePersistence
from ezra.zones.registry import ZoneRegistry
from ezra.epb import build_epb_bundle, write_epb_bundle

registry = ZoneRegistry()
registry.register(ZoneSchema(
    id="board",
    kind="game_region",
    channel_index=0,
    bbox_norm=BBoxNorm(x_min=0.1, y_min=0.1, x_max=0.9, y_max=0.9),
    persistence=ZonePersistence(sticky=True),
))
registry.freeze()

bundle = build_epb_bundle(
    detections=[],
    plugin_name="tesseract",
    plugin_version="stub-0.0.1",
    input_metadata={"width": 640, "height": 480, "channels": 3},
)

write_epb_bundle(bundle, Path("./output/epb"), zone_registry=registry)
```

### Baseline Capture Tool

EZRA includes a baseline capture tool for golden output comparison:

```bash
python -m ezra.tools.capture_easyocr_baseline
```

This captures known-good EasyOCR outputs on synthetic fixtures for regression testing. Requires EasyOCR extras.

---

## 10. Debugging Guide

### Exception Hierarchy

All EZRA exceptions inherit from `EzraError` (`src/ezra/errors.py`). The hierarchy uses dual inheritance (EZRA type + stdlib type) for backward compatibility:

| Exception | Parent(s) | Cause |
|-----------|-----------|-------|
| `EzraError` | `Exception` | Root of all EZRA errors |
| `PluginError` | `EzraError` | Base for plugin failures |
| `PluginRegistryError` | `PluginError`, `TypeError` | Malformed registry entry |
| `PluginResolutionError` | `PluginError`, `ValueError` | Unknown plugin name |
| `PluginExecutionError` | `PluginError`, `RuntimeError` | Inference or model load failure |
| `EPBError` | `EzraError` | Base for EPB failures |
| `EPBValidationError` | `EPBError`, `ValueError` | JSON Schema validation failure |
| `EPBHashError` | `EPBError`, `ValueError` | Hash mismatch or verification failure |
| `EPBCanonicalError` | `EPBError`, `ValueError` | NaN or Infinity in bundle data |
| `ZoneSchemaError` | `EzraError`, `ValueError` | Zone schema or registry constraint violation |
| `DeterminismError` | `EzraError`, `RuntimeError` | Determinism check failure |

### Common Failure Modes

| Symptom | Likely Cause | Resolution |
|---------|-------------|------------|
| `PluginResolutionError: Unknown plugin` | Plugin name not in `_PLUGIN_REGISTRY` | Check `list_plugins()` for available names |
| `ImportError: EasyOCR is not installed` | Missing optional dependency | `pip install -e ".[easyocr]"` |
| `PluginExecutionError: Model not loaded` | `plugin.load()` was not called before `infer()` | Call `plugin.load(artifact_path)` first |
| `EPBValidationError` | Bundle component fails JSON Schema check | Inspect the specific schema error message; ensure detections follow the canonical format |
| `EPBHashError` | Hash mismatch after write | Possible file system issue or manual tampering; re-emit bundle |
| `EPBCanonicalError: NaN values` | Float NaN in detection data | Ensure plugin output contains only finite float values |
| `ZoneSchemaError: registry is frozen` | Attempted registration after `registry.freeze()` | Register all zones before calling `freeze()` |
| `ZoneSchemaError: Duplicate zone id` | Two zones share the same `id` | Use unique zone identifiers |
| `ZoneSchemaError: Duplicate channel index` | Two zones share the same `channel_index` | Use unique channel indices |

### How to Verify Bundle Integrity

```python
from ezra.epb.hash_verifier import verify_epb_bundle

verify_epb_bundle(Path("./output/epb"))
# Raises EPBHashError if any hash mismatch is detected
```

### How to Validate Plugin Registry

```python
from ezra.plugins.registry import validate_registry

validate_registry()
# Raises PluginRegistryError or PluginExecutionError if any entry is invalid
```

---

## 11. Extension Guide

### Adding a New Plugin

1. Create `src/ezra/plugins/{name}_plugin.py` implementing `OCRPlugin`:

```python
from ezra.plugins.interface import OCRPlugin
from typing import Any

class MyPlugin(OCRPlugin):
    def load(self, artifact_path: str) -> None:
        # Load model from artifact_path
        ...

    def infer(self, image: Any) -> dict[str, Any]:
        # Return {"detections": [{"text": ..., "confidence": ..., "bbox": [...]}]}
        ...

    def describe_capabilities(self) -> dict[str, Any]:
        return {
            "version": "1.0.0",
            "plugin_name": "MyPlugin",
            "supported_formats": ["numpy array"],
            "input_requirements": {},
            "output_schema": {"detections": [{"text": "str", "confidence": "float", "bbox": "list[float]"}]},
        }
```

2. Register in `src/ezra/plugins/registry.py`:

```python
_PLUGIN_REGISTRY: dict[str, str] = {
    "easyocr": "ezra.plugins.easyocr_plugin:EasyOCRPlugin",
    "tesseract": "ezra.plugins.tesseract_plugin:TesseractPlugin",
    "myplugin": "ezra.plugins.myplugin_plugin:MyPlugin",  # NEW
}
```

3. Add tests in `tests/`

4. Ensure `validate_registry()` passes

### Adding Zones

1. Create `ZoneSchema` instances with unique `id` and `channel_index`
2. Register in a `ZoneRegistry`
3. Call `registry.freeze()` before use
4. Pass `zone_registry` to `write_epb_bundle()` for `zones.json` emission

### What Must NOT Be Changed (v1.0.0 Frozen Surface)

These are frozen and must not be modified without a new major milestone:

- `OCRPlugin` interface methods (`load`, `infer`, `describe_capabilities`)
- EPB v1.0.0 directory structure and file names
- Canonical JSON rules (encoding, key ordering, float precision, forbidden values)
- SHA256 hashing algorithm and bundle hash computation rules
- `epb_version` string (`"1.0.0"`)
- Zone schema contract (6dp float precision, channel uniqueness)
- Plugin registry resolution semantics (exact name match, lazy import)

---

## 12. v1 Guarantees (Frozen Surface)

### What Is Frozen

| Surface | Status | Reference |
|---------|--------|-----------|
| `OCRPlugin` ABC | Frozen | `src/ezra/plugins/interface.py` |
| EPB v1.0.0 schema | Frozen | `docs/specs/epb_v1/EPB_V1_SPEC.md` |
| Canonical JSON rules | Frozen | `src/ezra/epb/canonical.py` |
| SHA256 hashing rules | Frozen | `src/ezra/epb/hasher.py` |
| Bundle hash computation | Frozen | EPB spec Section 4.3 |
| Zone schema contract | Frozen | `src/ezra/zones/schema.py` |
| Exception hierarchy | Frozen | `src/ezra/errors.py` |
| Public surface snapshot | Frozen | `tests/test_public_surface_freeze.py` |

### What Requires a Version Bump

| Change Type | Required Bump |
|-------------|--------------|
| New optional EPB file | Minor (v1.1+) |
| New optional plugin capability | Minor (v1.1+) |
| New zone schema field | Minor (v1.1+) |
| Remove/rename required EPB file | Major (v2.0+) |
| Change `OCRPlugin` method signatures | Major (v2.0+) |
| Change canonicalization rules | Major (v2.0+) |
| Change hashing algorithm | Major (v2.0+) |
| Change `epb_version` string | Major (v2.0+) |

### Compatibility

- **Backward compatible:** existing plugins, bundles, and zone registries continue to work across v1.x releases.
- **Forward compatible:** additive changes (new optional fields, new plugins) are allowed in minor versions.
- **Breaking changes:** require a major version bump, a new milestone, and explicit audit justification.

---

## Appendix A: Repository Structure

This structure reflects the repository at v1.0.0 and may evolve in future versions.

```text
src/ezra/
  __init__.py                  ← Package root; __version__ = "1.0.0"
  types.py                     ← Canonical types (ImageInput, OCRResult, ModelArtifactMetadata)
  errors.py                    ← Typed exception hierarchy
  core/
    engine.py                  ← EzraEngine (minimal stub with EPB emission)
  plugins/
    interface.py               ← OCRPlugin ABC
    registry.py                ← Static plugin registry with lazy resolution
    easyocr_plugin.py          ← EasyOCR plugin (functional)
    easyocr_adapter.py         ← EasyOCR framework isolation layer
    tesseract_plugin.py        ← Tesseract plugin (stub)
  epb/
    builder.py                 ← In-memory EPB bundle construction
    writer.py                  ← EPB bundle disk writer
    canonical.py               ← Canonical JSON serialization (8dp)
    hasher.py                  ← SHA256 hashing (per-file + bundle)
    hash_verifier.py           ← Post-write hash verification
    schema_validator.py        ← JSON Schema validation
    zone_adapter.py            ← Zone registry → EPB zones.json adapter
  zones/
    schema.py                  ← ZoneSchema, BBoxNorm, ZonePersistence dataclasses
    registry.py                ← ZoneRegistry with freeze semantics
    validator.py               ← Zone schema validation
    serialize.py               ← Zone serialization utilities
    export.py                  ← Zone export utilities
    projector.py               ← Zone-scoped state projection
  epb_tools/
    epb_certify.py             ← Stdlib-only bundle certification
    epb_verify.py              ← Ed25519 signature verification
    epb_generate_cert_metadata.py ← Certification metadata envelope generator
  baseline/
    canonicalize.py            ← Baseline canonicalization (6dp, for golden outputs)
    parity.py                  ← Parity comparison utilities
  tools/
    capture_easyocr_baseline.py ← Golden baseline capture tool
    epb_sign.py                ← Ed25519 bundle signing
    epb_verify.py              ← Legacy wrapper (deprecated, use epb_tools)
    epb_certify.py             ← Legacy wrapper (deprecated, use epb_tools)
    epb_generate_cert_metadata.py ← Legacy wrapper (deprecated, use epb_tools)

tests/                         ← Unit + contract tests (PR-gated)
docs/
  ezra.md                     ← Governance ledger + milestone record
  ezra_operating_manual_v1.md  ← This document
  VISION.md                   ← Architectural intent + non-goals
  specs/epb_v1/               ← EPB v1.0.0 spec + JSON schemas
  milestones/                  ← Milestone proof packs
  baselines/                   ← Golden outputs + capture manifests
```

## Appendix B: Quick Reference Commands

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Install EasyOCR plugin (optional)
pip install -e ".[easyocr]"

# Run linter
ruff check .
ruff format --check .

# Run type checker
mypy src

# Run tests
pytest

# Run tests with coverage
pytest --cov=src/ezra

# Run parity tests (requires EasyOCR)
EZRA_RUN_PARITY=1 pytest -m parity

# Run integration tests
EZRA_RUN_INTEGRATION=1 pytest -m integration

# Capture EasyOCR baseline
python -m ezra.tools.capture_easyocr_baseline

# Verify distribution artifacts
python scripts/verify_distribution.py --tag latest
```
