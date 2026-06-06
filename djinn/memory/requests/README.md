---
title: Djinn Memory — Requests Queue
tags: [memory, typhon, requests]
updated: 2026-06-05
---

# Requests Queue

This directory holds proposed state updates submitted by non-Typhon agents.
Typhon processes these at its own cadence, validates each one, and either accepts or rejects.

## Rules

- Any agent may create a new `.md` file here.
- Never overwrite an existing file.
- Never delete files from this directory manually — Typhon archives processed requests.
- After Typhon processes a request, it appends a `PROCESSED:` block to the file.

## Request File Format

```markdown
---
request_id: YYYY-MM-DD_<agent>_<domain>_<slug>
source_agent: <agent name>
target_domain: <domain, e.g. memory.current.printer-state>
timestamp: YYYY-MM-DDTHH:MM:SSZ
priority: normal | high | needs-review
---

## Proposed Update

<description of the proposed change and the new value>

## Rationale

<why this update is needed>
```
