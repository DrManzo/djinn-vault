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
| 2026-07-03 | Claude | Iris / bambufy | medium | open | `_START_BAMBUFY` delayed gcode doesn't load on zmod Klipper — init must be triggered manually after restart | [[2026-07-03_bug-bambufy-start-not-loading-zmod]] |
| 2026-07-03 | Claude | Iris / bambufy | low | open | `shoot_y_position=223` causes "Move out of range" at Y=234.7 during long retractions — may need lowering to 218 | [[2026-07-03_bug-bambufy-shoot-y-position-out-of-range]] |
| 2026-07-03 | Claude | Iris / bambufy | low | fixed | `min_version` 1.2.3 mismatch with slicer gcode — lowered to 1.2.2 | [[2026-07-03_bug-bambufy-min-version-mismatch]] |
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
| 2026-07-01 | Claude | djinn-gcode-sync / scp to Windows OpenSSH | low | fixed | `scp` silently fails with "No such file or directory" on backslash remote paths against Windows OpenSSH, even though the file exists and `ssh ... dir` with the identical backslash path lists it fine — fixed by forward-slashing the scp remote path only | [[2026-07-01_djinn-gcode-sync]] |


## 2026-07-01 — djinn-bughunter scan (1 finding(s))
- **[HIGH]** `journald:djinn-discord-gateway` — unhandled exception (18 occurrence(s)) _(type: errlog)_

| 2026-07-05 | Claude | Nemesis / Klipper SAVE_CONFIG | medium | workaround | SAVE_CONFIG fails with "conflicts with included value" when `[probe]` z_offset is in printer.base.cfg (included file) — z_offset must be written manually to printer.base.cfg after every PROBE_CALIBRATE | [[2026-07-05_bug-nemesis-z-offset-conflict]] |
| 2026-07-05 | Claude | Calliope / hardware | high | open (cable ordered) | nozzle_mcu serial dropout on all PETG prints — bytes_invalid climbing post-crash confirms broken wire inside toolhead cable harness (intermittent partial contact). New cable ordered. | [[2026-07-05_bug-calliope-nozzle-mcu-cable]] |


## 2026-07-05 — djinn-bughunter scan (1 finding(s))
- **[HIGH]** `journald:djinn-discord-gateway` — unhandled exception (14 occurrence(s)) _(type: errlog)_


## 2026-07-05 — djinn-bughunter scan (1 finding(s))
- **[MEDIUM]** `journald:djinn-telegram-gateway` — network error (1 occurrence(s)) _(type: errlog)_


## 2026-07-06 — djinn-bughunter scan (1 finding(s))
- **[MEDIUM]** `/tmp/djinn-personal-gateway.log` — network error _(type: errlog)_

## 2026-07-06 — Iris: Bambu Studio Injects M981/M624/M625 Regardless of gcode_flavor

- **[HIGH]** Iris — `M981`/`M624`/`M625` injected by Bambu Studio even with `gcode_flavor: klipper` → Klipper `Unknown command` crash on every print
- **Root cause:** Spaghetti detection (M981) and AMS layer markers (M624/M625) come from Bambu Studio's internal code generation, not profile fields. Not suppressible via JSON.
- **Fix:** Klipper no-op macros in `user.cfg` on Iris (192.168.1.50). Pattern documented in [[2026-07-06_bug-bambu-studio-m981-m624-injection]]
- **Status:** Fixed

## 2026-07-06 — Iris: time_lapse_gcode Inherited from A1 Parent Contains G1 X-48.2

- **[HIGH]** Iris — `G1 X-48.2 F3000` from inherited A1 `time_lapse_gcode` runs at every layer change → `Move out of range` crash
- **Root cause:** A1 profile's timelapse uses center-origin coordinates. Iris is corner-origin 0–215mm. Inherited without override.
- **Fix:** `"time_lapse_gcode": ""` in `Iris.json`. Pattern: any Bambu Studio profile inheriting from a Bambu parent must override this field.
- **Status:** Fixed

