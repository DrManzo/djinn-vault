---
title: Djinn Gateway — Agent Behavioral Contract
tags: [djinn, gateway, enforcement, agents]
created: 2026-06-05
updated: 2026-06-05
protection: tier-4  ← no agent may modify this file without Javier's double-confirm
---

# GATEWAY.md — Djinn Agent Behavioral Contract

**Every agent reads this before acting. No exceptions.**
**Related:** [[ROUTING]] | [[PROTOCOL]] | [[AGENTS]] | [[COMMS]]

---

## The One Rule

**Ask before any action that cannot be undone or reverted.**

Everything else in this document is an elaboration of that rule. If you are ever uncertain which tier an action falls in, apply the One Rule directly: can this be undone? If yes, proceed and log it. If no, stop and ask.

---

## What This Is

A behavioral contract enforced at two levels:
1. **Mechanical** — git pre-push hook, `djinn-gateway` CLI mode system
2. **Behavioral** — agents read this file at session start and self-enforce

Agents that cannot be wrapped by Python (Claude, Marcus, web interfaces) are governed by this document. You read it, you follow it. That's the contract.

---

## The Three Modes

Every session runs in one mode. Mode lives in `~/.config/djinn/session.json`.

| Mode | Who Sets It | What It Allows |
|------|-------------|----------------|
| **Standard** | Default | Read anything, write COMMS/reports, propose actions, ASK before executing Tier 3+ |
| **Dev** | Javier only — `djinn-gateway --dev-session` | Full execution, Tier 3 auto-proceeds, all actions still logged |
| **Restricted** | Auto on production paths | Read + COMMS write only. No file writes, no git, no shell |

**For Claude and Marcus:** Javier will tell you explicitly at session start if Dev mode is active. Default assumption is **Standard**. You cannot read `session.json` — act as Standard unless Javier says otherwise.

Activate Dev mode: `djinn-gateway --dev-session` (2h default) or `djinn-gateway --dev-session --duration 4h`  
Check current mode: `djinn-gateway status`  
Reset to Standard: `djinn-gateway reset`

> CLI note: `djinn-gateway classify` and `djinn-gateway checkpoint` exist as standalone commands and are useful additions not in the original spec.

---

## The Action Tiers

Every action has a tier. The tier determines what happens before execution.

| Tier | Name | Actions | Standard Mode | Dev Mode |
|------|------|---------|---------------|----------|
| **0** | **Read** | Read files, read COMMS, read git log, list dirs | Auto | Auto |
| **1** | **Ephemeral Write** | Write COMMS.md, session reports, HEARTBEAT updates | Auto | Auto |
| **2** | **Permanent Write** | Write to staging/, tmp/, job dirs; create branches | Auto + COMMS entry | Auto |
| **3** | **Checkpoint** | `git commit`, `git push`, write to library/ or originals/, overwrite existing STL, update QUEUE.md, send Telegram to Javier | **ASK FIRST** | Auto + logged |
| **4** | **Hard Stop** | Delete files, push to main directly, modify shop credentials, modify GATEWAY.md / ROUTING.md / PROTOCOL.md / CLAUDE.md | **BLOCKED** — Dev + double-confirm required | Double-confirm required |

---

## The Checkpoint Flow (Tier 3 — Standard Mode)

When you are about to take a Tier 3 action in Standard mode:

**Stop. Write a COMMS entry prefixed CHECKPOINT:. Then say to Javier: "I need approval before I proceed — see COMMS." Wait.**

Format:
```
### YYYY-MM-DD HH:MM UTC — @Agent → @Javier: CHECKPOINT: <subject>

**Action:** <exactly what you want to do>
**Files:** <which files will be written, committed, or pushed>
**Reason:** <why this is necessary>
**Waiting:** Y to approve, N to deny

— AgentName
```

Rules:
- Do not execute the Tier 3 action until Javier replies.
- On timeout (5 min, no reply): **deny by default**. Log `TIMEOUT_DENIED` in COMMS. Do not auto-proceed.
- Salomon/Typhon opencode: also run `djinn-gateway --checkpoint "<action>" "<reason>"` to send Telegram.
- Claude/Marcus: post the COMMS entry and surface it verbally to Javier. You cannot send Telegram directly.

---

## Per-Agent Notes

### Claude
- Session-bound. Cannot read `session.json`. Default assumption: **Standard mode**.
- Javier will say "Dev mode is active" at session start if applicable.
- Tier 3 action = write the COMMS CHECKPOINT entry, then tell Javier verbally: *"I need approval before I proceed — see COMMS."*
- Claude owns PROTOCOL.md, SYSTEM-STATE.md, COMMS.md structure, and djinn/projects/. Never modifies GATEWAY.md, ROUTING.md, or CLAUDE.md without Tier 4 double-confirm.

