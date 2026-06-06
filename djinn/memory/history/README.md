---
title: Djinn Memory — History (Append-Only)
tags: [memory, typhon, history, append-only]
updated: 2026-06-05
---

# History (Append-Only)

This directory holds append-only event logs for every domain tracked in `../current/`.

**Rules:**
- Files in this directory are never modified after a record is written.
- Only Typhon appends to these logs.
- Each append is a single event block (see format below).

## Log Files

| File | Domain |
|------|--------|
| `printer-state.log` | Printer state changes |

## Entry Format

```
[YYYY-MM-DDTHH:MM:SSZ] ACCEPT|REJECT|INIT | source=<agent> | domain=<domain> | field=<field>
BEFORE: <previous value or "null">
AFTER:  <new value or description>
NOTE:   <one-line rationale>
---
```

## Conflict Entry Format

```
[YYYY-MM-DDTHH:MM:SSZ] CONFLICT | source=<agent> | domain=<domain>
CURRENT: <Typhon's current record>
PROPOSED: <conflicting value from request>
ACTION: Held in requests/<filename>.md — awaiting Javier review (NEEDS-REVIEW)
---
```