## BUG-014 CLOSED — 2026-07-09 (cable replaced, confirmed fixed)

Replacement nozzle_mcu toolhead cable installed by Javier. Calliope is back online — now at **192.168.1.113** (IP changed from .114, likely freed up by the Typhon Windows conversion). First post-install Benchy showed a squished bottom + merged fine details (nozzle sitting too close to the bed) — fixed live via `SET_GCODE_OFFSET Z_ADJUST=0.05 MOVE=0` over the Moonraker API. Javier confirmed the next print came out better.

**Final root cause (confirmed):** broken wire inside the nozzle_mcu toolhead cable harness, as diagnosed 2026-06-29. Cable replacement was the correct and sufficient fix — no software workaround was ever needed.

**Note:** the +0.05 Z_ADJUST is a runtime-only offset (resets on Klipper restart). Worth baking in permanently if it holds up over more prints.

| 2026-07-09 | Claude | Calliope / nozzle_mcu cable | high | **fixed** | Cable replaced by Javier, Calliope back online at .113, Z offset live-tuned (+0.05) to fix post-install squish, confirmed better on next print. | [[2026-07-09_bug-calliope-cable-fixed]] |

## 2026-07-09 — djinn-model-mark Broken by Storage Migration

- **[MEDIUM]** `~/.config/forge/makers-mark.json` pointed at `/home/drmanzo/printer-files/library/originals/logos/tf_anvil_traced_15mm.stl` — that whole `printer-files` tree was moved off Salomon to Alexandria during the 2026-07-09 storage migration, breaking every future `djinn-model-mark` call with "mark STL not found."
- **[LOW, separate issue]** Even after repointing to the migrated path, `tf_anvil_traced_15mm.stl` itself fails to load (`trimesh` returns an empty Scene, `bounds=None`) — the binary STL data looks corrupted/misaligned (no clean 80-byte header). The sibling `tf_anvil_traced_20mm.stl` in the same folder loads fine.
- **Fix:** repointed `makers-mark.json` `path` to `/run/media/drmanzo/alexandria/printer-files/library/originals/logos/tf_anvil_traced_20mm.stl`. Since `djinn-model-mark` always rescales the external mark mesh to `size_mm` (15mm default), using the 20mm source produces an identical result to what the 15mm file would have if it weren't corrupted.
- **Also fixed:** `djinn-model-mark` called `trimesh.load(args.stl, process=True)` with no `force='mesh'` — given a `.3mf` (or any multi-object container) it returned a `Scene`, and later boolean/repair steps (`trimesh.repair.fix_normals`) crashed with `AttributeError: 'Scene' object has no attribute 'is_winding_consistent'`. Patched `~/.local/bin/djinn-model-mark` to unwrap a `Scene` into a single `Trimesh` (`.dump(concatenate=True)` if multi-geometry, else the sole geometry) right after load. Verified: tool now runs directly on `.3mf` input with no manual STL extraction step, output geometry matches.
- **Status:** Fixed (config path, corrupted 15mm source worked around via 20mm file, 3mf input now supported natively)

## 2026-07-09 — djinn-print-safety Never Actually Worked (wrong Moonraker object/field path)