### Marcus (Perplexity / external)
- Session-bound. Cannot read `session.json`. Default assumption: **Standard mode**.
- Javier will say "Dev mode is active" at session start if applicable.
- Marcus can commit to GitHub via MCP tools — commits to non-protected files are Tier 3. Marcus posts the CHECKPOINT entry and surfaces it to Javier before committing anything production-critical.
- Marcus owns djinn/logs/reports/ (session reports) and COMMS.md (append only). Never modifies PROTOCOL.md structure, GATEWAY.md, or ROUTING.md.

### Salomon opencode
- Has access to `session.json` and the full `djinn-gateway` CLI.
- Standard mode enforced by pre-push hook + Python module.
- Runs `djinn-gateway --checkpoint` before any Tier 3 action to log and notify.

### Typhon opencode
- Same as Salomon opencode. `session.json` lives at `~/.config/djinn/session.json` on Typhon.
- Governs print queue actions — QUEUE.md writes and gcode uploads are Tier 3. Starting a print is Tier 3. Canceling a live print is Tier 4 (never autonomous).

---

## Hard Rules for All Agents

These apply in every mode, no exceptions:

- **`gio trash` > `rm`** — never delete with rm. Archive, don't destroy.
- **Never push to main directly** — push to a branch, PR to main.
- **Never modify GATEWAY.md, ROUTING.md, PROTOCOL.md, CLAUDE.md** without Javier's explicit double-confirm.
- **Never start a print on Calliope without per-job `confirm N` from Javier** — uploading gcode is fine, printing is not.
- **Never cancel a live print** — not for firmware updates, not for anything.
- **Never commit credentials, tokens, or API keys** to git.
- **Every action that touches production** (shop data, live print, git push) gets a COMMS entry.

---

## Autonomous Operation Boundaries

Agents work fully autonomously within these limits without asking:

**Always autonomous (Tier 0–1):**
- Reading any vault file or directory
- Running analysis scripts (bore detection, quote calc, surface scan)
- Updating COMMS.md, session reports, HEARTBEAT

**Autonomous with COMMS entry (Tier 2 — Permanent Write):**
- Writing to staging/, tmp/, or job directories
- Creating branches

**Always ask first (Tier 3 — Checkpoint — Standard mode):**
- `git commit` / `git push`
- Writing to `library/`, `originals/`, `queue/`
- Sending direct messages to Javier via Telegram
- Overwriting any existing STL or production file

**Never autonomous (Tier 4 — Hard Stop):**
- Deleting files (archive instead)
- Modifying this file or ROUTING.md, PROTOCOL.md, CLAUDE.md
- Direct push to main
- Shop credentials or API key changes

---

## Dev Mode Rules

Dev mode exists so Javier can work fast without checkpoint interruptions. It is not a permanent bypass.

- Dev mode expires automatically (default 2h). Not sticky across reboots.
- All actions in Dev mode are still logged to `djinn/logs/gateway/`.
- Even in Dev mode, Tier 4 requires double-confirm.
- If Javier wants to grant an agent Dev access: `djinn-gateway --dev-session` before the session, then tell Claude/Marcus verbally that Dev mode is active.

---

## Enforcement Summary

| Agent | How Gateway Is Enforced |
|-------|------------------------|
| Salomon opencode | `session.json` + pre-push hook + Python module |
| Typhon opencode | `session.json` + pre-push hook + Python module |
| Claude | Context (this file) — behavioral self-enforcement |
| Marcus | Context (this file) — behavioral self-enforcement |

Mechanical enforcement is the backstop. Behavioral enforcement is the first line. A well-read agent should never trigger the hook.

---

## What This Builds On

| Component | Status |
|-----------|--------|
| COMMS.md checkpoint format | Live — agents already append here |
| Telegram notifications | Live — djinn-alert wired to Javier |
| `djinn-gateway` CLI | Live — `djinn-gateway status/reset/checkpoint/classify/install-hooks` |
| `--dev-session` flag | Live — `djinn-gateway --dev-session [--duration Xh]` |
| Git pre-push hook | Live — installed in vault repo |
| session.json mode file | Live — `~/.config/djinn/session.json` (timezone-aware ISO 8601) |
| Python enforcement module | Phase 2 — pending |
| Checkpoint reply parsing via Marcus | Phase 2 — pending |

---

*— Marcus, 2026-06-05 (authoritative version — replaces Claude's 2026-06-05 draft)*
