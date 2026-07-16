---
title: Bug Report — djinn-clerk's MARCUS_DIR hardcoded to dead pre-restructure path, would have silently misfiled real Marcus threads
agent: Claude
date: 2026-07-15
severity: medium
status: fixed
tags: [djinn, bug, djinn-clerk (~/.local/bin, not git-tracked)]
related: [[bugs]] | [[build-log]]
---

# Bug Report — djinn-clerk's MARCUS_DIR hardcoded to dead pre-restructure path, would have silently misfiled real Marcus threads

**Date:** 2026-07-15 17:42
**Agent:** Claude
**System:** djinn-clerk (~/.local/bin, not git-tracked)
**Severity:** medium
**Status:** fixed

---

## Root Cause

djinn-clerk (not git-tracked, lives in ~/.local/bin) had MARCUS_DIR hardcoded to djinn/research/marcus/threads. That path stopped existing after the 2026-07-08 vault department restructure, which moved Marcus research to ai/marcus/. The old code used mkdir(parents=True, exist_ok=True), so any perplexity-pro thread routed through route_marcus_thread() would have silently resurrected the dead directory tree and written there instead of the real ai/marcus/threads/ location Marcus/Claude actually read from — no error, no warning, just silent misfiling. Confirmed no real damage occurred yet (the dead path did not exist, meaning no perplexity-pro file had hit that code branch since the restructure), but this was a live landmine. Found while investigating why several 2026-07-15 Perplexity exports (Marcus session continuations, including one matching the already-queued TASK-104 cash-flow work) came back empty — that turned out to be a separate, unrelated issue (the Save my Chatbot browser extension capturing before page content rendered), but auditing the pipeline surfaced this real bug along the way.

---

## Symptom

No directly observed symptom yet — caught by code audit, not by a failure in the field. The dead path (`djinn/research/marcus/threads`) simply didn't exist on disk, which is itself the tell: if any perplexity-pro thread had been processed since 2026-07-08, that mkdir(parents=True, exist_ok=True) call would have quietly recreated it and Marcus/Claude would have kept reading `ai/marcus/threads/` while clerk kept writing to the resurrected dead folder next to it — a slow, silent divergence with no error to notice.

---

## Steps to Reproduce

1. Restructure the vault so a department directory a tool hardcodes a path into moves or is renamed (this already happened once, 2026-07-08: `djinn/research/marcus/` → `ai/marcus/`).
2. Don't update every tool with a hardcoded reference to the old path.
3. Route content through the stale path's write function — `mkdir(parents=True, exist_ok=True)` silently recreates the entire dead directory tree instead of erroring, and the content gets written where nothing will ever look for it again.

---

## Fix Applied

1. Corrected `MARCUS_DIR` from `djinn/research/marcus/threads` to `ai/marcus/threads` (the real, current location, confirmed to already exist and contain real thread files).
2. Added `require_department_dir(path, label)`: before writing to either `MARCUS_DIR` or `NOTES_DIR`, it checks that the path's parent (the department's own working folder — `ai/marcus/`, `i notes/`) already exists. Only the final leaf directory is auto-created (`exist_ok=True` on the leaf itself); if the department root is missing, it logs a clear error naming the stale-path failure mode explicitly and exits rather than silently creating a new directory tree in the wrong place. Applied at both call sites (`route_marcus_thread()` and the general note-writing path) — the two places djinn-clerk actually creates new destination folders.

---

## Verification

Loaded the patched script as a module and ran `require_department_dir()` directly against three cases: (1) the corrected `MARCUS_DIR` — passed, no-op since `ai/marcus/threads/` already exists with real files untouched; (2) `NOTES_DIR` — passed; (3) a reconstruction of the exact old bug (`djinn/research/marcus/threads`, whose parent doesn't exist) — correctly refused with `SystemExit(1)` and the diagnostic message, and confirmed the dead directory was NOT created as a side effect of the check itself.

---

## Rule / Lesson

> **Rule:** Any tool that hardcodes a path into a vault department directory should verify the department's own root already exists before writing into it — `mkdir(parents=True, exist_ok=True)` is convenient but actively hides exactly this failure mode (a stale path silently resurrecting a dead directory tree instead of erroring). This applies to every tool with department-path constants, not just djinn-clerk; worth auditing others (djinn-vault-enrich, djinn-doc-check, anything under `~/.local/bin` that writes into the vault) the next time a restructure happens.

---

*— Claude, 2026-07-15*
