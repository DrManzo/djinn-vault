---
title: Bug — djinn-model-mark hard-fails when config mark STL is unmounted
agent: Claude
date: 2026-10-01
tags: [djinn, bug, forge, makers-mark]
---

# Bug — djinn-model-mark hard-fails when config mark STL is unmounted

**System:** `~/.local/bin/djinn-model-mark` (Salomon) · **Severity:** low · **Status:** open (workaround used)

## Symptom
Both `~/.config/forge/makers-mark.json` (read by djinn-model-mark) and `~/.config/djinn/makers-mark.json` point at `/run/media/drmanzo/alexandria/.../tf_anvil_traced_20mm.stl`. Alexandria isn't mounted, so the tool exits `Error: mark STL not found` despite shipping a built-in TF anvil cutter. The memory-note path `~/printer-files/library/tf_anvil_traced_15mm.stl` also doesn't exist.

## Root cause
Config `path` takes precedence; missing file is a hard exit with no fallback to `build_cutter()`.

## Workaround
Imported the module and called `build_cutter(15, 0.5)` + `apply_mark()` directly.

## Fix (proposed)
Warn and fall back to built-in geometry on missing STL, or copy the mark STL locally (`~/.config/djinn/`) and repoint both configs.

## Lesson
Tools depending on a removable drive need a local fallback for required assets.

*— Claude*
