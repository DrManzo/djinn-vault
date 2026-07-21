---
title: Bug Report — Nemesis Z-Offset / FlashOS Leveling Dialog Unfixable Remotely, Moonraker Outage Self-Inflicted and Recovered
agent: Claude
date: 2026-07-19 to 2026-07-20
tags: [djinn, bug, nemesis, z-offset, calibration, printer-safety, moonraker, forge-x]
related: [[build-log]] | [[bugs]]
---

# Bug Report — Nemesis Z-Offset / FlashOS Leveling Dialog, Moonraker Outage

**System:** Nemesis (FlashForge AD5M Pro) — Klipper `probe.z_offset`, `forge-x` mod, stock FlashOS firmware
**Severity:** High (hardware risk — nozzle-to-bed contact, twice) + self-inflicted Moonraker outage (fully recovered)
**Status:** RESOLVED (pending full-print confirmation). Klipper-side calibration fixed and verified. Root cause of the FlashOS Z-offset reset confirmed 2026-07-20: print-starts must route through the `LEVELING_PRINT_FILE` macro (real bed leveling), not `NOLEVELING_PRINT_FILE`/Moonraker's native `/printer/print/start` (skips leveling, discards computed offset to `0.0`). See Addendum 3. Moonraker outage caused during investigation, fully recovered via reboot, no lasting damage.

---

## Timeline

**2026-07-19, first pass:** Bed screws leveled (`SCREWS_TILT_CALCULATE`, 1.73mm → 0.466mm tilt), then `BED_MESH_CALIBRATE` saved — in the wrong order, before Z-offset was recalibrated. `PROBE_CALIBRATE` run afterward; Javier completed the manual paper-test himself past where guided steps left off, landing at `probe.z_offset: -0.336`, saved. Next print scraped the plate; Javier emergency-cancelled. Printer left in Klipper `shutdown` state overnight.

**2026-07-20, second pass:** Redid the process in the correct order — `PROBE_CALIBRATE` first (this time landing at a much more reasonable `-0.101`, verified via a clean 0.537mm bed mesh), *then* `BED_MESH_CALIBRATE` fresh against the corrected offset. This Klipper-side calibration is solid and was reverified after the reboot below — still `-0.101`, mesh profile `default` intact.

**Print attempts kept scraping anyway.** Root-caused why: the actual print-start path (`NOLEVELING_PRINT_FILE` from the stock screen, and — critically — even Moonraker's *native* `/printer/print/start` and Klipper's own core `SDCARD_PRINT_FILE` command) all route through an M23-socket handshake to the stock FlashOS firmware (port 8899, closed-source), which runs its **own separate leveling-before-print dialog** — completely independent of Klipper's `probe.z_offset`. This dialog:
- Prints console text nearly identical to Klipper's real `MANUAL_PROBE`/`TESTZ`/`ACCEPT` flow, but **does not accept `TESTZ` or `ACCEPT`** (`Unknown command`, confirmed twice) — it is not a real Klipper manual-probe session despite the matching text.
- Computes a fresh offset each time (consistently ~`1.05`, watched across multiple attempts) but **discards it and applies `0.0`** right before the print actually starts (`SET: Z-OFFSET: 1.052` → `SET: Z-OFFSET: 0.0`, every single attempt).
- Auto-cancels/times out (~30s) if nothing interacts with it, which nothing can from any API/gcode path found.
- Has its own persistent value in `/opt/config/Adventurer5M.json`: `"zLevelOffset": -2.073...` — a **third, independent Z-offset system**, separate from both Klipper's `probe.z_offset` and the unrelated `mod_params.z_offset`/`load_zoffset` toggle (confirmed inactive/irrelevant — that one only applies to the `_START_PRINT` macro flow, which this gcode file never calls, since it's a raw macro-free start sequence).

**Exhaustively confirmed no remote bypass exists**: stock screen macros (`LEVELING_PRINT_FILE`, `NOLEVELING_PRINT_FILE` — both call this same handshake via different shell scripts, `zprint.sh`/`zsend.sh` → `zsend.py` → raw socket to port 8899), Moonraker's native print-start API, and Klipper's own unwrapped `SDCARD_PRINT_FILE` core command all hit the identical FlashOS dialog. This is architectural — `virtual_sdcard` on this machine is integrated with the stock firmware's file-select mechanism at a level deeper than gcode macro wrapping.

