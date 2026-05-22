# Djinn Communications Protocol

## Agent Contract

| Agent | Scope |
|-------|-------|
| Claude API | Architecture, synthesis, vault design — session-bound, Javier initiates |
| Claude Code / Salomon | Complex builds, file editing on Salomon |
| opencode / Salomon | Daily ops, tool use, automation, quick queries |
| Claude Code / Typhon | Typhon-local code work only |

## Routing

- Architecture / synthesis → **Claude API** (Javier opens session)
- Code work on Salomon → **Claude Code / Salomon**
- Daily ops, tool use → **opencode / Salomon**
- Anything on Typhon → **Typhon agents**
- Cross-machine → **Typhon initiates.** Salomon writes to COMMS.md → Typhon reads on sync → Typhon executes.
- Salomon cannot push to Typhon. This is a permanent network constraint, not a bug.

## Two Channels

| Channel | Use for | Latency |
|---------|---------|---------|
| Telegram | Alerts, interrupts, real-time signals | Seconds |
| COMMS.md | Decisions, task handoffs, persistent state | ~2 min (vault sync) |

## Session Protocol

Every agent, every session, in order:

1. **READ** → `HEARTBEAT.md` + `HEARTBEAT-typhon.md` (machine status)
2. **READ** → `tail -n 50 COMMS.md` (recent context)
3. **WORK** → do the task
4. **APPEND** → one entry to `COMMS.md`
5. **PUSH** → `git add . && git commit -m "..." && git push`

No session ends without steps 4 and 5.

## Message Format

```
### YYYY-MM-DD HH:MM UTC — @Sender → @Recipient: Subject
- **What:** one line
- **Action:** what recipient does (or "none")
- **Paths:** relevant files if any
— AgentName
```

## Ownership

| Agent | Owns | Never touches |
|-------|------|---------------|
| Claude | COMMS.md, PROTOCOL.md, djinn/projects/, djinn/logs/ | systemd timers, ~/.local/bin/, heartbeat files |
| Salomon | HEARTBEAT.md, systemd timers, ~/.local/bin/ | vault structure, routing docs |
| Typhon | HEARTBEAT-typhon.md, printer agent, Typhon timers | vault structure, routing docs |
| Anyone | Append to COMMS.md, CHANGELOG.md | — |

## Signing

| Agent | Signature | Git Author |
|-------|-----------|------------|
| Claude | `— Claude` | `Claude` |
| Salomon | `— Salomon` | `DrManzo` |
| Typhon | `— Typhons Forge` | `Typhons Forge` |
