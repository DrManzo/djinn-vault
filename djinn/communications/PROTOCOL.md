---
title: Djinn Communications Protocol
tags: [djinn, protocol, communications, agents]
updated: 2026-05-28
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
4. **REPORT** → write a session report (see Report Standard below)
5. **APPEND** → one entry to `COMMS.md` (see format below)
6. **PUSH** → `git add -A && git commit && git push`

No session ends without steps 4, 5, and 6. **A session that produces no report is incomplete.**

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

**Every agent must write a session report whenever significant work is completed.** This is not optional and does not require Javier to ask. "Significant work" means: anything that creates, modifies, or deletes files; any build, install, or configuration change; any decision with architectural implications; any completed pipeline run.

### When to write a report

| Trigger | Report required |
|---------|----------------|
| Build session (new tools, agents, configs) | Yes — always |
| Print job started or completed | Yes — update print log |
| Media project processed end-to-end | Yes — update project manifest |
| Config change (OpenClaw, systemd, vault) | Yes — note what changed and why |
| Debug session | Yes — document root cause and fix |
| Routine sync / heartbeat | No |
| Read-only query | No |

### File naming and location

```
djinn/logs/reports/YYYY-MM-DD_<slug>.md
```

One file per session or per significant topic. If a session covers multiple unrelated topics, write one file per topic.

### Required format

Use `djinn/logs/REPORT-TEMPLATE.md` as the base. Every report must have:

1. **YAML frontmatter** — title, agent, date, tags, related wikilinks
2. **Summary** — 2–4 sentences: what, why, key outcome
3. **What Was Built or Changed** — specifics: names, paths, commands
4. **Technical Decisions** — non-obvious choices with rationale
5. **Files Created or Modified** — explicit list
6. **Tests & Validation** — what was run, what passed
7. **Known Issues** — caveats and limitations (write "None" if clean)
8. **What's Next** — checkbox list, assign to agent where known
9. **Signature** — `— AgentName, YYYY-MM-DD`

### Build log and decision log

After writing the full report, also append a **short summary entry** (3–8 bullet points) to:
- `djinn/logs/build-log.md` — what was done
- `djinn/decisions/decision-log.md` — if any architectural decision was made

### Enforcement

Any AI agent — Claude, Salomon opencode, Typhon opencode, or any media/design agent — is expected to produce a report unprompted. If Javier has to ask for a report, the session protocol was not followed.

Salomon: `djinn-session-end "slug" "summary"` is called by the comms-processor wrapper after every opencode invocation. If no report exists for today, a stub is auto-created and Javier is notified via Telegram.

---

## Bug Reporting

**Every bug — discovered, diagnosed, or fixed — must be logged. This is not optional.**

A bug is: any unexpected behavior, crash, import error, logic error, misconfiguration, or silent failure. If something broke and you fixed it, that's a bug. Log it.

### Why this matters

Bugs are institutional memory. An agent that fixes a bug silently has deprived every future agent (and Javier) of the knowledge that this failure mode exists and what it looks like. The rule, the root cause, and the fix are exactly what turns a one-time incident into a system that gets smarter.

### How to log a bug

**Fast path (any agent, any machine):**
```bash
djinn-bugreport "Title" "Root cause summary" [system] [severity] [status]
```
This creates a bug report in `djinn/logs/reports/YYYY-MM-DD_bug-<slug>.md`, appends to `djinn/logs/bugs.md`, appends to `build-log.md`, commits, pushes, and optionally sends a Telegram notification.

**Severity levels:**
- `critical` — system is down, data loss possible, Javier must be notified immediately
- `high` — feature is broken, workaround exists but deployment is degraded
- `medium` — bug found and fixed without user impact; important to document
- `low` — cosmetic, edge case, or minor behavior deviation

**Minimum a bug report must include:**
1. What the symptom was (exact error, log line, behavior)
2. Root cause (not a guess — dig until you know)
3. Fix applied (what changed, where)
4. Rule/lesson — one sentence that prevents this class of bug in the future

### Bug log

All bugs are indexed in `djinn/logs/bugs.md`. Template: `djinn/logs/BUG-REPORT-TEMPLATE.md`.

### Bug severity → action

| Severity | Action |
|----------|--------|
| critical | Telegram alert immediately + bug report + session report |
| high | Bug report + session report + COMMS entry |
| medium | Bug report + session report |
| low | Bug report (can be brief) |

*— Claude, 2026-05-28*
