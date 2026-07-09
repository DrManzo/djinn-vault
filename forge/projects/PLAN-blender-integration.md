---
title: Blender Integration — Typhon's Forge + Djinn
created: 2026-06-18
status: in_progress
owner: Claude (architecture) | Marcus (addon) | Salomon (build)
tags: [djinn, blender, typhons-forge, pipeline, automation]
---

# Blender Integration — Master Build List

Blender 5.1.2 (snap) already installed on Salomon. Zero-install path.

Two tracks running in parallel:
- **Track A — Addon** (Marcus builds): Interactive Blender UI panel for Javier's manual workflow
- **Track B — Headless CLI** (Claude specs, Salomon builds): Automated djinn pipeline tools that call `blender --background --python`

These share the same bpy operations. The addon is the UI surface; the headless scripts are the automation layer.

---

## Track A — Typhon's Forge Blender Addon

**Repo path:** `blender_addon/typhons_forge/`
**Marcus owns this track.**

### Phase A-1 — Core Addon (Marcus scoped, ready to build)

- [ ] `__init__.py` — addon metadata (`"blender": (5, 0, 0)` for 5.1.2 compat), register/unregister
- [ ] `operators/boolean_cut.py` — boolean difference + clearance offset (shrink_fatten on cutter)
- [ ] `operators/push_back.py` — translate along face normals, axis lock support
- [ ] `operators/smooth_seam.py` — remove doubles + fix normals + bevel modifier + Smooth by Angle
- [ ] `panels/main_panel.py` — N-panel sidebar, Typhon's Forge tab
- [ ] `utils/mesh_utils.py` — shared helpers: manifold check, face count, bounding box, wall thickness probe

### Phase A-2 — Extended Operators

- [ ] `operators/batch_export.py` — export selected objects as individual STLs, auto-name from object name, drop to `~/printer-files/queue/`
- [ ] `operators/bore_prep.py` — UI wrapper for bore workflow: set bore diameter, depth, center XY — calls same logic as `djinn-bore-core` but interactively in Blender
- [ ] `operators/maker_mark.py` — load TF anvil STL, position on model bottom, boolean subtract — mirrors `djinn-model-mark` logic
- [ ] `operators/render_preview.py` — one-click EEVEE render to file using branded scene template

### Phase A-3 — Polish

- [ ] Preferences panel: queue path, maker mark STL path, default clearance value
- [ ] Error messaging: missing selection, non-manifold input, disk full on export
- [ ] README.md for the addon (installation, shortcut list)

---

## Track B — Headless CLI (djinn pipeline)

**Key fact:** Snap Blender has its own bundled Python. Call as:
```
blender --background --python /path/to/script.py -- [args]
```
Arguments after `--` are passed to the script via `sys.argv`.
Do NOT use `pip install bpy` — that's a different Python env.

### Phase B-1 — djinn-blender-repair

**File:** `~/.local/bin/djinn-blender-repair`
**Purpose:** Clean incoming Meshy AI sculpts before they hit djinn-bore-core.

```
djinn-blender-repair <input.stl> [--out output.stl] [--report]
```

Operations (in order):
1. Load STL into Blender headless
2. Remove doubles (threshold 0.001)
3. Recalculate normals (make_consistent, inside=False)
4. Fill holes (fill_holes, sides=4)
5. Manifold check — report remaining issues
6. Export clean STL
7. Print summary: face count before/after, issues fixed, issues remaining

Pipeline hook: runs automatically when `djinn-bore-core` receives a fresh Meshy file (detect by `Meshy_*` filename pattern).

- [ ] Write headless bpy script (`blender_scripts/repair.py` in vault)
- [ ] Write `djinn-blender-repair` wrapper (handles snap path, args, 120s timeout)
- [ ] Wire into `djinn-bore-core` pre-flight: if input matches `Meshy_*`, auto-repair first
- [ ] COMMS entry on repair: faces removed, issues fixed

