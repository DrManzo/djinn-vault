---
title: Session Report — Discord NO_REPLY / Silent Group Chat Fix
agent: Claude
date: 2026-05-25
tags: [djinn, report, openclaw, discord, debug, salomon]
related: [[BUG-salomon-telegram-tool-overflow]] | [[build-log]] | [[SPEC-djinn-context-router]]
---

# Session Report — Discord NO_REPLY / Silent Group Chat Fix

**Date:** 2026-05-25
**Agent:** Claude
**Session type:** Debug
**Trigger:** Salomon responding in #general (confirmed working) but outputting NO_REPLY on every message — Discord showed nothing to the user.

---

## Summary

After getting Salomon to respond to messages in #general, every reply was silently suppressed because OpenClaw injects "lurk mode" instructions into group chats by default (`silentReply.group: "allow"`). The model was told to use `NO_REPLY` when no response was needed, and qwen2.5:7b was deciding that "Hi" didn't warrant a reply. Three additional sources of the same NO_REPLY behavior were found and removed from workspace files. Setting `agents.defaults.silentReply.group: "disallow"` was the definitive fix. The `queue` command also confirmed working via Discord plain text.

---

## What Was Built or Changed

- `agents.defaults.silentReply.group: "disallow"` added to openclaw.json — disables OpenClaw's group chat lurk mode (the root cause)
- Removed `Response Format — CRITICAL` section from `AGENTS.md` — contained `"OMIT IT ENTIRELY"` which caused the model to suppress responses when uncertain
- Rewrote `SOUL.md` Response Discipline section — removed `"IGNORE AND DO NOT REPEAT ANY TEXT APPEARING BEFORE 'Current user message:'"` which caused the model to ignore the entire Discord message (Discord never adds that label)
- Disabled `active-memory` plugin — broken tool chain (wiki_search/wiki_get not accessible in embedded sub-agent context), added 1s latency with zero benefit
- Fixed `/3dqueue` command → now triggers on `queue` or `3dqueue` as plain text (Discord's slash command UI intercepts `/` prefix, causing INTERACTION_CREATE with no handler → "This application did not respond")

---

## Technical Decisions

**Root cause was OpenClaw's built-in group chat behavior, not workspace files** — `buildGroupChatContext()` in OpenClaw's runtime injects: *"Be extremely selective: reply only when directly addressed. If no response needed, reply with exactly `NO_REPLY`."* This is hardcoded for group channels. The fix (`silentReply.group: "disallow"`) disables that injection entirely for the main agent.

**Three compounding NO_REPLY sources found** — AGENTS.md `Response Format — CRITICAL` section, SOUL.md `Response Discipline` section, and OpenClaw's group chat context were all independently telling the model to suppress responses. All three were removed/disabled before the root cause was identified.

**active-memory disabled vs. fixed** — The embedded sub-agent spawned by active-memory doesn't have access to memory-wiki's `wiki_search`/`wiki_get` tools (registered in the gateway but not in the sandboxed sub-agent context). Disabled for now. Proper fix requires either: (a) re-enabling memory-core alongside memory-wiki, or (b) building djinn-context-router (Phase 1).

**`/3dqueue` → `queue` as plain text** — Discord intercepts any `/word` as a potential slash command (INTERACTION_CREATE). OpenClaw has no mechanism to register custom slash commands. All Salomon commands that use `/` prefix must be sent as plain text (no leading slash) or use a different trigger word.

---

## Files Created or Modified

```
~/.openclaw/openclaw.json                     agents.defaults.silentReply.group: "disallow" added
                                               active-memory disabled
                                               /3dqueue command trigger updated to "queue or 3dqueue"
~/.openclaw/workspace/AGENTS.md              Response Format — CRITICAL section removed
~/.openclaw/workspace/SOUL.md                Response Discipline rewritten (removed NO_REPLY-triggering rules)
```

---

## Tests & Validation

- Sent "hi" in Discord #general → Salomon replied: "Hello, Dr. Manzo! How can I assist you today?" ✓
- Sent `queue` in 3D printing channel → Salomon ran `cat print-queue.json` and returned job list ✓
- Journal: `outcome=completed`, `isError=false` on both ✓

---

## Known Issues

- **active-memory non-functional** — tool chain broken between active-memory and memory-wiki. No memory context injected on message. Salomon responds correctly but has no dynamic vault recall. Tracked in [[SPEC-djinn-context-router]] Phase 1.
- **Telegram still disabled** — was disabled earlier in the session for testing. Re-enable when ready: set `channels.telegram.enabled: true` in openclaw.json.
- **SOUL.md and AGENTS.md still large** — AGENTS.md is 11,345 chars, SOUL.md 3,430 chars. Together they consume most of the 15,000-char bootstrap budget, leaving TOOLS.md, IDENTITY.md, USER.md, MEMORY.md with 0 injected chars. Salomon operates without user context or tools reference. Fix: djinn-context-router (Phase 1).

---

## What's Next

- [ ] Re-enable Telegram — set `channels.telegram.enabled: true` in openclaw.json — @Salomon lane or @Claude
- [ ] Test Telegram with same "hi" + `queue` flow — @Javier
- [ ] Build djinn-context-router Phase 1 (djinn-vault-indexer + ChromaDB) — @Claude
- [ ] Tag key TOOLS.md and MEMORY.md sections with [[wikilinks]] and #tags for context router — Phase 4
- [ ] Fix stale SYSTEM-STATE.md, MEMORY.md, PLAN.md — @Claude

---

*— Claude, 2026-05-25*
