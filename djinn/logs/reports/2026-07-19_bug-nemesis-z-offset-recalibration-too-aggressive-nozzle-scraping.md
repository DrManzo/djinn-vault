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
**Status:** Klipper-side calibration fixed and verified. FlashOS-level leveling-before-print behavior identified but NOT fixable remotely — needs physical-screen intervention or further investigation with Javier present. Moonraker outage caused during investigation, fully recovered via reboot, no lasting damage.

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

## Current State (end of session)

- Nemesis: `Ready`, idle, heaters off, `homed_axes` cleared (normal post-reboot, not homed until next command)
- `probe.z_offset: -0.101` — good, Klipper-verified, survived the reboot
- `bed_mesh` profile `default` — good, captured against the corrected offset
- Moonraker: fully recovered, running correctly inside its chroot
- **The actual scraping bug is NOT fixed.** Any print started through any path available to us (touchscreen, Moonraker API, raw Klipper command) still routes through the FlashOS dialog that discards its own fresh probe and applies `0.0` instead.

---

## What's Actually Needed Next (requires Javier physically present)

1. **Try the physical touchscreen's own Accept/Reject buttons** on that leveling dialog directly — it may only be operable that way, not via any gcode/API command. This is the most likely path to a real fix and hasn't been tried yet.
2. If that also doesn't stick, the remaining option is directly editing `zLevelOffset` in `/opt/config/Adventurer5M.json` — **not attempted**, because the sign/reference-frame relationship between that value and Klipper's `probe.z_offset` is unverified, and guessing wrong on a value that directly controls nozzle-to-bed clearance is a real crash risk. This needs a supervised, low-stakes verification (e.g. checking clearance at a known Z height by eye) before trusting it for a real print — explicitly the kind of thing that should not be done unsupervised, which is why it wasn't attempted tonight.
3. Do not attempt to hand-fix individual mounts/paths under `/data/.mod/.forge-x/` again if Moonraker ever goes down on this machine — reboot first, it's the correct recovery path for this chroot-based setup.

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
