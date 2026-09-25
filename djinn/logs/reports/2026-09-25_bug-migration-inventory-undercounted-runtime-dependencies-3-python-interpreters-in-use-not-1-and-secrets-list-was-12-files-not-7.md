---
title: Bug Report — Migration inventory undercounted runtime dependencies: 3 Python interpreters in use, not 1, and secrets list was 12 files not 7
agent: Claude
date: 2026-09-25
severity: high
status: fixed
tags: [djinn, bug, New-Typhon (migration Phase 2, runtime dependency audit)]
related: [[bugs]] | [[build-log]]
---

# Bug Report — Migration inventory undercounted runtime dependencies: 3 Python interpreters in use, not 1, and secrets list was 12 files not 7

**Date:** 2026-09-25 09:38
**Agent:** Claude
**System:** New-Typhon (migration Phase 2, runtime dependency audit)
**Severity:** high
**Status:** fixed

---

## Root Cause

The original migration inventory (2026-09-07) and typhon-bootstrap.sh only accounted for pyenv 3.11.11. Live-fire testing on new-Typhon revealed the actual automation stack uses THREE distinct Python interpreters: system python3 (3.14, via '#!/usr/bin/env python3', used by most djinn-*/forge-*/studio- scripts, needs flask+requests installed into its user-site -- and python3-pip itself wasn't even present on the fresh install), pyenv 3.11.11 directly (a handful of scripts pin this shebang explicitly), and a THIRD interpreter never mentioned in the inventory at all: a dedicated virtualenv at ~/.venvs/djinn-orchestrator (Python 3.11.11, ~49 packages including anthropic/openai/ollama client libs + trimesh/manifold3d/rtree geometry tooling) used by djinn-hound, djinn-iris-address-watch, djinn-print-complete-watcher, and djinn-printer-log-sync. None of this was discoverable from the inventory doc -- only found by actually starting each service and reading the real ModuleNotFoundError tracebacks. Also found inotify-tools (system apt package, provides inotifywait) was missing -- used by inbox-watcher. Separately, the inventory's 'Cross-cutting dependencies: 7 secret files' was also incomplete -- grepping every migrating script's actual env-file references (not the inventory doc) found 5 additional required secrets never listed: ~/.config/djinn/groq.env, ops-tg.env, personal-tg.env, firecrawl.env, and claude.env (the Anthropic API key, read implicitly by the SDK from env, no explicit os.environ reference to grep for -- this one in particular would never have been found by code inspection alone, only by noticing the orchestrator venv's anthropic package and reasoning backward to what it needs). Two more required symlinks (~/.config/djinn/printer-bot.env and ~/.config/djinn/shop.env, both pointing into ~/.config/forge/) were also missing until traced.

---

## Symptom

<!-- Fill in: what the user or system observed -->

---

## Steps to Reproduce

1. <!-- steps -->

---

## Fix Applied

<!-- What was changed, where, and why -->

---

## Verification

<!-- How you confirmed the fix worked -->

---

## Rule / Lesson

> **Rule:** <!-- one sentence: what prevents this class of bug in the future -->

---

*— Claude, 2026-09-25*
