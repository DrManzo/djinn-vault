---
title: Bug Report — BUG-014 Closed: Calliope Cable Replaced, Post-Install Z Offset Fix
agent: Claude
date: 2026-07-09
tags: [djinn, bug, calliope, klipper, cable, z-offset]
related: [[2026-07-05_bug-calliope-nozzle-mcu-cable]] | [[2026-06-28_bug-camood-petg-start]] | [[build-log]] | [[bugs]]
---

# Bug Report — BUG-014 Closed: Calliope Cable Replaced

**Date:** 2026-07-09
**System:** Calliope (Ender-3 V3 Plus, Klipper, now at 192.168.1.113)
**Severity:** High (was blocking all PETG/engraved prints)
**Status:** Fixed

---

## What Happened

Javier installed the replacement nozzle_mcu toolhead cable (ordered 2026-07-05 after the cable diagnosis). Calliope came back online — but on a new IP, **192.168.1.113**, not the previously documented **192.168.1.114**. Likely cause: .113 was Typhon's static IP before its Windows conversion; once that machine stopped claiming it, DHCP handed it to Calliope.

First Benchy test print after the cable install came out with a squished bottom layer and fine surface details merging together — the classic signature of the nozzle sitting slightly too close to the bed.

---

## Root Cause (confirmed, closes out 2026-07-05 diagnosis)

The original BUG-014 symptom (repeated `klippy_shutdown` / key561 errors on PETG and engraved prints) was a broken wire inside the nozzle_mcu toolhead cable harness — confirmed via climbing `bytes_invalid` post-crash (intermittent partial contact, not a clean break). Cable replacement was the correct and sufficient fix. No software workaround (fan cap, thermal soak, TRSYNC, mesh density) was ever the real solution — all of those were tried and reverted 2026-06-29 as ineffective.

---

## Fix Applied (post-install Z tuning)

Calliope uses Creality's `prtouch_v2` strain-gauge auto-leveling system, not a Klipper `[probe]` section (different tuning surface than Nemesis — no direct `z_offset` config line to hand-edit the same way). Live-tuned instead:

```bash
curl -X POST "http://192.168.1.113:7125/printer/gcode/script" \
  -d 'script=SET_GCODE_OFFSET Z_ADJUST=0.05 MOVE=0'
```

Confirmed via `gcode_move.homing_origin` → `[0, 0, 0.05, 0]`. Runtime-only — no config file touched, no Klipper restart. Javier confirmed the next print came out better.

**Access notes:**
- SSH failed both ways: password auth (`root`/`root`, works on Nemesis) rejected; key auth (`~/.ssh/calliope_ed25519`) also rejected. SSH host key also changed (old ED25519 entry stale from the .113-was-Typhon era) — cleared via `ssh-keygen -R 192.168.1.113`. Root cause of the auth failure not investigated (out of scope, time-boxed live fix) — Moonraker's HTTP gcode-script endpoint was sufficient and required no auth.
- Config confirmed as genuinely Calliope via Moonraker `configfile` query: hostname `Ender-3`, custom Djinn macros present (`djinn_failure_park`, `djinn_resume_print`).

---

## Rule / Lesson

**Not every Klipper machine's Z calibration lives in a `[probe]` section.** Creality's stock strain-gauge auto-leveling (`prtouch_v2`) exposes a different config surface — check `configfile` via Moonraker before assuming the Nemesis-style manual `z_offset` edit pattern applies. For a fast, safe, reversible live nudge on any Klipper machine regardless of probe type, `SET_GCODE_OFFSET Z_ADJUST=<value> MOVE=0` over the Moonraker gcode-script endpoint works universally and requires no SSH access.

**IP addresses on this network are not static without a DHCP reservation.** Calliope moved from .114 to .113 with no config change on its end — likely inherited Typhon's old lease. Any machine without a confirmed DHCP reservation should be checked by hostname/Moonraker query, not assumed IP, especially after other machines on the subnet get reprovisioned.

---

## What's Next

- [ ] Bake the +0.05 Z_ADJUST into something persistent (start-gcode macro or prtouch_v2 offset) if it holds up over more prints — currently resets on Klipper restart
- [ ] Investigate why SSH access to Calliope stopped working (both password and key auth) — not urgent, Moonraker API covers current needs
- [ ] Confirm/set a DHCP reservation for Calliope at .113 so this doesn't shift again
- [ ] Update all docs/scripts referencing Calliope at .114 (e.g. `forge/MACHINE-ROLES.md`, `PENELOPE-SATURDAY-RUNBOOK.md`) — out of scope for this fix, flagging for follow-up

---

*— Claude, 2026-07-09*
