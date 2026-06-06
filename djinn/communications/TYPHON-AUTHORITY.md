---
title: Typhon Memory Authority Standard
agent: Perplexity (on behalf of Marcus)
date: 2026-06-05
tags: protocol, memory, typhon, authority, append-only
status: active
---

# Typhon Memory Authority Standard

## The Rule

**Typhon is the sole write authority for all long-term memory, current-state records, and archived reports in the Djinn system.**

All other agents — Claude, Salomon, Marcus, Perplexity, or any sub-agent — are read-only consumers. They may produce analyses, proposals, and reports. They may not write directly to any canonical memory or state store. They submit requests to Typhon. Typhon decides.

---

## Storage Layout

```
djinn/memory/
  current/       ← Typhon's canonical latest state for each tracked domain
  history/       ← Append-only event log, never modified after write
  requests/      ← Inbound proposed updates from other agents (unprocessed)
  reports/       ← Detailed analyses, task outputs, postmortems (read-only archive)
```

- `current/` is the single source of truth. One file per domain.
- `history/` is append-only. Records are never modified or deleted after they are written.
- `requests/` holds proposed updates submitted by non-Typhon agents. Typhon processes them at its own cadence.
- `reports/` is an archive. Files are written once and never overwritten.

---

## Write Workflow

1. An agent produces analysis, a proposed update, or a new report.
2. The agent writes the request or report to `requests/` or `reports/` — the only two locations non-Typhon agents may touch.
3. Typhon picks up the request.
4. Typhon validates: structure, timestamp, source agent, and conflict with current state.
5. If valid, Typhon writes the canonical update to `current/`.
6. Typhon appends a full before/after diff entry to `history/`.
7. Typhon republishes the updated state to all readers.

If invalid or ambiguous, Typhon:
- Retains the request in `requests/` with a rejection note appended.
- Writes a rejection event to `history/`.
- Leaves `current/` unchanged.
- Requests a human decision only if the proposed update is high-stakes (marks it `NEEDS-REVIEW`).

---

## Conflict Rule

If any agent's proposed update conflicts with Typhon's current record:

> **Typhon's current record wins until a human explicitly overrides it.**

There is no automatic merge. Conflicting requests are held in `requests/` with a `CONFLICT` flag and reviewed by Javier.

---

## Fail-Safe Mode

When Typhon is unreachable or in an error state:

- All non-Typhon agents switch to **pull-only mode** immediately.
- No agent may write to `current/` or `history/` during outage.
- Pending reports and requests accumulate in `requests/` for Typhon to process on recovery.
- `current/` is treated as frozen-valid until Typhon comes back online.
- Typhon logs the outage window on recovery with a `TYPHON-RECOVERY` event in `history/`.

---

## History Entry Format

Every `history/` entry is a single append to the domain's `.log` file. Format:

```
[2026-06-05T18:31:00Z] ACCEPT | source=Claude | domain=printer.tools | field=djinn-detect-surfaces
BEFORE: null
AFTER: created djinn/printer/tools/djinn-detect-surfaces.py
NOTE: New tool — surface detection pre-flight for djinn-model-text-engrave
---
```

For rejections:

```
[2026-06-05T18:31:00Z] REJECT | source=Salomon | domain=memory.current-state | field=queue_depth
REASON: Stale timestamp — proposed value is 47min old
ACTION: Held in requests/2026-06-05-salomon-queue-depth.md
---
```

---

## What Non-Typhon Agents May Do

| Action | Allowed |
|---|---|
| Read from `current/` | ✅ |
| Read from `history/` | ✅ |
| Read from `reports/` | ✅ |
| Write to `reports/` (new file, never overwrite) | ✅ |
| Write to `requests/` (new file, never overwrite) | ✅ |
| Write to `current/` | ❌ |
| Write to `history/` | ❌ |
| Modify any existing file in `current/` or `history/` | ❌ |

---

## Rationale

This standard exists because:

1. **Split-brain drift** — when multiple agents can write to the same memory store, state diverges silently. The system loses the ability to know what is actually true.
2. **Auditability** — append-only history means every change can be traced, replayed, and reviewed. Nothing is silently overwritten.
3. **Recovery** — a single writer means recovery after outage is deterministic. Typhon processes the queue and reconciles cleanly.
4. **Tool chain integrity** — the 3D printing pipeline, shop operations, and agent orchestration all depend on consistent state. A single authority prevents one agent's bad write from corrupting another agent's read.

---

## Integration With Existing Systems

- **COMMS.md** — COMMS entries are write-once reports. They go to `reports/`. Typhon indexes them. ✅
- **QUEUE.md** — Queue state is tracked in `current/queue-state.md`. Only Typhon updates it based on verified agent output. ✅
- **HEARTBEAT-typhon.md** — Typhon writes its own heartbeat. This is the one self-write Typhon performs directly. ✅
- **Salomon-to-Typhon.md / Typhon-to-Salomon.md** — These are message channels, not memory stores. They are read-write for their respective owners as communication primitives, not canonical state. ✅
- **djinn-detect-surfaces / djinn-bore-core** — Tool outputs (surfaces.json, COMMS entries) route through `requests/`. Typhon decides what gets promoted to `current/`. ✅

---

## Enforcement

This is a **protocol standard**, not a code-enforced permission system (yet). All agents operating in the Djinn system are expected to follow it. Violations should be noted in COMMS with a `PROTOCOL-BREACH` tag.

Future hardening: add a Typhon gateway script (`djinn-typhon-write`) that is the only process with filesystem write permissions to `current/` and `history/`. All writes go through it. Direct writes to those paths fail with a permission error.

---

*Written 2026-06-05. Author: Perplexity on behalf of Marcus. Based on single-writer, append-only memory architecture for the Djinn agent system.*
