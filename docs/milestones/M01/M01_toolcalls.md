# M01 — Tool Calls Log

| Timestamp | Tool | Purpose | Files | Status |
|-----------|------|---------|-------|--------|
| 2026-03-20 | Write | Seed M01 milestone folder | docs/milestones/M01/ | ✅ Complete |
| 2026-03-20 | (batch) | M01 baseline: docs, T5 train/infer/validate, notebook rename, deps pins | `docs/`, `src/akk2eng/`, `kaggle/`, `tests/`, `.github/` | ✅ Complete |
| 2026-03-21 | (batch) | M01-A tools: gpu_bringup, checkpoint_hash, train CLI flags, docs | `src/akk2eng/tools/`, `pipeline/train.py`, `tests/`, `docs/` | ✅ Complete |
| 2026-03-21 | pip / code | Ran bring-up + smoke train; fixed cp1252 print, numpy<2 + torch<2.6 pins, train `data_seed` removed | `pyproject.toml`, `requirements.txt`, `train.py`, `inference.py`, `README.md`, `akk2eng.md` | ✅ Complete |
| 2026-03-21 | (batch) | M01-A remediation: hard CUDA checks, version prints, train GPU asserts + step logger, M01_run1.md | `gpu_bringup.py`, `train.py`, `README.md`, `akk2eng.md`, `M01_plan.md` | ✅ Complete |
| 2026-03-21 | (batch) | Blackwell sm_120: arch detection in gpu_bringup, README runbook, akk2eng.md notes, M01_run1.md template | `gpu_bringup.py`, `README.md`, `akk2eng.md`, `M01_run1.md` | ✅ Complete |
| 2026-03-21 | (batch) | **M01-A closeout:** run1 closeout section, governance (M01-A complete / M01-B active), release tag `v0.0.2-m01a`, `M01B_plan.md`, `M01B_toolcalls.md`, README dual-track wording | `M01_run1.md`, `akk2eng.md`, `M01_plan.md`, `README.md`, `M01B_*.md` | ✅ Complete |
| 2026-03-21 | (batch) | **M01-B:** full GPU FP32 train, checkpoint hash, `pipeline.run`; `M01_run2.md`; governance M01-B complete / M01-C active | `M01_run2.md`, `akk2eng.md`, `M01_plan.md`, `M01B_plan.md`, `M01B_toolcalls.md` | ✅ Complete |
| 2026-03-21 | (batch) | **M01-B closeout:** `M01_run2.md` closeout, tag `v0.0.3-m01b`, release table, frozen M01-B refs, `M01C_checklist.md`, README Kaggle pointer | `M01_run2.md`, `akk2eng.md`, `M01_plan.md`, `M01B_plan.md`, `M01C_checklist.md`, `README.md` | ✅ Complete |