### Phase B-2 — djinn-blender-render

**File:** `~/.local/bin/djinn-blender-render`
**Purpose:** Product render from STL → `cover.jpg` for media pipeline.

```
djinn-blender-render <input.stl> [--out cover.jpg] [--brand typhon|terp-tribe] [--engine eevee|cycles] [--size 1080]
```

Operations:
1. Load branded scene template (`.blend` file with lighting rig, background, camera)
2. Import STL, center it, auto-scale to fit frame
3. Apply brand material (Typhon: dark metallic; Terp: brand colors from config)
4. Render to `--out` path
5. EEVEE-Next default (~5s), Cycles optional (60-120s, GPU if available)

Brand scene templates:
- `blender_scenes/typhon-forge.blend` — dark studio, 3-point light, black background
- `blender_scenes/terp-tribe.blend` — brand colors, lighter aesthetic

- [ ] Design and save Typhon's Forge scene template in Blender
- [ ] Design Terp Tribe scene template
- [ ] Write headless bpy script (`blender_scripts/render.py`)
- [ ] Write `djinn-blender-render` wrapper
- [ ] Wire render output into `djinn-media-ingest`: auto-render `cover.jpg` after ingest if STL source present
- [ ] Telegram notification: "🖼 Render ready — {job_slug}"

### Phase B-3 — djinn-blender-qa

**File:** `~/.local/bin/djinn-blender-qa`
**Purpose:** Headless quality check before slicing.

```
djinn-blender-qa <input.stl> [--min-wall 1.2] [--report]
```

Checks:
- Manifold (watertight)
- Min wall thickness at sampling points (1.2mm ASA, 0.8mm PLA)
- Overhangs > 45° (flag only)
- Face count > 500K (flag for decimation)
- Bounding box vs Ender-3 V3 Plus build volume (300×300×300mm)

Output: JSON report + human summary. Exit 1 on critical failures.

- [ ] Write headless bpy script (`blender_scripts/qa_check.py`)
- [ ] Write `djinn-blender-qa` wrapper
- [ ] Wire into `djinn-print-consult` pre-flight — QA results feed into Telegram consult message

---

## Phase C — Full Pipeline Integration

Once B-1 and B-2 are stable:

- [ ] `djinn-bore-core` → auto-calls `djinn-blender-repair` on Meshy files
- [ ] `djinn-media-ingest` → auto-calls `djinn-blender-render`, places output as `cover.jpg`
- [ ] `djinn-print-consult` → auto-calls `djinn-blender-qa`, includes results in consult report
- [ ] Telegram gateway: `render {project_id}` → on-demand render
- [ ] Telegram gateway: `qa {job_id}` → on-demand QA check

---

## Phase D — Advanced (after C stable)

- [ ] Per-brand turntable GIF: 8-frame rotation, 800×800, alongside `cover.jpg`
- [ ] Multi-view render: front, 3/4, detail shot — 3 frames per STL, auto-named
- [ ] HDRI background variants (studio, outdoor, dark forge aesthetic)
- [ ] Auto-UV + texture bake for branded products

---

## Build Order

```
A-1   Marcus — addon core (interactive workflow)
B-1   Salomon — djinn-blender-repair  ← highest pipeline value, unblocks Kraken + Meshy flow
B-2   Salomon — djinn-blender-render  ← feeds media pipeline directly
A-2   Marcus — extended operators
B-3   Salomon — djinn-blender-qa
C     Wire everything together
A-3   Addon polish
D     Advanced features
```

---

## Technical Notes

- Snap Blender path: `/snap/bin/blender`
- Headless call: `blender --background --python script.py -- arg1 arg2`
- Scene templates: `blender/scenes/` in typhons-forge repo
- Addon location: `blender/addon/typhons_forge/` in typhons-forge repo
- Addon install: symlink to `~/.config/blender/5.1/scripts/addons/` (handled by `install-addons.sh`)
- Render engine in Blender 5.1.2 snap: `'BLENDER_EEVEE'` (NOT `BLENDER_EEVEE_NEXT` — invalid in this build)
- All headless bpy scripts must be self-contained — no external pip deps inside Blender's Python env

