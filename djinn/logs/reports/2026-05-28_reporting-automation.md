---
title: Session Report — Reporting Automation Infrastructure
agent: Claude
date: 2026-05-28
tags: [djinn, automation, reporting, protocol, bugs]
related: [[PROTOCOL]] | [[build-log]] | [[bugs]]
---

# Session Report — Reporting Automation Infrastructure

**Date:** 2026-05-28  
**Agent:** Claude  
**Session type:** Architecture  
**Trigger:** Javier: "I need you to also have all of the agents and AIs — Salomon, Claude, Typhon — always write a report of the thing that they did and log it especially when bugs come up. That is information that needs to be automated if it's not yet."

---

## Summary

Formalized and extended the reporting infrastructure for all Djinn agents. Added a bug log, a bug report template, a `djinn-bugreport` CLI script (deployed to Salomon and Typhon), a `djinn-session-end` script with report enforcement, and updated PROTOCOL.md and CLAUDE.md with explicit bug reporting requirements. The goal: no session ends without a report, and bugs are never silently absorbed — they get a structured record that future agents can learn from.

---

## What Was Built or Changed

### New Files — Vault

**`djinn/logs/BUG-REPORT-TEMPLATE.md`**  
Structured template for bug reports. Sections: Symptom, Steps to Reproduce, Root Cause, Fix Applied, Verification, Rule/Lesson. The "Rule" section is the key one — it extracts the generalizable lesson and feeds it back into agent context.

**`djinn/logs/bugs.md`**  
Running flat index of all bugs. One row per bug: date, agent, system, severity, status, summary, link to full report. Machine-readable enough for future agents to query. Auto-updated by `djinn-bugreport`.

### New Scripts — Salomon (`~/.local/bin/`)

**`djinn-bugreport`**
```
Usage: djinn-bugreport "Title" "Root cause summary" [system] [severity] [status]
```
- Creates a timestamped bug report in `djinn/logs/reports/YYYY-MM-DD_bug-<slug>.md`
- Appends one-liner to `djinn/logs/bugs.md`
- Appends entry to `build-log.md`
- Commits and pushes vault
- Sends Telegram notification if `DJINN_TELEGRAM_TOKEN` / `DJINN_CHAT_ID` are set
- Any agent — Claude, Salomon opencode, or a future automated process — can call this

**`djinn-session-end`**
```
Usage: djinn-session-end "session-slug" "one-line summary"
```
- Checks if a report was written in `djinn/logs/reports/` within the last 2 hours that contains today's date in its filename
- If NOT: generates a minimal report stub from the slug and summary, appends to build-log, and sends a Telegram warning "⚠️ Session ended without full report — stub created"
- If YES: appends to COMMS.md and pushes
- Intended to be called at the end of every opencode session on Salomon and Typhon

### Updated Files

**`djinn/communications/PROTOCOL.md`** — added Bug Report section; added `djinn-bugreport` and `djinn-session-end` to the agent contract; added enforcement note.

**`~/.claude/CLAUDE.md`** — added explicit bug reporting requirement: any bug discovered, diagnosed, or fixed must produce a bug report entry (via `djinn-bugreport` or manually in bugs.md) in addition to the session report.

---

## The Reporting Contract (Summary)

Every agent must do this at session end — no exceptions, no "I'll do it next time":

```
1. Write session report  →  djinn/logs/reports/YYYY-MM-DD_<slug>.md
2. Append to build-log   →  djinn/logs/build-log.md
3. If bug found/fixed    →  djinn-bugreport "title" "root cause" [system] [severity]
4. Append to COMMS.md    →  one entry per session
5. git add -A && git commit && git push
```

For Salomon opencode: `djinn-session-end` is called by the comms-processor wrapper after every opencode invocation. It checks for a report and generates a stub if one is missing.

For Claude: the session protocol in CLAUDE.md is binding. Bug reports are now an explicit line item, not implied.

---

## Files Created / Modified

| File | Status |
|------|--------|
| `djinn/logs/BUG-REPORT-TEMPLATE.md` | Created |
| `djinn/logs/bugs.md` | Created (pre-populated with 2 known bugs) |
| `djinn/logs/reports/2026-05-28_reporting-automation.md` | Created (this file) |
| `~/.local/bin/djinn-bugreport` | Created + chmod +x |
| `~/.local/bin/djinn-session-end` | Created + chmod +x |
| `djinn/communications/PROTOCOL.md` | Updated — bug reporting section |
| `~/.claude/CLAUDE.md` | Updated — explicit bug report requirement |

---

## Tests & Validation

| Test | Result |
|------|--------|
| `djinn-bugreport --help` | ✅ Usage printed |
| `djinn-bugreport "test" "test cause" "studio" "low" "fixed"` | ✅ Report created, bugs.md updated, pushed |
| `djinn-session-end` with no recent report | ✅ Stub created, Telegram warning fired |
| `djinn-session-end` with recent report | ✅ COMMS.md updated, pushed cleanly |

---

## Known Issues

- **Salomon comms-processor integration** — `djinn-session-end` is written but not yet wired into the comms-processor's opencode invocation wrapper. Salomon needs to update the wrapper script. Left a message in COMMS.md.
- **Typhon opencode** — Typhon doesn't run opencode sessions currently, but the script is deployed there for future use.

---

## What's Next

- [ ] Wire `djinn-session-end` into Salomon's opencode invocation — @Salomon
- [ ] Test Telegram notification from `djinn-bugreport` end-to-end — @Javier
- [ ] Add `djinn-bugreport` alias to opencode's AGENTS.md so Salomon knows to call it — @Salomon

---

*— Claude, 2026-05-28*
