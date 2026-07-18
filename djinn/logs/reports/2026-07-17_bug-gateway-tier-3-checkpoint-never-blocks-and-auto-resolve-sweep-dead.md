---
title: Bug Report — Gateway Tier 3 checkpoint never blocks pushes, and the checkpoint auto-resolve sweep has been dead since 2026-06-14
agent: Claude
date: 2026-07-17
severity: high
status: open
tags: [djinn, bug, djinn-gateway, checkpoints, git]
related: [[bugs]] | [[build-log]] | [[GATEWAY]]
---

# Bug Report — Gateway Tier 3 checkpoint never blocks pushes, and the checkpoint auto-resolve sweep has been dead since 2026-06-14

**Date:** 2026-07-17 19:28
**Agent:** Claude
**System:** djinn-gateway (`~/.local/bin/djinn-gateway`, pre-push hook, `CHECKPOINTS.md`)
**Severity:** high
**Status:** open

---

## Root Cause

Two separate, compounding gaps in the same subsystem:

1. **Phase 2 (blocking) was never implemented.** `djinn-gateway`'s `cmd_checkpoint()` posts the checkpoint to COMMS + Telegram, prints `"(Phase 1: non-blocking. Phase 2 will wait for reply.)"`, then immediately calls `sys.exit(0)`. The very next line in the source is a comment: `# Phase 2: block here and poll checkpoints/{chk_id}.json for Y/N` — dead code that documents the intended behavior but was never written. The installed pre-push hook (`install_hooks()`) mirrors this: for a Tier 3 action it logs `"Standard mode — Tier 3 push: logging checkpoint and allowing."` and unconditionally `exit 0`s. So despite GATEWAY.md's framing of checkpoints as an approval gate, a regular `git push` to `main` requires zero actual Javier approval today — it always goes through.

2. **The passive checkpoint auto-resolve sweep has also been dead for over a month.** `CHECKPOINTS.md` shows a working sweep through 2026-06-14 (`"Resolved: 105 PENDING checkpoints → TIMEOUT_DENIED (age > 5 min)"`), after which every single checkpoint — 1,343 of them as of this report, vs. 106 ever resolved — has stayed `PENDING` forever. Whatever process ran that sweep (cron/systemd timer, not found in this session) appears to have stopped running silently, with no error surfaced anywhere.

Neither gap is new damage — Tier 3 was always effectively "log + allow," and the sweep dying doesn't lose data, it just leaves a growing, misleading `PENDING` backlog. But the combination means the approval workflow described in GATEWAY.md ("enforcement contract: read before any write, commit, push, or send action") does not currently enforce anything for git pushes — it only logs.

---

## Symptom

Surfaced when reconciling a filament inventory update: after committing and pushing changes to the vault repo, the push succeeded immediately and unconditionally. The pre-push hook printed a Tier 3 checkpoint message and posted `CHECKPOINT-20260717-192308` to `CHECKPOINTS.md` + Telegram, but the push was not held pending Javier's Y/N — it landed on GitHub (`39a3218f..20ceb2a3`) in the same command. Checking `CHECKPOINTS.md` showed the new checkpoint sitting `PENDING`, identical in status to 1,343 older, never-resolved checkpoints going back to mid-June.

---

## Steps to Reproduce

1. Make any change in `~/Obsidian`, commit it on `main`.
2. `git push origin main`.
3. Observe: the pre-push hook logs a Tier 3 checkpoint and the push completes immediately — no wait, no block, regardless of whether Javier responds.
4. `grep -c PENDING ~/Obsidian/djinn/communications/CHECKPOINTS.md` — count only grows; nothing since 2026-06-14 has flipped to `TIMEOUT_DENIED`.

---

## Fix Applied

None yet — this session only diagnosed and documented the gap; no code changed. Flagging for a future session (or Javier's call) to decide between:
- Implementing the stubbed Phase 2 (poll `checkpoints/{chk_id}.json`, block until Y/N or timeout) if blocking was actually the intended production behavior, or
- Formally downgrading GATEWAY.md's description of Tier 3 to match reality (log + notify, non-blocking) if "log + allow" was an acceptable interim design that just needs its docs corrected, plus
- Either way, restoring or replacing whatever swept stale `PENDING` checkpoints to `TIMEOUT_DENIED` before 2026-06-14, so the log doesn't grow unbounded and unreadable.

---

## Verification

N/A — no fix applied yet.

---

## Rule / Lesson

> **Rule:** Don't assume a documented approval gate (GATEWAY.md's "enforcement contract") is actually enforcing anything — read the hook's actual source (`~/.local/bin/djinn-gateway`) before relying on it, since a `sys.exit(0)` after a "waiting for approval" message means the wait never happens. Any tier described as blocking needs an explicit test (make a change, push, confirm it actually stops) rather than trusting the log message it prints.

---

*— Claude, 2026-07-17*
