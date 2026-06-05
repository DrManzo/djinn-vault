---
title: Djinn Gateway — Agent Behavioral Contract
tags: [djinn, gateway, enforcement, agents]
created: 2026-06-05
protection: tier-4  ← no agent may modify this file without Javier's double-confirm
---

# GATEWAY.md — Djinn Agent Behavioral Contract

**Every agent reads this before acting. No exceptions.**
**Related:** [[ROUTING]] | [[PROTOCOL]] | [[AGENTS]] | [[COMMS]]

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
| **Dev** | Javier only — `djinn-gateway dev` | Full execution, Tier 3 auto-proceeds, all actions still logged |
| **Restricted** | Auto on production paths | Read + COMMS write only. No file writes, no git, no shell |

Agents that cannot read `session.json` default to **Restricted**.

Activate Dev mode: `djinn-gateway dev` (2h default) or `djinn-gateway dev --duration 4h`
Check current mode: `djinn-gateway status`
Reset to Standard: `djinn-gateway reset`

---

## The Action Tiers

Every action has a tier. The tier determines what happens before execution.

| Tier | Actions | Standard Mode | Dev Mode |
|------|---------|---------------|----------|
| **0 — Read** | Read files, read COMMS, read git log, list dirs | Auto | Auto |
| **1 — Log** | Write COMMS.md, session reports, HEARTBEAT updates | Auto | Auto |
| **2 — Propose** | Write to staging/, tmp/, job dirs; create branches | Auto + COMMS entry | Auto |
| **3 — Checkpoint** | `git commit`, `git push`, write to library/ or originals/, overwrite existing STL, update QUEUE.md, send Telegram to Javier | **ASK FIRST** | Auto + logged |
| **4 — Hard Stop** | Delete files, push to main directly, modify shop credentials, modify GATEWAY.md / ROUTING.md / PROTOCOL.md / CLAUDE.md | **BLOCKED** — Dev + double-confirm required | Double-confirm required |

---

## The Checkpoint Flow (Tier 3 — Standard Mode)

When you are about to take a Tier 3 action in Standard mode:

1. **Stop.** Do not execute the action.
2. **Post to COMMS.md** — use this format:
   ```
   ## CHECKPOINT-{timestamp} | {agent} | PENDING
   **Action:** <what you want to do>
   **Files:** <which files>
   **Reason:** <why>
   → Waiting for Javier: Y to approve, N to deny
   ```
3. **Run `djinn-gateway checkpoint "<action>" "<reason>"`** — this sends Telegram to Javier and logs the request.
4. **Wait for explicit approval** before proceeding.
5. On timeout (5 min, no reply): **deny by default**. Log `TIMEOUT_DENIED` in COMMS. Do not auto-proceed.

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

**Always autonomous (Tier 0–2):**
- Reading any vault file or directory
- Running analysis scripts (bore detection, quote calc, surface scan)
- Writing to staging, tmp, or job directories
- Updating COMMS.md, session reports, HEARTBEAT

**Always ask first (Tier 3 — Standard mode):**
- `git commit` / `git push`
- Writing to `library/`, `originals/`, `queue/`
- Sending direct messages to Javier via Telegram
- Overwriting any existing STL or production file

**Never autonomous (Tier 4):**
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
- If Javier wants to grant an agent Dev access: `djinn-gateway dev` before the session.

---

## What This Builds On

| Component | Status |
|-----------|--------|
| COMMS.md checkpoint format | Live — agents already append here |
| Telegram notifications | Live — djinn-alert wired to Javier |
| `djinn-gateway` CLI | Live — `djinn-gateway status/dev/reset/checkpoint/install-hooks` |
| Git pre-push hook | Live — installed in vault repo |
| session.json mode file | Live — `~/.config/djinn/session.json` |
| Python enforcement module | Phase 2 — pending |
| Checkpoint reply parsing via Marcus | Phase 2 — pending |

---

*— Claude, 2026-06-05*
