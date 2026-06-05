---
subject: Djinn Bug Log
tags: [djinn, bugs]
created: 2026-05-28
---

# Bug Log

Running index of all bugs discovered across Djinn systems. Each entry links to a full bug report.

| Date | Agent | System | Severity | Status | Summary | Report |
|------|-------|--------|----------|--------|---------|--------|
| 2026-05-28 | Claude | Typhon Studio / Vue 3 frontend | medium | fixed | `_tsToTime` prefixed with `_` — Vue 3 drops `_`-prefixed properties from template proxy; caused silent ReferenceError → browser reload loop | [[2026-05-28_typhons-studio-guardian-final]] |
| 2026-05-28 | Claude | Typhon Studio / copilot_agent.py | high | fixed | SyntaxError on line 109 — bad `sed` replacement broke f-string in `log.warning()` line; service failed to import | [[2026-05-28_typhons-studio-phase5]] |

---

*Auto-updated by `djinn-bugreport`. Full reports in `reports/`.*
| 2026-05-28 | Claude | djinn-discord-watcher | high | fixed | openclaw not in systemd PATH — Discord sends fail | [[2026-05-28_bug-openclaw-not-in-systemd-path-discord-sends-fail]] |
| 2026-05-28 | Claude | djinn-discord-watcher | medium | fixed | trimesh headless render fails — no DISPLAY in systemd service | [[2026-05-28_bug-trimesh-headless-render-fails-no-display-in-systemd-service]] |
| 2026-05-30 | Print | cup_engraved_FINAL / Job #2 | low | open | Engraving shallow at letter edges (T crossbar, e curve) due to cup surface curvature; tank underside rough — supports needed | [[print-2026-05-30-job2-model]] |
| 2026-05-31 | Claude | djinn-print-consult | medium | open | Maker's mark engraving reads reversed on bottom surfaces | [[2026-05-31_bug-maker-s-mark-engraving-reads-reversed-on-bottom-surfaces]] |

---
## BUG-013 — Djinn voice too terse on conversational messages
- **Date:** 2026-05-31
- **System:** djinn-telegram-gateway / djinn-discord-gateway
- **Severity:** low
- **Status:** open
- **Root cause:** Model (llama-3.3-70b-versatile) treats short social messages ("thank you") as small talk and gives minimal responses. SOUL.md identity is loaded but the model defaults to brevity on non-command input. Needs prompt tuning to distinguish between command formatting (be concise) and presence/conversation (be Djinn).
- **Fix:** Adjust system prompt to explicitly instruct the model to respond with full presence on conversational messages, not just acknowledge. Possible: add temperature nudge or separate conversational instruction block.
| 2026-06-01 | Claude | openclaw / qwen2.5:7b main agent | high | fixed | Agent hallucinates task specs instead of reading QUEUE.md — invented SQLite tutorials for TASK-054 | [[2026-06-01_bug-agent-hallucinating-task-specs]] |

| 2026-06-02 | Claude | djinn-model-text-engrave / PrusaSlicer bridge | high | open | No bridge between PrusaSlicer visual text placement and djinn FDM engraving parameters — operator intent cannot be translated to tool coordinates | [[2026-06-02_bug-engraving-placement-bridge]] |
| 2026-06-03 | Javier+Claude | calliope | high | fixed | nozzle_mcu physical dropout (bytes_invalid=0): loose frame cross-support brace caused frame flex → cable stress at specific toolhead positions. Tightened 2026-06-03. | [[2026-06-02_bug-calliope-nozzle-mcu-cable-loses-comms-under-print-vibration]] |

| 2026-06-02 | Claude | calliope / PrusaSlicer | high | fixed | M106 S255 at bridge infill creates EMI spike → instant key561 nozzle_mcu comms loss. Fix: cap fan at S128. Misdiagnosed as cable for most of session. | [[2026-06-02_calliope-m106-emi-root-cause]] |

| 2026-06-04 | Claude | OpenClaw / openclaw.json | high | fixed | `agents.defaults.bootstrapTotalMaxChars` was 15000 — OpenClaw silently loaded only AGENTS.md + partial SOUL.md, dropping USER.md, IDENTITY.md, TOOLS.md, HEARTBEAT.md, MEMORY.md. Djinn had no identity, didn't know Javier. Fix: raised limit to 60000, added bootstrapMaxChars 15000. | [[2026-06-04_openclaw-bootstrap-fix]] |
