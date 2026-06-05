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

---

### BUG-013 — PrusaSlicer ignores SupportBlocker for multi-instance 3MF

**Date:** 2026-06-05
**System:** 3D printing / PrusaSlicer 2.9.4
**Severity:** medium
**Status:** workaround (gcode post-processor)

**Symptom:** 3MF with `volume_type="SupportBlocker"` in `Slic3r_PE_model.config` produces correct gcode when there is one `<item>` in the build section. With 3 `<item>` elements referencing the same object ID, PS treats the blocker mesh as printable geometry → gcode has 583g/31h instead of 372g/22h.

**Root cause:** PrusaSlicer multi-instance handling does not correctly propagate volume type config to all instances when build items share an object ID. The `SupportBlocker` designation is ignored and the modifier mesh is printed as solid.

**Workaround:** Use `djinn-gcode-support-cap INPUT OUTPUT Z_MM` to strip support extrusion above Z_MM after slicing.

**Lesson:** Test multi-instance 3MF blocker separately from single-instance. Single-instance works; multi-instance requires gcode post-processing.

*— Claude*

---

### BUG-014 — Calliope nozzle_mcu UART disconnect (E0003 / key561)

**Date:** 2026-06-05
**System:** Hardware — Calliope (Ender-3 V3 Plus)
**Severity:** high
**Status:** open — physical fix required

**Symptom:** Klipper hard-shutdown with `E0003：key2561 communication abnormal` on LCD. Moonraker shows `printing → paused → standby`. klippy.log: `Lost communication with MCU 'nozzle_mcu'` (code: key561). Happened 3× on 2026-06-05: 14:24, 14:31, 15:34.

**Root cause:** nozzle_mcu UART cable bundle has insufficient slack or routing relief. Wide XY travel (bed leveling mesh probe at print start, 3× plate spanning X=27–273mm) pulls or kinks the cable and drops the serial connection. Klipper kills all motion on MCU timeout.

**Why it wasn't obvious earlier:** Single centered prints don't traverse the full bed width — cable stays within a safe range. Wide-travel operations (multi-object plates, bed leveling) exceed the cable's slack budget.

**Fix:** Physical re-route of nozzle_mcu cable harness. Add cable relief so harness has slack in all XY positions at all Z heights. Possible approaches: re-clip the cable chain, add a strain relief loop, or extend the cable run.

**Workaround until fixed:** Disable or reduce bed leveling probe grid in START_PRINT macro to minimize XY travel at print start. Avoid 3× wide plates.

**Lesson:** E0003/key561 on Ender-3 V3 Plus = nozzle_mcu UART loss = cable, not firmware, not filament, not Z height alone. Check klippy.log for `Lost communication with MCU 'nozzle_mcu'` to confirm.

*— Claude*
