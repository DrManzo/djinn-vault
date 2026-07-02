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
| 2026-06-08 | Claude | djinn-print-track v2 | low | fixed | WebSocket message with str instead of dict status crashes `_handle_ws_message` — daemon self-recovered via reconnect backoff | [[2026-06-08_bug-ws-message-str-status]] |

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

### BUG-014 UPDATE — 2026-06-05
Cable reroute performed but dropouts continue. All 11 shutdown events confirmed at Z < 10mm (early layers). XY positions scattered. Root cause refined: **connector at nozzle_mcu board is loose or cable has internal damage**. Not a routing/slack issue. Next step: replace connector or cable harness.

### BUG-014 UPDATE — 2026-06-05 (2nd occurrence)
**12th dropout** at Z=4.2mm, 20 min into Camood_TTHQ_job17 (PrusaSlicer, 220°C/55°C, fan S128). Dropout occurred at 22:34:33 PDT. Klipper auto-restarted but power-loss recovery got stuck (empty filename in recovery state). Print cancelled.

Connector reseat (2026-06-03) did **not** permanently fix the issue — dropout recurred after 3 days. Board or cable needs replacement, not reseat.

**Impact:** Blocks all prints until fixed. Both Orca (ECO temp issue, worked around by PrusaSlicer gcode structure) and PrusaSlicer (temperature correct, but nozzle_mcu drops out) approaches fail at Z<10mm due to this hardware issue.

### BUG-014 UPDATE — 2026-06-28 (recurrence after 23-day gap)
Two key561 dropouts today during Camood PETG prints:
1. **06:36:59 PDT** — Camood_TTHQ_engraved: dropout during END_PRINT parking gcode (6 seconds after `Finished SD card print`). Part was complete. Position: X=10, Y=295, Z=165 (park position). Klipper crashed in end-gcode only, part is physically fine.
2. **20:01:17 PDT** — Camood_clean-marked: dropout mid-print at Z=47.92mm (~45% of 107mm body). Part SCRAPPED.

Both confirmed `Timeout with MCU 'nozzle_mcu'` → key561. Connector reseat from 2026-06-03 lasted 23 days before failure. **Cable or board replacement is now required — reseat is not sufficient.**

| 2026-06-07 | Claude | clerk | low | fixed | clerk-watch wrong RAW_PATH | [[2026-06-07_bug-clerk-watch-wrong-raw-path]] |


## 2026-06-11 — djinn-bughunter scan (1 finding(s))
- **[HIGH]** `/tmp/djinn-marcus-sync.log` — unhandled exception _(type: errlog)_


## 2026-06-11 — djinn-bughunter scan (1 finding(s))
- **[HIGH]** `journald:djinn-telegram-gateway` — unhandled exception (1 occurrence(s)) _(type: errlog)_
| 2026-06-14 | Claude | forge-slicer | high | wont-fix | CrealityPrint v6+ CLI --slice 0 segfault | [[2026-06-14_bug-crealityprint-v6-cli-slice-0-segfault]] |
| 2026-06-15 | Claude | djinn-webcam-monitor | medium | fixed | Milestone clips wrote 1 frame per 10s — clips were 33ms not 10s | [[2026-06-15_bug-webcam-milestone-clip-framerate]] |


## 2026-06-15 — djinn-bughunter scan (1 finding(s))
- **[HIGH]** `journald:djinn-discord-gateway` — unhandled exception (159 occurrence(s)) _(type: errlog)_


## 2026-06-15 — djinn-bughunter scan (1 finding(s))
- **[HIGH]** `journald:djinn-discord-gateway` — unhandled exception (44 occurrence(s)) _(type: errlog)_


## 2026-06-16 — djinn-bughunter scan (1 finding(s))
- **[HIGH]** `journald:djinn-discord-gateway` — unhandled exception (22 occurrence(s)) _(type: errlog)_


## 2026-06-17 — djinn-bughunter scan (1 finding(s))
- **[HIGH]** `journald:djinn-discord-gateway` — unhandled exception (2 occurrence(s)) _(type: errlog)_


## 2026-06-17 — djinn-bughunter scan (1 finding(s))
- **[HIGH]** `journald:djinn-discord-gateway` — unhandled exception (12 occurrence(s)) _(type: errlog)_