Verify snap Python version:
```bash
blender --background --python-expr "import sys; print(sys.version)" 2>/dev/null | grep -E "^\d"
```

---

## A-2 Extended Operators — Feature Classification (2026-06-19)

Architecture review produced the following classification for all new tools.

### System-of-record by feature

| Feature | Owner | Rationale |
|---|---|---|
| Non-manifold detector/highlighter | Addon (TASK-086) | Viewport diagnostic — user needs to see what's wrong |
| Auto-merge by distance | Addon + repair.py (TASK-087) | Available both interactively and headlessly |
| Auto-fill holes / remove loose | Addon + repair.py (TASK-087) | Same as above — both surfaces need it |
| Auto-center + drop to bed | Addon (TASK-088) | Geometry edit with visual feedback |
| Bounding box + weight estimator | Addon panel (TASK-089) | Live feedback during modeling; provisional only |
| Rename/version stamp | Addon (TASK-090) | Workflow convenience; no headless value |
| Wall thickness QA | Addon + qa_check.py (TASK-091) | Visual flag in addon, enforced pass/fail headlessly |
| Decimate to target | Addon (Tier 2) | Model-specific; needs user judgment on quality |
| Hollow with wall thickness | Addon (Tier 2) | Geometry authoring; can damage model if blind |
| Auto-scale to build volume | Addon (Tier 2) | Print-prep geometry edit with visual confirmation |
| Maker's mark auto-placer | Addon (Tier 2) | Needs face-detection and brand-scene logic |
| Auto-orient for min overhang | djinn utility (Tier 3) | Optimization problem, not a mesh edit |
| Real cost/weight from slicer | PrusaSlicer output (Tier 3) | Slicer is authoritative; Blender estimates only |
| Raft/base strategy | Slicer (Tier 3) | Never model into STL geometry unless required |

### QA severity model (TASK-091)

Three classes in `qa_check.py`:

| Class | Trigger | Pipeline action |
|---|---|---|
| `critical` | Non-manifold, build vol exceeded, zero volume | Exit 1 — blocks slice |
| `warning` | Thin walls, high overhang %, face count >500k, trapped volume | Exit 0 — user decides |
| `info` | Dims, volume, face count, weight estimate | Exit 0 — always included |

Blender weight estimates are provisional. PrusaSlicer output (filament used × density × price) is authoritative for production pricing.

### Design constraints

**Operators that can damage geometry need a safe default:**
- Hollow: preview-first, never auto-commit
- Decimate: warn if bore/fitment surfaces detected, show reduction ratio before commit
- Auto-fill holes: flag intentional openings (if hole > 5mm diameter, warn before filling)
- Maker mark: dry-run pass checks bottom-face thickness before engraving

**Object metadata (future):** Reserve `obj["tf_source"]`, `obj["tf_material"]`, `obj["tf_printer"]`, `obj["tf_brand"]` as custom properties for smarter operator behavior. Not blocking A-2, but operators should write these if they know the value.

**Report provenance:** Every automated repair step (headless or operator) should log what changed: verts merged, holes filled, loose removed, scale adjusted. Treat reporting as part of the feature.

### Implementation order

**Tier 1 — now (TASK-086 to TASK-091):**
Non-manifold check → mesh cleanup → align to bed → mesh info panel → rename stamp → qa_check.py

**Tier 2 — after Tier 1 validates:**
Decimate to target → hollow with wall thickness → auto-scale → maker's mark auto-placer

**Tier 3 — owned outside addon:**
Auto-orient (djinn utility), cost from slicer output, raft recommendation

---

*— Claude, 2026-06-18 | Updated 2026-06-19 — A-2 feature classification and QA severity model added*
