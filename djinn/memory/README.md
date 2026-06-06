---
title: Djinn Memory Store
tags: [memory, typhon, authority, state]
updated: 2026-06-05
---

# Djinn Memory Store

This is the canonical memory and state store for the Djinn system.
**Typhon is the sole write authority.** All other agents are read-only.
See `djinn/communications/TYPHON-AUTHORITY.md` for the full protocol.

## Directory Layout

```
djinn/memory/
  current/     — Typhon's canonical latest state for each tracked domain
  history/     — Append-only event log. Never modified after write.
  requests/    — Inbound proposed updates from other agents (unprocessed)
  reports/     — Detailed analyses, task outputs, postmortems (read-only archive)
```

## Rules

- Only Typhon writes to `current/` and `history/`.
- Any agent may write to `reports/` (new file only, never overwrite).
- Any agent may write to `requests/` (new file only, never overwrite).
- Direct writes to `current/` or `history/` by non-Typhon agents are protocol violations. Tag the COMMS entry `PROTOCOL-BREACH`.
- When Typhon is unavailable, all agents switch to pull-only mode. No writes to `current/` or `history/` during outage.

## Write Gateway

`~/.local/bin/djinn-typhon-write` is the script Typhon uses to process requests, write canonical state, and append to history. Other agents never call it directly — they write requests to `requests/` and Typhon picks them up.

## Related
- `djinn/communications/TYPHON-AUTHORITY.md` — full authority standard
- `djinn/communications/PROTOCOL.md` — agent ownership table
- `djinn/communications/COMMS.md` — inter-agent channel
