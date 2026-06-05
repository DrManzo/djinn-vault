---
title: Session Report — OpenClaw Bootstrap Context Fix
agent: Claude
date: 2026-06-04
tags: [djinn, report, openclaw, bootstrap, config, fix]
related: [[build-log]] [[bugs]]
---

# Session Report — OpenClaw Bootstrap Context Fix

**Date:** 2026-06-04
**Agent:** Claude
**Session type:** Debug / Config
**Trigger:** Javier ran `openclaw tui`, found Djinn acting like a generic assistant — no knowledge of who Javier is, couldn't identify itself as Djinn.

---

## Summary

Diagnosed and fixed a silent config truncation bug: `agents.defaults.bootstrapTotalMaxChars` was set to 15000, causing OpenClaw to load only AGENTS.md (truncated) + a partial SOUL.md, dropping USER.md, IDENTITY.md, TOOLS.md, HEARTBEAT.md, and MEMORY.md entirely. Djinn had no identity and didn't know Javier because those files were silently excluded at session start. Increased limit to 60000 (the framework default) and added `bootstrapMaxChars: 15000` (per-file) to handle AGENTS.md at 12175 chars. Gateway restarted cleanly; all 7 workspace files now load (49,653 total chars).

---

## What Was Built or Changed

- `~/.openclaw/openclaw.json` — `agents.defaults.bootstrapTotalMaxChars`: 15000 → 60000; `agents.defaults.bootstrapMaxChars` added at 15000
- OpenClaw gateway restarted (`systemctl --user restart openclaw-gateway`)
- Attempted (and reverted) invalid `bootstrapFiles` key — not a valid per-agent config key in this OpenClaw version

---

## Technical Decisions

**Set total limit to 60000, not 50000 — Why:** 60000 is the framework default (`agents.defaults.bootstrapTotalMaxChars` docstring says "default: 60000"). Using the framework default gives headroom for workspace growth without hitting the ceiling again.

**Per-file limit set to 15000, not 12000 — Why:** The OpenClaw default per-file limit is 12000. AGENTS.md is 12175 chars — slightly over. Setting 15000 avoids silent truncation of the routing table.

**Did NOT try to reduce workspace file sizes — Why:** The 7 files total 49,653 chars. qwen2.5:7b has a 32K token context but the system prompt + bootstrap fit within budget. Trimming workspace files is premature; fix the constraint first.

**Reverted `bootstrapFiles: ["CONTEXT.md"]` — Why:** OpenClaw's Zod schema validation rejected it with "Unrecognized key" and the gateway crashed. The correct mechanism is adjusting the per-agent/default `bootstrapTotalMaxChars`, not specifying files explicitly.

---

## Files Created or Modified

```
~/.openclaw/openclaw.json     ← bootstrapTotalMaxChars 15000→60000, bootstrapMaxChars added at 15000
```

---

## Tests & Validation

```
Before fix (15000 total):
  AGENTS.md   12000/12175  (truncated at per-file limit)
  SOUL.md      3000/3308   (partially truncated, 15000 budget exhausted)
  TOOLS.md        0        (dropped)
  IDENTITY.md     0        (dropped)
  USER.md         0        (dropped)
  HEARTBEAT.md    0        (dropped)
  MEMORY.md       0        (dropped)

After fix (60000 total / 15000 per-file):
  AGENTS.md   12175        ✓ full
  SOUL.md      3308        ✓ full
  TOOLS.md     8021        ✓ full
  IDENTITY.md  1231        ✓ full
  USER.md     11739        ✓ full
  HEARTBEAT.md 1592        ✓ full
  MEMORY.md   11587        ✓ full
  Total:      49653        ✓ under 60000
```

- `openclaw doctor` — clean after restart (no bootstrap errors)
- `systemctl --user is-active openclaw-gateway` → `active`

---

## Known Issues / Caveats

- Total system prompt for main agent (systemPromptOverride ~12K + bootstrap ~50K = ~62K chars ≈ 15K tokens). qwen2.5:7b context is 32K tokens — tight but feasible for typical short conversations. Watch for context forgetting if sessions run very long.
- MEMORY.md in the workspace (11587 chars) is separate from Claude's memory system at `~/.claude/projects/`. Djinn's MEMORY.md should be kept current by Salomon.

---

## What's Next

- [ ] Test `openclaw tui` — verify Djinn knows who Javier is — @Javier
- [ ] Compute natal chart: April 4, 1994, 00:55 AM, Los Angeles CA → update USER.md Astrology Rising/Ascendant — @Claude
- [ ] Update `camood.md` print history when Job 9 completes — @Claude
- [ ] TASK-027: Fill SHIPPO_API_KEY in `~/.config/forge/shop.env` — @Javier
- [ ] TASK-063: Studio first-run (Cloudflare tunnel, Meta credentials, YouTube OAuth) — @Claude

---

*— Claude, 2026-06-04*
