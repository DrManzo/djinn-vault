---
title: Session Report — Blender Integration into Djinn + Typhon's Forge
agent: Claude
date: 2026-06-18
tags: [djinn, report, blender, typhons-forge, headless, cli]
related: [[build-log]] | [[decision-log]] | [[TASK-080]] | [[PLAN-blender-integration]]
---

# Session Report — Blender Integration into Djinn + Typhon's Forge

**Date:** 2026-06-18
**Agent:** Claude
**Session type:** Architecture + Build
**Trigger:** Javier requested Blender be added as automation layer to Djinn and Typhon's Forge

---

## Summary

Blender 5.1.2 (already snap-installed on Salomon) was integrated as a headless studio tool into the Typhon's Forge pipeline. Marcus built the addon and headless scripts; Claude wrote specs and wired the CLI wrappers. Two tools — `djinn-blender-repair` and `djinn-blender-render` — are now live, tested, and passing on the Kraken pipe STL. Five bugs were found and fixed across Marcus's scripts and the initial wrappers.

---

## What Was Built or Changed

- **Blender library scaffold** in `~/typhons-forge/blender/` — addon, scripts, scenes, docs directories
- **Marcus-built addon** `typhons_forge/` — boolean cut, push back, smooth seam, batch export (A-2 stub), bore prep (A-2 stub), maker mark (A-2 stub), render preview (A-2 stub)
- **Marcus-built headless scripts** — `repair.py`, `render.py`, `qa_check.py`
- **`djinn-blender-repair`** at `~/.local/bin/` — wraps repair.py; always passes `--report <path>`; 120s timeout
- **`djinn-blender-render`** at `~/.local/bin/` — wraps render.py; auto-detects JPEG/PNG from extension; 300s timeout
- **TASK-080** — Kraken pipe diagnostic confirmed print-ready (marginal 1.31mm wall at Z=10mm)
- **TASK-081 through 084** written to QUEUE.md for Salomon (Phase C pipeline wiring)
- **TASK-085** written to QUEUE.md — fix gateway `build TASK-NNN` command to be QUEUE-aware

---

## Technical Decisions

**Headless Blender via snap** — Do not install `bpy` via pip. Snap Blender bundles its own Python. All scripts run as `blender --background --python script.py -- [args]`.

**`BLENDER_EEVEE` not `BLENDER_EEVEE_NEXT`** — Snap Blender 5.1.2 on Salomon exposes the legacy engine name `BLENDER_EEVEE` despite being version 5.x. `BLENDER_EEVEE_NEXT` raises enum error at runtime. Verified by hitting the error and checking the error message's valid enum list.

**`trigger: manual` for TASK-081–084** — Build tasks require Salomon's opencode agent to read specs and build Python tools. The queue runner cron only handles shell command tasks; it can't run opencode. Manual trigger is correct. Side effect: `djinn-queue-runner` skips them, which surprised Javier.

**`os.makedirs` guard on empty dirname** — `os.path.dirname("/tmp/file.stl")` returns `"/tmp"` (fine) but `os.path.dirname("file.stl")` returns `""` (empty), and `os.makedirs("", exist_ok=True)` raises FileNotFoundError. Added null check in repair.py.

**Format detection from extension** — render.py hardcoded `file_format = 'PNG'`. Changed to detect JPEG vs PNG from `--out` file extension so callers get what they asked for.

---

## Files Created or Modified

```
~/.local/bin/djinn-blender-repair          ← new: repair wrapper (TASK-081)
~/.local/bin/djinn-blender-render          ← new: render wrapper (TASK-082)
~/typhons-forge/blender/scripts/repair.py  ← fixed: os.makedirs empty dirname guard
~/typhons-forge/blender/scripts/render.py  ← fixed: BLENDER_EEVEE, JPEG/PNG detection
~/typhons-forge/blender/README.md          ← new: master studio vision doc
~/typhons-forge/blender/scenes/README.md   ← new: brand scene authoring guide
~/typhons-forge/blender/docs/README.md     ← new: docs index (Marcus fills these in)
~/Obsidian/djinn/communications/QUEUE.md   ← appended: TASK-081–085
~/Obsidian/djinn/projects/PLAN-blender-integration.md  ← in worktree only, not yet in vault
```

---

## Tests & Validation

```
djinn-blender-repair ~/Downloads/kraken-typhons-forge/Kraken_pipe.stl
→ 1 duplicate vertex removed
→ bad edges before=0 after=0, manifold=true
→ Kraken_pipe_repaired.stl written
✓ PASS

djinn-blender-render ~/Downloads/kraken-typhons-forge/Kraken_pipe.stl --out /tmp/kraken_cover.jpg
→ 4.16s EEVEE render (fallback 3-point rig — no brand .blend yet)
→ /tmp/kraken_cover.jpg 38KB
✓ PASS
```

---

## Known Issues / Caveats

- Brand scene `.blend` files don't exist yet — render.py falls back to generic 3-point rig. Javier needs to author `typhon-forge.blend` and `terp-tribe.blend` in Blender manually.
- TASK-083 (wire repair into djinn-bore-core) and TASK-084 (wire render into djinn-media-ingest) not yet built — Salomon needs to execute them.
- TASK-085 (gateway `build TASK-NNN` fix) not yet built — Discord gateway still hallucinating wrong task descriptions on `build` commands.
- PLAN-blender-integration.md was written to the worktree, not committed to vault main.
- Snap Blender 5.1.2 deprecation warnings for `World.use_nodes` and `Material.use_nodes` — harmless now, will break in Blender 6.0.

---

## What's Next

- [ ] Javier authors brand scenes in Blender — @Javier
- [ ] Salomon executes TASK-083 (djinn-bore-core wiring) — @Salomon
- [ ] Salomon executes TASK-084 (djinn-media-ingest wiring) — @Salomon
- [ ] Salomon executes TASK-085 (gateway build command fix) — @Salomon
- [ ] Marcus fills blender/docs/ — @Marcus
- [ ] Fix Blender 6.0 deprecation warnings before Blender 6.0 ships — @Claude

---

*— Claude, 2026-06-18*
