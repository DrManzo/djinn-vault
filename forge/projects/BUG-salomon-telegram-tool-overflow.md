---
title: "BUG: Salomon Telegram — Unsolicited Tool Calls Overflow Context → 'Something Went Wrong'"
status: open
priority: high
assigned_to: Claude
date: 2026-05-25
tags: [bug, salomon, telegram, openclaw, qwen2.5, context-overflow]
---

# BUG: Salomon Telegram — Unsolicited Tool Calls Overflow Context

## Summary

Salomon (qwen2.5:7b via OpenClaw gateway, Telegram channel) keeps making unsolicited tool calls on session startup — bash file reads and `web_fetch` — without any user command. This fills up the 16384-token context window within 2–3 messages. When the session hits the compaction threshold, compaction either fails or the model returns an empty response (`payloads=0, stopReason=stop`). Telegram receives "something went wrong / please try again."

The user cannot have a basic conversation on Telegram without hitting this error.

---

## Confirmed Root Cause

qwen2.5:7b is following startup instructions embedded in the workspace files it receives in its system prompt. Two confirmed triggers:

**1. AGENTS.md** — previously said:
```
## Session Startup
Read these files at the start of each session:
- IDENTITY.md, SOUL.md, USER.md, TOOLS.md, SCHEDULE.md, MEMORY.md, PLAN.md
Then run the sync workflow before anything else: workflows/djinn-sync.md
```
→ **Partially fixed:** replaced with "files are auto-loaded, respond directly." Still may not be obeyed reliably.

**2. SOUL.md** — still says:
```
## Continuity
Each session, you wake up fresh. These files are your memory. Read them. Update them.
```
→ **NOT fixed yet.** This directly tells the model to read files.

**3. Post-compaction context refresh message** — OpenClaw injects a system message:
```
Session was just compacted. The conversation summary above is a hint, NOT a substitute
for your startup sequence. R[ead these files...]
```
→ This fires even on fresh sessions (confirmed in session jsonl). It re-triggers the startup sequence every time.

**4. HEARTBEAT.md / djinn-sync** — session contributor log showed a `web_fetch` tool result (2163 chars) before `/3dqueue` was even sent. Likely triggered by a heartbeat check URL or djinn-sync workflow step.

---

## What Has Been Tried (This Session)

| Fix | Applied | Result |
|-----|---------|--------|
| Remove `reserveTokensFloor: 20000` from openclaw.json | ✅ | Fixed original crash; floor now 3000 |
| Disable memory-core plugin | ✅ | `/dreaming` tool removed from context |
| AGENTS.md startup section rewritten | ✅ | Now says "files are auto-loaded, respond directly" |
| Added CRITICAL RULES prefix to `systemPromptOverride` in openclaw.json | ✅ | 5 rules: no tools on startup, no file reads, no web_fetch, no background tasks, files already loaded |
| Session clear + gateway restart after each failure | ✅ (repeated) | Temporary relief only; next session re-breaks |

---

## What Still Needs To Be Fixed

### Fix 1 — SOUL.md "Read them" instruction
`~/.openclaw/workspace/SOUL.md`, Continuity section:

Change:
```
Each session, you wake up fresh. These files are your memory. Read them. Update them. They're how you persist.
```
To:
```
Each session, you wake up fresh. These files are your memory — they are automatically loaded by the system. Do NOT read them with bash. They are already in your context.
```

### Fix 2 — Find and remove web_fetch trigger
The last broken session had a `web_fetch` tool result (2163 chars) as the biggest context contributor. Need to identify:
- What URL was fetched
- Which file/instruction triggered it (likely HEARTBEAT.md or djinn-sync workflow)

Check: `~/.openclaw/workspace/HEARTBEAT.md` — if it contains URLs or "check this URL" instructions, those need to be converted to read-only notes (no action trigger).

Check: `~/.openclaw/workspace/workflows/djinn-sync.md` — if it says "run on startup", remove that.

### Fix 3 — Post-compaction context refresh message
OpenClaw injects a "run your startup sequence" message even in fresh sessions (confirmed via session jsonl role `compactionSummary`). This message overrides all our prompt rules.

Options:
- Find where this message is configured in OpenClaw and remove/override it
- Or make the message say "DO NOT run startup sequence — all files are already loaded" instead

Look in: `~/.nvm/versions/node/v22.22.3/lib/node_modules/openclaw/dist/extensions/memory-core/` and the main runtime for where `compactionSummary` messages are generated.

### Fix 4 — Reduce workspace file injections
Currently injecting: AGENTS.md (8995 chars), SOUL.md (3371), TOOLS.md (5147), IDENTITY.md (1218), USER.md (9378), HEARTBEAT.md (1658), MEMORY.md (8449).

Total: ~38,000 chars ≈ ~9,500 tokens, which is already 58% of qwen2.5:7b's 16384-token window before a single message is sent.

Consider: only inject the files the agent actually needs at runtime. IDENTITY.md, USER.md, and MEMORY.md cover persona and context. AGENTS.md has the routing rules. SOUL.md and TOOLS.md may be redundant given the systemPromptOverride already contains the core rules.

