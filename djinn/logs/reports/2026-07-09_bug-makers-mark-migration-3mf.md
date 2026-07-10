---
title: Bug Report — djinn-model-mark Broken by Storage Migration + 3mf Input Crash
agent: Claude
date: 2026-07-09
tags: [djinn, bug, makers-mark, trimesh, migration, forge]
related: [[2026-07-09_alexandria-setup-storage-migration-cleanup]] | [[build-log]] | [[bugs]]
---

# Bug Report — djinn-model-mark Broken by Storage Migration + 3mf Input Crash

**Date:** 2026-07-09
**System:** `djinn-model-mark` (`~/.local/bin/djinn-model-mark`)
**Severity:** Medium
**Status:** Fixed

---

## What Happened

Javier asked for the maker's mark stamped onto `puffco-710_fixed.3mf` (from `~/Downloads/`). Running `djinn-model-mark` against it failed immediately:

```
Error: mark STL not found: /home/drmanzo/printer-files/library/originals/logos/tf_anvil_traced_15mm.stl
```

---

## Root Cause 1 — Stale Path from Storage Migration

`~/.config/forge/makers-mark.json` pointed at `/home/drmanzo/printer-files/library/originals/logos/tf_anvil_traced_15mm.stl` — a path on Salomon's local disk. The entire `printer-files` tree was moved to the Alexandria SSD during the 2026-07-09 storage migration ([[2026-07-09_alexandria-setup-storage-migration-cleanup]]) as part of clearing ~12GB off Salomon. The config file referencing this asset was never updated, so every `djinn-model-mark` call has been silently broken since that migration.

**Fix:** Repointed `makers-mark.json` to `/run/media/drmanzo/alexandria/printer-files/library/originals/logos/tf_anvil_traced_20mm.stl` (see Root Cause 2 for why 20mm, not 15mm).

---

## Root Cause 2 — Corrupted 15mm Mark Source (unrelated to migration)

After fixing the path, the tool crashed differently:

```
TypeError: 'NoneType' object is not subscriptable
  (mark.bounds[1][0] — mark.bounds was None)
```

`tf_anvil_traced_15mm.stl` loads as an empty `trimesh.Scene` with no geometry. Inspecting the file header shows it's missing the standard 80-byte binary-STL header — the first bytes are already meaningful float data, not padding. The file is corrupted (likely from an earlier incomplete write or transfer, unrelated to the storage migration — its mtime is 2026-07-03).

The sibling `tf_anvil_traced_20mm.stl` in the same directory loads correctly.

**Fix:** Since `djinn-model-mark` always rescales the external mark mesh to `size_mm` (config default: 15mm) based on its X-extent, sourcing from the 20mm file and letting the tool scale it down produces an identical result to what the 15mm file would have given if it weren't corrupted. Repointed config to the 20mm file rather than trying to regenerate the 15mm one.

---

## Root Cause 3 — Tool Doesn't Handle 3mf (Scene) Input

Even with both of the above fixed, running the tool directly on the `.3mf` crashed a third way:

```
AttributeError: 'Scene' object has no attribute 'is_winding_consistent'
  (inside trimesh.repair.fix_normals, called from apply_mark)
```

`~/.local/bin/djinn-model-mark` line 279 calls `trimesh.load(args.stl, process=True)` with no `force='mesh'`. A `.stl` always loads as a bare `Trimesh`, but a `.3mf` (or any multi-object container format) loads as a `trimesh.Scene`. The early `mesh.bounds` access on line 280 works fine (Scene has an aggregate `.bounds`), so the size printout looked correct and the failure only surfaced deep inside the boolean/repair step — misleadingly far from the actual cause.

**Fix:** Patched the tool itself (not just worked around):

```python
mesh  = trimesh.load(args.stl, process=True)
if isinstance(mesh, trimesh.Scene):
    mesh = mesh.dump(concatenate=True) if len(mesh.geometry) > 1 else next(iter(mesh.geometry.values()))
b     = mesh.bounds
```

Verified: `djinn-model-mark puffco-710_fixed.3mf --output ...` now runs end-to-end with no manual STL-extraction step, producing a watertight single-component result identical (geometrically) to the manual-extraction workaround tried first.

---

## Rule / Lesson

**A storage migration that moves asset files must grep every config for the old path before calling itself done.** `makers-mark.json` was the kind of small, easy-to-miss reference that a bulk `mv`/`rsync` migration silently breaks. Any future large-scale file relocation should include a repo-wide/config-wide grep for the old path prefix as a checklist item, not just moving the files and confirming disk space freed.

**`trimesh.load()` without `force='mesh'` is a landmine for any tool that's only ever been tested against `.stl` input.** If a script assumes a bare `Trimesh` but might receive a `.3mf`/`.obj`/other container format, either pass `force='mesh'` at load time or explicitly unwrap `Scene` objects immediately after loading — don't let it fail three call-frames deep where the error message no longer points at the real cause.

---

## Files Modified

```
~/.config/forge/makers-mark.json     ← path repointed to Alexandria + working 20mm source
~/.local/bin/djinn-model-mark          ← Scene-unwrap patch added after trimesh.load()
```

---

## What's Next

- [ ] Regenerate or re-trace `tf_anvil_traced_15mm.stl` properly if a true 15mm-native source is ever needed (not urgent — 20mm rescale is functionally identical)
- [ ] Grep the rest of `~/.config/forge/*.json` and any other config referencing pre-migration `printer-files` paths for similar stale references
- [ ] Consider a `--force-mesh` default in any other djinn forge script that calls `trimesh.load()` on user-supplied model files

---

*— Claude, 2026-07-09*
