---
title: Session Report — Gateway Compaction / Empty Response Fix
agent: Claude
date: 2026-05-25
tags: [djinn, report, openclaw, gateway, debug]
related: [[build-log]] | [[decision-log]] | [[2026-05-25_slice-quote-pipeline]]
---

# Session Report — Gateway Compaction / Empty Response Fix

**Date:** 2026-05-25
**Agent:** Claude
**Session type:** Debug
**Trigger:** Telegram repeating "Auto-compaction could not recover" and "something went wrong while processing request" — Salomon was broken.

---

## Summary

Salomon's main session had accumulated a 1.3MB trajectory that triggered compaction on every Telegram message. Compaction failed because `reserveTokensFloor: 20000` exceeded qwen2.5:7b's 16384-token context window, causing the model to produce empty responses. The fix was removing the bad floor setting from `openclaw.json` and clearing the broken session. Gateway restarted clean, both Telegram and Discord connected without errors.

---

## What Was Built or Changed

- Removed `reserveTokensFloor: 20000` from `~/.openclaw/openclaw.json` — this was the root cause
- Cleared the broken session: archived `~/.openclaw/agents/main/sessions/a0bad3aa*.jsonl` and removed its entry from `sessions.json`
- Gateway restarted and confirmed running clean

---

## Technical Decisions

**Remove reserveTokensFloor entirely vs. lower it** — Removed it entirely (no key in config). A floor of 20000 meant OpenClaw reserved tokens that didn't exist in a 16384 window, breaking the budget math. Default (unset) is safe; if Salomon needs a floor later, 2000–4000 is appropriate for qwen2.5:7b.

**Clear session vs. let it compact** — Compaction was stuck in a loop: each attempt produced garbage output (empty payload, stopReason=stop), sent an error to Telegram, and retried. The session needed to be cleared, not repaired. Archived rather than deleted per the `trash > rm` rule.

---

## Files Created or Modified

```
~/.openclaw/openclaw.json                           reserveTokensFloor removed
~/.openclaw/agents/main/sessions/                   old broken session archived
```

---

## Tests & Validation

- `systemctl --user status openclaw-gateway.service` — Active: running
- Journal: no compaction errors, no empty-response errors, no fallback decisions
- Both Telegram (`@DjinnOCBot`) and Discord connected at startup

---

## Known Issues

- `~/.openclaw/agents/main/agent/models.json` appears to be managed/rewritten by the gateway on startup — contextWindow change to 32768 does not persist. Root cause not investigated; the fix (removing the floor) makes this a non-issue at 16384 since floor is gone.

---

## What's Next

- [ ] Salomon: send test message via Telegram to confirm clean response (Salomon lane)
- [ ] Confirm job 7 (GoPro_Tripod_raft) via Discord/Telegram (Salomon lane)
- [ ] Fix SYSTEM-STATE.md — stale printer queue, missing media agents
- [ ] Fix workspace/MEMORY.md — stale
- [ ] Fix PLAN.md — empty

---

— Claude, 2026-05-25