- **[HIGH]** `~/.local/bin/djinn-print-safety` (Calliope's real-time nozzle_mcu failure predictor, built specifically to catch BUG-014-style dropouts before they crash a print) has been silently broken since it was written. It queried `/printer/objects/query?mcu=bytes_retransmit,bytes_invalid,send_seq,retransmit_seq` — wrong object (`mcu`, the mainboard, not `mcu nozzle_mcu`, the toolhead board it's meant to watch) **and** wrong field path (those fields live nested under `last_stats`, not as top-level attributes of the mcu object in Moonraker's object-query API). Every poll returned `null` for all four fields, and `int(None)` crashed on every single cycle — confirmed via journalctl: `int() argument must be a string, a bytes-like object or a real number, not 'NoneType'` repeating every ~5s throughout an actively-printing job.
- **Consequence:** every prior run of this daemon (including during the two post-cable-replacement klippy_shutdowns tonight) was polling garbage and computing nothing — it never had a chance to warn or auto-pause, regardless of how it was started.
- **Fix:** `get_mcu_stats()` now queries `mcu%20nozzle_mcu=last_stats` and reads fields from the nested `last_stats` dict, with `or 0` fallback instead of `.get(key, 0)` (which doesn't catch explicit `None` values). Verified live against an in-progress print: clean `Z=1.4mm | retx=0.0% | emi=0.00B/s | p=0%` output every poll, no more errors.
- **Also fixed (related, same session):** the systemd unit (`~/.config/systemd/user/djinn-print-safety.service`) used `Restart=on-failure`, but the daemon exits with code 0 (not a failure) whenever Moonraker's `print_stats.state` is `"complete"` at startup — which is the normal resting state after any successful print (it doesn't revert to `"standby"` on its own). That meant the watchdog silently stayed dead after every print until manually restarted right as the next one began. Changed to `Restart=always` + `RestartSec=5` so it self-heals with no manual intervention — confirmed this is safe since the daemon's own `while True` loop already sits and polls quietly (5s interval) in every state that isn't a terminal one, so a 5s systemd restart cadence adds negligible overhead.
- **Status:** Fixed. Both bugs together meant this safety system has never once functioned as designed until tonight.

## 2026-07-10 (early AM) — Alexandria SSD Root-Directory Corruption + Physical Re-Enumeration

- **[HIGH]** While hunting for a model file, `ls` on `/run/media/drmanzo/alexandria` started failing with `Input/output error`. `journalctl -k` showed: `EXT4-fs warning (device sdb1): htree_dirblock_to_tree: inode #2: error -5 reading directory block` — inode #2 is the ext4 root directory itself, meaning the top-level directory structure of the whole drive had become unreadable. First occurrence at 23:43:07, roughly an hour after an unrelated `usb usb3-port2: unable to enumerate USB device` kernel message (22:31) that may or may not be connected.
- **Root cause:** the drive physically disconnected and reconnected during the session — confirmed via kernel log showing the SanDisk Extreme re-enumerating as a **new device node, `/dev/sdd`, not the original `/dev/sdb`**. This is why the first `e2fsck /dev/sdb1` attempt failed with "No such file or directory" — that device node no longer existed once the drive came back under a new SCSI host assignment. Not a software/filesystem-only corruption; the physical connection dropped.
- **Fix:** `sudo umount` (against the still-valid mount, which was pointing at the stale sdb1 handle but succeeded anyway) → `sudo e2fsck -y /dev/sdd1` (the *current* device node, found via `lsblk`) → journal recovered cleanly through all 5 fsck passes, one minor `orphan_present` flag cleared, no inodes relocated to `lost+found` (confirmed empty except pre-existing `.`/`..`). Remounted at the same `/run/media/drmanzo/alexandria` path (UUID-based, per the 2026-07-09 mount decision — survived the device-letter change with no fstab edit needed) and verified all top-level folders present and readable.
- **Status:** Fixed, no data loss detected. Filesystem-level repair was straightforward once the correct current device node was identified — the confusing part was the stale device-node reference from before the physical reconnect.
- **Rule/Lesson:** When `/dev/sdX` I/O errors show up on a drive that was working minutes earlier, check `lsblk`/kernel log for a re-enumeration event before assuming pure filesystem corruption — the device letter can silently change on a USB reconnect, and running fsck against the old (now-nonexistent) node just fails confusingly instead of pointing at the real issue.


## 2026-07-11 — djinn-bughunter scan (1 finding(s))
- **[MEDIUM]** `journald:djinn-telegram-gateway` — network error (3 occurrence(s)) _(type: errlog)_