| 2026-06-18 | Claude | TASK-080 diagnostic | medium | fixed | pyembree hasattr false positive — hasattr() doesn't catch deferred import errors | [[2026-06-18_bug-pyembree-hasattr-false-positive]] |
| 2026-06-18 | Claude | djinn-blender-repair | high | fixed | repair.py --report required path arg — wrapper treated as bool flag, tool dead on first run | [[2026-06-18_bug-blender-repair-report-arg-mismatch]] |
| 2026-06-18 | Claude | djinn-blender-render | high | fixed | BLENDER_EEVEE_NEXT not valid in snap Blender 5.1.2 — correct name is BLENDER_EEVEE | [[2026-06-18_bug-blender-eevee-next-engine-name]] |
| 2026-06-18 | Claude | djinn-blender-render | medium | fixed | render.py hardcoded PNG format — output extension ignored, .jpg saved as PNG bytes | [[2026-06-18_bug-blender-render-format-hardcoded-png]] |
| 2026-06-18 | Claude | djinn-discord-gateway | high | open | build TASK-NNN falls through to Ollama with no QUEUE context — silent hallucinated output | [[2026-06-18_bug-gateway-build-command-no-queue-context]] |

| 2026-06-21 | Claude | Penelope/OctoPrint | high | fixed | OctoPrint alwaysSendChecksum causes Marlin resend loop — printer requests line 1 indefinitely, comm deadlocked | [[2026-06-21_bug-octoprint-checksum-marlin-resend-loop]] |
| 2026-06-21 | Claude | Penelope/Creality Print | high | documented | Creality Print V7 gcode contains Klipper macros (START_PRINT, EXCLUDE_OBJECT) — silently fails on Marlin, bed never heats | [[2026-06-21_bug-creality-print-klipper-macros-on-marlin]] |
| 2026-06-21 | Claude | Penelope/Z offset | medium | fixed | Z offset not configured on Penelope — nozzle 0.5mm too high, first layer ghosted/non-adhesive | [[2026-06-21_bug-penelope-z-offset-unconfigured]] |


## 2026-06-28 — djinn-bughunter scan (1 finding(s))
- **[HIGH]** `journald:djinn-clerk` — OOM (1 occurrence(s)) _(type: errlog)_

| 2026-06-28 | Claude | Calliope / nozzle_mcu UART | high | open | BUG-014 recurring — key561 nozzle_mcu dropout killed Camood_clean-marked at Z=47.92mm (part scrapped). Also hit end-gcode of TTHQ engraved print (part OK). Connector reseat June 3 lasted 23 days — cable/board replacement now required. | [[2026-06-28_bug-camood-petg-start]] |


## 2026-06-29 — djinn-bughunter scan (1 finding(s))
- **[HIGH]** `journald:djinn-telegram-gateway` — unhandled exception (2 occurrence(s)) _(type: errlog)_

### BUG-014 UPDATE — 2026-06-29 (root cause confirmed, print completed)
Cable reseat performed by Javier — good slack restored. Camood (simple solid, no engraving, maker's mark only) printed to completion at 106mm with gyroid infill. No key561 errors at any point.

**Root cause confirmed:** key561 dropouts are caused by specific XY toolpath positions generated by engraving/emboss geometry pulling the cable to the connector stress point. Simple solid geometry = centered toolpaths = cable stays in safe range = no dropout.

**key561 errors are symptoms, not causes.** Sequence: XY toolpath pulls cable → connector loses contact → Klipper detects MCU timeout → key561 → emergency stop. The errors do nothing to the hardware — they are Klipper's reaction to the lost connection.

**Software workarounds (fan cap, thermal soak, 3×3 mesh, TRSYNC) all reverted — none helped.** Thermal soak may have been making it worse by pre-stressing the connector before motion started. Stock config is correct.

**Validated Calliope print rules:**
1. Single merged body — no separate engraving/emboss shells (Blender union before slicing)
2. Gyroid safe for simple solids; rectilinear/grid for engraved/embossed geometry
3. Cable slack is the real fix — reseat with proper relief routing

| 2026-07-01 | Claude | Typhon onboarding | medium | open | `setup-typhon.ps1` post-reboot instructions curl a `djinn/scripts/bootstrap-node.sh` that was never created — blocks WSL2-side Djinn install once the Windows setup script runs | [[2026-07-01_bug-typhon-bootstrap-node-missing]] |
| 2026-07-01 | Claude | Typhon / Windows SSH | medium | workaround | GUI installers (OrcaSlicer) and tray-apps (Ollama, Claude Code wizard) launched over SSH hang or crash — Session 0 isolation blocks UI init. Archive-extraction bypass found for OrcaSlicer; Ollama server still needs a human interactive session to start | [[2026-07-01_bug-typhon-session0-noninteractive-hangs]] |
| 2026-07-01 | Claude | Print library migration / GNU tar | low | fixed | `tar --exclude` patterns placed after the file/dir argument are silently ignored (GNU tar 1.35) — one Camood file leaked into a transfer to Typhon before the ordering bug was caught via post-transfer verification and fixed | [[2026-07-01_print-library-migration]] |


## 2026-07-01 — djinn-bughunter scan (1 finding(s))
- **[HIGH]** `journald:djinn-discord-gateway` — unhandled exception (18 occurrence(s)) _(type: errlog)_
