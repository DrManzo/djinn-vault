---
title: Djinn Communications Protocol
tags: [djinn, protocol, communications, agents]
updated: 2026-05-23
---

# Djinn Communications Protocol

Rules every agent follows. No exceptions. No shortcuts.
**Related:** [[SYSTEM-STATE]] | [[ROUTING]] | [[COMMS]] | [[AGENTS]]

---

## Agent Contract

| Agent | Machine | Scope |
|-------|---------|-------|
| Claude | Salomon (API) | Architecture, synthesis, vault design — session-bound, Javier initiates |
| opencode | Salomon | Daily ops, tool use, automation, COMMS processing |
| opencode | Typhon | Typhon-local tasks, storage, COMMS processing |

---

## Network — Current State

Both machines on **192.168.1.x** subnet as of 2026-05-23.
- Salomon → Typhon: ✅ SSH works (`ssh -i ~/.ssh/id_ed25519 tf-tthq@192.168.1.113`)
- Typhon → Salomon: ✅ SSH works
- Cross-machine file delivery: Salomon can SCP directly to Typhon — no longer relay-only

~~Salomon cannot push to Typhon — permanent constraint~~ **RESOLVED 2026-05-23**

---

## Communication Channels

| Channel | File / Method | Latency | Use for |
|---------|--------------|---------|---------|
| COMMS.md | `djinn/communications/COMMS.md` | ~2 min (vault sync) | Task handoffs, decisions, persistent state |
| Telegram | Bot → Javier | Seconds | Alerts, interrupts, real-time signals |
| SSH | Direct Salomon↔Typhon | Immediate | File delivery, service management |

**COMMS.md is the primary inter-agent channel.** All agents append to it. Never overwrite.

---

## Session Protocol

Every agent, every session, in this order:

1. **READ** → `HEARTBEAT.md` + `HEARTBEAT-typhon.md` — machine status
2. **READ** → `tail -n 50 COMMS.md` — recent context
3. **WORK** → execute the task
4. **APPEND** → one entry to `COMMS.md` (see format below)
5. **PUSH** → `git add -A && git commit && git push`

No session ends without steps 4 and 5.

---

## COMMS Message Format

```
### YYYY-MM-DD HH:MM UTC — @Sender → @Recipient: Subject

**What:** one-line description
**Action:** what the recipient must do (or "none — FYI")
**Paths:** relevant files (if any)

— AgentName
```

**Recipient tags:** `@Salomon`, `@Typhon`, `@Claude`, `@All`
**Processed tag:** After acting on a message, append `**Processed:** YYYY-MM-DD — AgentName` below it.

---

## COMMS Processor — Automated Trigger

Each machine runs a `comms-processor` timer that:
1. Pulls vault (git pull)
2. Scans COMMS.md for unprocessed messages addressed to this machine
3. If found → invokes `opencode run` with SOUL + AGENTS context + message
4. opencode executes, appends response to COMMS.md
5. Pushes vault

This means any agent can leave a task for Salomon or Typhon and it will be picked up within ~3 minutes.

---

## Ownership

| Agent | Owns | Never touches |
|-------|------|---------------|
| Claude | COMMS.md, PROTOCOL.md, SYSTEM-STATE.md, djinn/projects/, djinn/logs/ | systemd timers, ~/.local/bin/, heartbeat files |
| Salomon | HEARTBEAT.md, systemd timers, ~/.local/bin/ scripts, vault-sync | vault structure, routing docs |
| Typhon | HEARTBEAT-typhon.md, printer bot service, Typhon timers | vault structure, routing docs |
| Anyone | Append to COMMS.md, CHANGELOG.md | — |

---

## Signing Convention

| Agent | Signature | Git Author | Git Email |
|-------|-----------|------------|-----------|
| Claude | `— Claude` | `Claude` | `claude@djinn` |
| Salomon opencode | `— Salomon` | `DrManzo` | `salomon@djinn` |
| Typhon opencode | `— Typhons Forge` | `Typhons Forge` | `typhon@djinn` |

---

## Report Standard

All session reports, audits, and significant work logs go to the vault as wiki-standard documents:
- YAML frontmatter (title, tags, date, related)
- Wikilinks `[[file]]` for all cross-references
- Saved under `djinn/logs/` or relevant subject dir
- Linked from the hub file for that domain

*— Claude, 2026-05-23*
