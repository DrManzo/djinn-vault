---
title: Bug Report — djinn-model-mark Skips Marking Based on a Filename Heuristic, Not Real Geometry
agent: Claude
date: 2026-07-16
tags: [djinn, bug, forge/tools/djinn-model-mark]
related: [[bugs]] | [[build-log]] | [[2026-07-14_bug-djinn-bore-core-has-two-independent-silent-auto-scale-triggers-that-can-massively-corrupt-output-geometry-with-no-warning]]
---

# Bug Report — djinn-model-mark Filename Heuristic False-Positive Skip

**Date:** 2026-07-16
**System:** `~/.local/bin/djinn-model-mark`
**Severity:** Medium
**Status:** Fixed (workaround applied at call site; source not patched)

---

## Symptom

Ran `djinn-model-mark` on a freshly bore-core'd Backpack Boyz piece (`backpack_small_bored.stl`, produced with `--no-mark` explicitly passed to `djinn-bore-core`). Instead of applying the mark, it printed:

```
⚠  bore mark already applied by djinn-bore-core — outside bottom mark skipped
The maker's mark is engraved on the bore floor, visible when loading the Proxy Core.
```

...and exited 0 with **no output file written at all**. The piece was left with no maker's mark of any kind.

---

## Root Cause

```python
# Guard: bored files already have the mark on the bore floor
if Path(args.stl).stem.endswith("_bored"):
    print(f"  ⚠  bore mark already applied by djinn-bore-core — outside bottom mark skipped")
    print(f"  The maker's mark is engraved on the bore floor, visible when loading the Proxy Core.")
    sys.exit(0)
```

This guard checks the **input filename string**, not the mesh geometry and not whether `--no-mark` was actually passed to the upstream `djinn-bore-core` call. My input happened to be named `backpack_small_bored.stl` (my own working filename, ending in `_bored`) — the guard fired regardless of the fact that `djinn-bore-core`'s own JSON output for that run reported `"mark_size": 0.0`, confirming no mark was actually applied.

Any file whose name happens to end in `_bored` — whether or not it actually has a mark — silently gets no mark and no output file, with only an easy-to-miss warning line as the only signal something didn't happen.

---

## Fix Applied (workaround, not a source patch)

Renamed the input file to not end in `_bored` before calling `djinn-model-mark` (`backpack_small_bored.stl` → `backpack_small_prebored.stl`), which let the real marking logic run. Verified the result: watertight, correct mark geometry (0.0126 cm³ removed, matching the standard 15mm/0.5mm-deep mark), `Z_min` shifted from 0 to 0.0244mm exactly as expected for a bottom-face recess.

**Source itself not patched** — this report documents the defect for the next person who hits it; the actual fix (check `djinn-bore-core`'s own mark_size output or the mesh itself, not the caller's filename string) is still open.

---

## Rule / Lesson

**Never gate a tool's core behavior on a caller-supplied filename convention.** The correct signal here already existed one layer up — `djinn-bore-core`'s own JSON output includes `mark_size`, which is the ground truth for whether a mark was applied. A filename ending in `_bored` says nothing reliable about whether `--no-mark` was used on that specific run. Any tool in this chain that needs to know "was X already done to this mesh" should check the mesh or the upstream tool's own report, not infer it from a string the caller chose for unrelated reasons (in this case, my own working-file naming during a debugging session).

---

## What's Next

- [ ] Patch `djinn-model-mark`'s guard to check actual mesh state (e.g., presence of a recess at the expected bore-floor mark location) or accept an explicit `--already-marked` flag from the caller, instead of sniffing the filename
- [ ] Audit other tools in this forge pipeline for the same filename-as-state-signal pattern — this is the second tool this week (after `djinn-bore-core`'s own auto-scale issues) where a print-quality tool's control flow depended on something other than the actual mesh

---

*— Claude, 2026-07-16*