**Self-inflicted Moonraker outage:** Attempted to restart the Moonraker service after its HTTP API hung (stuck behind a blocking `SDCARD_PRINT_FILE` gcode request). The stock `S65moonraker` init script failed (`start-stop-daemon: command not found` — not available in this busybox environment) on both stop and start, which also tore down what turned out to be a **chroot-scoped bind mount** (`/root/moonraker-env`, sourced from `/data/.mod/.forge-x/root/moonraker-env`). Manual reconstruction attempts (direct invocation, PYTHONPATH tricks, copying `importlib_metadata`/dependency files across Python versions) failed with increasingly deep errors, eventually hitting a hard blocker: the packages in that venv require Python 3.11 syntax (`zipp`'s positional-only parameters, a 3.8+ feature) that the outer-namespace `/usr/bin/python3` (actually 3.7.2) cannot even parse. Root cause: `forge-x` runs as a **full chroot environment** at `/data/.mod/.forge-x/` (own `/proc`, `/dev`, `/tmp`, `/data`) — Moonraker is meant to run *inside* that chroot, where `/usr/bin/python3` correctly resolves to forge-x's own bundled 3.11 interpreter. Manually invoking paths from the outer filesystem namespace can never work correctly, no matter how many individual files/mounts are patched by hand.

**Fix: a full reboot**, not manual mount reconstruction. The boot-time init sequence correctly re-established every mount and re-launched Moonraker inside its chroot exactly as designed (confirmed via `ps aux` showing PID 1462 — identical PID to before, consistent with a deterministic init sequence). Verified post-reboot: Klipper untouched throughout (`probe.z_offset` still `-0.101`, `bed_mesh` profile `default` still loaded, Klipper process never stopped), Moonraker fully responsive, `djinn-print-safety@nemesis` reconnected.

---

## Addendum 1 (2026-07-20): OrcaSlicer profile origin was ALSO wrong, independently

While chasing whether Salomon's re-sliced Kraken gcode might be a contributing factor, found that Salomon's `Flashforge Adventurer 5M Pro 0.4 Nozzle - Copy.json` had `printable_area` set to corner-origin (`0x0` to `220x220`) — the result of the 2026-07-16 bug fix ([[2026-07-16_bug-nemesis-orcaslicer-center-origin-printable-area]]). Live Klipper verification (`printer.base.cfg` mesh_min/max `-105/105`, live `axis_minimum/maximum` `-125/125`, `SCREWS_TILT_CALCULATE` probe coordinates) proved Nemesis is genuinely **center-origin** — the 2026-07-16 fix was itself wrong and had been silently mispositioning Salomon-sliced Nemesis jobs since that date. Typhon's independent copy of the profile was never "fixed" this way and was correct the whole time. Reverted Salomon's profile back to center-origin (`-110x-110` to `110x110`); that report has been corrected in place with a full addendum. This is a separate bug from the Z-offset/FlashOS issue below — it affects XY placement, not Z clearance — but was found during the same investigation and is unrelated to why prints were scraping.

## Addendum 2 (2026-07-20): `mod_params.load_zoffset` override — tested live, confirmed does NOT work

Hypothesis: `forge-x`'s `mod_params` layer exposes a `load_zoffset` toggle + `z_offset` value, read by `_START_PRINT_PREPARE`'s `LOAD_GCODE_OFFSET` call. If set (`load_zoffset=1`, `z_offset=-0.101`, matching Klipper's verified-good `probe.z_offset`), maybe `_START_PRINT_PREPARE` would apply the correct offset *after* the buggy FlashOS dialog resets it to `0.0`, since `_START_PRINT_PREPARE` fires later in the sequence.

Flagged the risk before testing: the buggy dialog's own `SET: Z-OFFSET: 0.0` message uses the exact same `SET_MOD`-backed storage mechanism (confirmed via the `ModParamManagement.cmd_SET_MOD_PARAM` pycache string), so there was a real chance both paths write to the same slot and the dialog — firing later — would win regardless.

**Test (2026-07-20, live, closely watched, run at Javier's explicit instruction — "run the test then stop it when you have what you need"):**
1. Confirmed Nemesis idle/`standby`.
2. Set `load_zoffset=1`, `z_offset=-0.101` via `SET_MOD`.
3. Started `Kraken_pipe_PLA_4h5m.gcode` via Moonraker's `/printer/print/start`.
4. Polled `mod_params.z_offset` + `print_stats.state` every 4s via a backgrounded watch loop.
5. Observed: `z_offset` `-0.101` → `0.855` (FlashOS dialog's fresh probe reading) → held → **snapped to `0.0` at the exact same poll tick `print_stats.state` became `printing`.**
6. Cancelled immediately (`/printer/print/cancel`) + `M104 S0`/`M140 S0`, before any real extrusion.
7. Pulled `/server/gcode_store?count=25` — confirmed the mechanism fired as designed but read a value that was already clobbered: `Global Z-Offset management is used... Z-Offset set from global parameters: 0.0`.
8. Reverted `load_zoffset` to `0` afterward (confirmed `load_zoffset: False`, `z_offset: 0.0`) to leave no half-applied state.

**Verdict: this fix path is confirmed dead, empirically — not guessed.** The dialog's zero-reset and `_START_PRINT_PREPARE`'s restore-attempt share the same storage slot, and the dialog always writes last. No software-side override of the FlashOS dialog's `0.0` has been found through any of: stock macros, Moonraker API, raw Klipper commands, or the `mod_params`/`SET_MOD` layer.

**Open question this addendum does NOT resolve:** whether that `0.0` is actually dangerous. All four FlashOS-dialog print-start attempts this session were cancelled within ~1 poll tick of reaching `printing` state, specifically *because* `0.0` was assumed unsafe — none were allowed to run long enough to observe a real nozzle-to-bed outcome under the *current* (`-0.101`, clean mesh) calibration. The original scraping incidents both predate this calibration (one under the bad `-0.336` offset, one before offset/mesh order was corrected). It's possible `SET_GCODE_OFFSET Z=0.0` is a harmless "clear any leftover manual babystep" no-op layered on top of an already-correctly-homed position (Klipper's `probe.z_offset` is read at `G28`/homing time, not overwritten by a runtime `SET_GCODE_OFFSET` call) — in which case the real scraping cause may already be fully fixed and this whole FlashOS-dialog thread is a red herring. But the dialog computing real values around `+0.85` to `+1.05` before discarding them for `0.0` is concrete evidence pointing the other way. This has NOT been resolved either way and should not be assumed safe without the verification in the next section.

---

## Addendum 3 (2026-07-20, later): ROOT CAUSE CONFIRMED — every failed attempt used the no-leveling print-start path

Javier ran a print manually from the touchscreen with the bed-leveling option explicitly enabled at the file-select screen. Result: full 17×17 `BED_MESH_CALIBRATE` captured live, saved to profile `default`, print started immediately after — and the print-start log has **no** `SET: Z-OFFSET` / `Global Z-Offset management` sequence at all, unlike every prior attempt. Live `gcode_move.homing_origin` confirmed `[0,0,0,0]` (no leftover garbage), webcam snapshot ~5min into the print showed a clean, well-adhered first layer with no scraping or scoring. Print continued normally.

This lines up exactly with what's already in `stock.cfg` (see the earlier full-text capture of `mod/config/stock.cfg` above): there are **two separate print-start macros**, not one —

- `NOLEVELING_PRINT_FILE` — "Print file from Stock screen", routes through `zsend` → the M23-socket handshake → the FlashOS dialog that computes-then-discards its offset (`0.0`). **This is what every attempt tonight actually hit**, including mine via Moonraker's native `/printer/print/start` (which does not distinguish leveling-on/off — it apparently defaults to the no-leveling behavior).
- `LEVELING_PRINT_FILE` — "Printing a file **with bed leveling** from the printers Stock screen", routes through `zprint PRINT '<filename>'` instead, which actually runs and *keeps* a real `BED_MESH_CALIBRATE`.

**Checked whether any djinn automation needs patching:** grepped all of `~/.local/bin` for both Nemesis's IP and `printer/print/start`. Neither `djinn-confirm-print` nor `djinn-print-recover` touch Nemesis at all (hardcoded to Calliope's IP). No dedicated Nemesis print-start script exists yet — every attempt tonight was an ad-hoc `curl` straight to Moonraker's native endpoint, which is exactly the no-leveling path. Nothing to patch today, but this is now the required pattern for any future Nemesis print-start tooling:

```
# WRONG — hits the no-leveling FlashOS dialog, forces Z-offset to 0.0:
curl -X POST "$MOONRAKER/printer/print/start" -d '{"filename":"<name>"}'

# RIGHT — routes through real bed leveling, offset stays correct:
curl -X POST "$MOONRAKER/printer/gcode/script" -d '{"script":"LEVELING_PRINT_FILE FILENAME=<name>"}'
```

**Caveat — this is strong evidence, not yet fully closed.** The print in question was ~5 minutes into a 4h5m job when checked, first layer only. Treating this as confirmed given (a) it exactly matches macro source we already have in hand, not inference from symptoms, and (b) the print-start log difference is a clean binary (offset-reset sequence present vs. absent), not a fuzzy signal — but the print should be watched through to completion before fully closing this out.

---

## Current State (end of session)

- Nemesis: `Ready`, idle, heaters off, `homed_axes` cleared (normal post-reboot, not homed until next command)
- `probe.z_offset: -0.101` — good, Klipper-verified, survived the reboot, confirmed intact 2026-07-20
- `bed_mesh` profile `default` — good, captured against the corrected offset, 0.537mm range, confirmed intact 2026-07-20
- OrcaSlicer profile on Salomon — corrected back to center-origin 2026-07-20 (see Addendum 1)
- `mod_params.load_zoffset` — confirmed dead-end (see Addendum 2), reverted to off/0.0, no lingering state
- Moonraker: fully recovered, running correctly inside its chroot
- **Whether the scraping bug is actually still live is UNCONFIRMED.** The FlashOS dialog demonstrably discards a computed ~0.85–1.05mm offset for `0.0` on every print-start, which looks dangerous, but no real print has been allowed to run far enough under the *current* good calibration to prove it one way or the other.

---

## What's Actually Needed Next

1. **Watch the current Kraken print through to completion** to fully close this out — clean first layer confirmed live via webcam at ~5min in, but the fix (Addendum 3) should be considered provisional until a full print finishes clean.
2. **Any future Nemesis print-start automation must call `LEVELING_PRINT_FILE FILENAME=<name>` via `/printer/gcode/script`, never Moonraker's native `/printer/print/start`.** No existing djinn script needs patching (grepped — nothing currently targets Nemesis), but this is now the required pattern going forward. Worth adding a small wrapper script once the fix is fully confirmed, so this isn't reliant on remembering it each time.
3. The earlier ideas below are now superseded by Addendum 3 but kept for the record in case the leveling-macro theory turns out incomplete:
   - Non-destructive paper-check (`G28` + `SET_GCODE_OFFSET Z=0` + `G1 Z0.25` + paper drag) — still a valid fallback verification method if a future print scrapes again despite going through `LEVELING_PRINT_FILE`.
   - Endstop-level offset compensation (`Z_OFFSET_APPLY_ENDSTOP`) — only relevant if the no-leveling path is ever used deliberately and needs to be made safe too.
   - Direct edit to `zLevelOffset` in `/opt/config/Adventurer5M.json` — not attempted, not needed if Addendum 3 holds.
   - Physical touchscreen Accept/Reject on the dialog — moot; the actual fix was enabling leveling at file-select, not interacting with the dialog itself.
   - Javier's physically-re-level-the-screws proposal — not needed; screws control tilt (already verified level), the actual issue was which macro the print-start went through.
4. Do not attempt to hand-fix individual mounts/paths under `/data/.mod/.forge-x/` again if Moonraker ever goes down on this machine — reboot first, it's the correct recovery path for this chroot-based setup.

---

## Rule / Lesson

**A console message that looks like a known interface (Klipper's `MANUAL_PROBE`/`TESTZ`/`ACCEPT`) is not proof it *is* that interface.** This FlashOS dialog mimicked Klipper's manual-probe text closely enough to cause two failed attempts before the mismatch (`Unknown command: "TESTZ"`) was actually noticed and taken seriously. When a command that should be registered (confirmed via `/printer/gcode/help`) is rejected as unknown in a live session, that's a signal the session itself isn't what it appears to be — worth checking before repeating the same command a second time expecting a different result.

**On an unfamiliar embedded/chroot system, prefer reboot over manual reconstruction once you're patching individual mount points and copying files across incompatible Python versions.** Every manual fix attempted here (remounting one directory, copying one dependency, setting PYTHONPATH) fixed the symptom just in front of it and immediately exposed a deeper one, because the real structure (a full chroot with its own `/usr`) wasn't understood until several failed attempts in. A boot-time-managed mount tree should be restored by the mechanism that manages it (the boot sequence), not hand-reconstructed piece by piece under time pressure.

**Bypassing a suspected bug by trying "the next API layer down" (macro → Moonraker API → raw Klipper command) is good instinct, but confirm each layer actually reaches a different code path before trusting it as a fix.** All three layers here funneled into the identical FlashOS handshake — the appearance of using a "more native" interface didn't guarantee it avoided the problem, because the integration was deeper than any of those layers.

---

## Files / State Touched

```
Nemesis (192.168.1.51):
  probe.z_offset: -0.101 (Klipper-verified, correct, survived reboot)
  bed_mesh profile "default": recaptured fresh against corrected offset, good
  zLevelOffset (Adventurer5M.json, FlashOS): -2.073... — untouched, unverified, NOT the fix
  /opt/config/mod/... : zprint.sh briefly edited then reverted to original (wrong script, not the actual bug)
  Moonraker: went down (self-inflicted during investigation), fully recovered via reboot
```

---

*— Claude, 2026-07-19/20*