Check which files are configured for injection in: `~/.openclaw/openclaw.json` → `agents.list[id=main].workspace` and the gateway's workspace loader logic.

---

## How to Verify a Fix

1. Clear the Telegram session (see procedure below)
2. Start the gateway
3. Send "hi" on Telegram
4. Salomon should reply in plain text with no tool calls
5. Send `/3dqueue`
6. Salomon should call `bash cat /home/drmanzo/.local/share/djinn/print-queue.json` and return the job list
7. Check journal: `journalctl --user -u openclaw-gateway.service --since "2 minutes ago" --no-pager | grep -E "tool|web_fetch|incomplete|fallback"`
8. Should see: one tool call for `/3dqueue`, no web_fetch, no incomplete terminal response

---

## Session Clear Procedure (use between attempts)

```bash
systemctl --user stop openclaw-gateway.service

python3 - << 'EOF'
import json, os, shutil
sessions_path = "/home/drmanzo/.openclaw/agents/main/sessions/sessions.json"
archive_dir = "/home/drmanzo/.openclaw/agents/main/sessions/archive"
sessions_dir = "/home/drmanzo/.openclaw/agents/main/sessions"
data = json.load(open(sessions_path))
tg_keys = [k for k in data if "telegram" in k]
for k in tg_keys:
    sid = data[k].get("sessionId", "")
    for f in os.listdir(sessions_dir):
        if sid and sid in f and os.path.isfile(os.path.join(sessions_dir, f)):
            shutil.move(os.path.join(sessions_dir, f), os.path.join(archive_dir, f))
    del data[k]
with open(sessions_path, "w") as f:
    json.dump(data, f, indent=2)
print("Done.")
EOF

systemctl --user start openclaw-gateway.service
```

---

## Key File Locations

| File | Purpose |
|------|---------|
| `~/.openclaw/openclaw.json` | Main config: reserveTokensFloor, systemPromptOverride, plugin toggles |
| `~/.openclaw/workspace/AGENTS.md` | Workspace file injected into Salomon — startup rules live here |
| `~/.openclaw/workspace/SOUL.md` | Behavioral rules — still contains "Read them" trigger |
| `~/.openclaw/workspace/HEARTBEAT.md` | Likely contains web_fetch trigger URL |
| `~/.openclaw/workspace/workflows/djinn-sync.md` | Sync workflow — may trigger on startup |
| `~/.openclaw/agents/main/sessions/` | Active session jsonl files |

---

## Current State (as of 2026-05-25 ~11:00 PDT)

- Gateway: running, 9 plugins (memory-core disabled)
- reserveTokensFloor: 3000
- AGENTS.md startup: fixed (OVERRIDE text added to counter compaction preamble)
- SOUL.md: fixed ("Read them. Update them." → "auto-loaded, do NOT read with bash")
- djinn-sync.md: fixed (removed "Always: At session start" trigger)
- HEARTBEAT.md workspace: fixed ("Proactive Work (no asking needed)" → "only when asked")
- Post-compaction message: partially mitigated — postCompactionSections set explicitly to ["Session Startup", "Red Lines"]; Session Startup now starts with OVERRIDE instruction countering the preamble
- Post-compaction preamble text "Run your startup sequence": still hardcoded in compiled JS (selection-hR-AeOeU.js:6467) — cannot fix without editing bundle
- web_fetch trigger: HEARTBEAT.md workspace had "Proactive Work (no asking needed): Check git status on forge repo" — removed. If web_fetch persists, suspect HEARTBEAT.md in communications/ or djinn-sync step 4 (reads HEARTBEAT files which may contain external URLs)

## Additional Fixes Applied (2026-05-25 ~11:25 PDT)

- **Root cause confirmed:** compaction summaries were hallucinated garbage ("Implement ML model for stock prices") every cycle because qwen2.5:7b cannot produce coherent summaries under context pressure
- **Compaction mode:** set to `safeguard` — stricter guardrails, preserves recent context
- **Quality guard:** enabled with maxRetries=2 — rejects bad summaries and retries
- **bootstrapTotalMaxChars:** 15000 — caps workspace file injection (was ~38000 chars = 9500 tokens = 58% of 16384-token window)
- **Note:** `compaction.model` to route summaries to phi4:14b failed schema validation (expected string but format unclear) — left as default (qwen2.5:7b) for now; qualityGuard+safeguard mode should compensate
- **Telegram session:** cleared again post-fix
- **Gateway:** running as of 11:25 PDT

## Remaining Risk

If web_fetch still fires: djinn-sync step 4 reads HEARTBEAT-typhon.md which may contain Typhon's IP or a URL in the machine status. Check that file for URLs if the error returns.

If qwen2.5:7b still produces garbage compaction summaries despite qualityGuard: the correct fix is `compaction.model` but the valid string format for Ollama models is unknown — needs openclaw docs or source investigation to find the right enum/format.

— Claude, 2026-05-25
