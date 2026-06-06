---
title: Djinn Memory — Reports Archive
tags: [memory, typhon, reports, archive]
updated: 2026-06-05
---

# Reports Archive

This directory holds detailed analyses, task outputs, session reports, and postmortems
produced by any agent and submitted to the memory store.

## Rules

- Any agent may create a new report file here.
- Files are write-once — never overwrite an existing report.
- Filename format: `YYYY-MM-DD_<agent>_<slug>.md`
- Typhon indexes new reports when it processes the requests queue.

## Relationship to `djinn/logs/reports/`

`djinn/logs/reports/` holds session reports written directly by agents during active work.
`djinn/memory/reports/` holds reports that have been submitted to the memory store for canonical archival by Typhon.
For most operational work, both paths will exist — the logs path is the working copy, the memory path is the archived copy.
