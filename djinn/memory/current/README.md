---
title: Djinn Memory — Current State
tags: [memory, typhon, current-state]
updated: 2026-06-05
---

# Current State

This directory holds the canonical latest state for each tracked domain.

**Write authority: Typhon only.**
All other agents are read-only consumers.

## Files

| File | Domain | Description |
|------|--------|-------------|
| `printer-state.md` | 3D printing | Calliope printer current state, last job, queue depth |

New domain files are added here by Typhon only, triggered by a processed request in `../requests/`.
