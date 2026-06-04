---
title: Session Report — Calliope Upgrade + OrcaSlicer Setup
agent: Claude
date: 2026-06-03
tags: [djinn, report, calliope, klipper, moonraker, fluidd, orcaslicer, upgrade]
related: [[error_log]] | [[build-log]] | [[2026-06-02_proxy-stand-print-diagnosis]]
---

# Session Report — Calliope Upgrade + OrcaSlicer Setup

**Date:** 2026-06-03  
**Agent:** Claude  
**Session type:** Upgrade + Diagnosis continuation  
**Trigger:** Continued proxy stand print failures + Javier requested Calliope brought up to date

---

## Summary

Continued diagnosing nozzle_mcu (key561) failures on Proxy Stand prints. Confirmed the M106 fix (50% fan) did not fully resolve the issue — the most recent failure showed an instant retransmit spike with `bytes_invalid=0` (not EMI pattern) suggesting a physical disconnect or power glitch on the nozzle board rather than EMI. All proxy stand STLs and gcodes scrubbed to blocked archive; fresh STL incoming.

Calliope was then upgraded: SSH enabled via printer settings, Creality Helper Script deployed, Moonraker updated from v0.7.1 (old dirty fork) to v0.10.0 (upstream), Fluidd installed at port 4408, Gcode Shell Command installed. Full config backup taken before upgrade.

OrcaSlicer 2.3.2 installed via Flatpak on Salomon. Calliope physical printer profile written. Switching from PrusaSlicer.

---

## What Was Built or Changed

### Calliope (192.168.1.113)
- **SSH enabled** — Settings → Root Account Information → root / `creality_ender3v3`
- **Moonraker** — `v0.7.1-780-gdde9bcc-dirty` → `v0.10.0-20-g9008485` (upstream, via Creality Helper Script)
- **Fluidd** — installed at `http://192.168.1.113:4408` (replaces old Creality web UI)
- **Gcode Shell Command** — installed (enables shell execution from Klipper macros)
- **Config backups** — cleaned from 52 → 5 (kept most recent)
- **Safe point** — `/usr/data/SAFE-POINT-2026-06-02/` on printer, `~/printer-files/calliope-safe-point-2026-06-02/` locally
- **Helper Script** — `/usr/data/helper-script/` (Guilouz, for future installs)

### Salomon (this machine)
- **OrcaSlicer 2.3.2** — installed via `flatpak install flathub com.orcaslicer.OrcaSlicer`
- **Calliope printer profile** — `~/.var/app/com.orcaslicer.OrcaSlicer/data/OrcaSlicer/user/default/machine/Calliope.json`
  - Host: `http://192.168.1.113`, Port 7125, Moonraker, Fluidd UI at `:4408`
- **Connection doc** — `~/.config/djinn/calliope-orcaslicer.md`

### Vault
- Proxy stand operational records scrubbed — only bug reports retained
- All proxy stand STLs and gcodes moved to `~/printer-files/blocked/proxy-stands-2026-06-02/`
- Fresh STL pending for next attempt

---

## Why OrcaSlicer Over PrusaSlicer

PrusaSlicer was identified as a contributing factor to the key561 failures via aggressive default fan settings (`bridge_fan_speed=100` → `M106 S255`). OrcaSlicer:
- Has better defaults for Klipper/Creality printers
- Native Moonraker integration (direct upload + print start from slicer)
- Built-in Ender-3 V3 Plus profile
- Active maintenance for Creality hardware
- Pressure advance calibration tools
- Works with Fluidd web UI at port 4408

Key OrcaSlicer setting to verify: `bridge_fan_speed` — should be 0 or ≤25% for Calliope.

---

## nozzle_mcu Failure — New Evidence

Most recent failure (ProxyStandTF_brim.gcode, 643s duration, 22:30:26):

```
22:30:15 — nozzle_mcu: retransmit_seq=17, bytes_invalid=0  ← CLEAN
22:30:18 — nozzle_mcu: retransmit_seq=11079, bytes_invalid=0  ← INSTANT SPIKE
22:30:24 — rto=5.000, stalled_bytes=759  ← MAXED OUT
22:30:39 — bytes_invalid=22  ← noise appears AFTER the dropout
22:30:44 — Got EOF when reading from device  ← main MCU also drops
```

**Key difference from EMI failure:** `bytes_invalid=0` at time of dropout. EMI causes corrupted bytes immediately. This pattern (instant silence, no corruption) suggests:
- Power reset of nozzle_mcu board
- Physical connector momentary disconnect under vibration
- NOT fan EMI (would show bytes_invalid immediately)

**Status:** Unresolved. Needs physical inspection of the nozzle board connector and power supply during a print. The stand geometry (hollow ring, continuous circular wall moves at ~10 min) may be stressing a specific cable position.

---

## Files Created or Modified

```
/usr/data/SAFE-POINT-2026-06-02/                          ← Calliope pre-upgrade backup
~/printer-files/calliope-safe-point-2026-06-02/           ← Local copy
~/.var/app/com.orcaslicer.OrcaSlicer/.../Calliope.json   ← OrcaSlicer printer profile
~/.config/djinn/calliope-orcaslicer.md                   ← Connection reference doc
~/printer-files/blocked/proxy-stands-2026-06-02/          ← All blocked stand files
```

---

## What's Next

- [ ] Open OrcaSlicer, verify Calliope profile loads correctly — @Javier
- [ ] Set bridge_fan_speed=0 in OrcaSlicer Calliope filament profile — @Javier
- [ ] Get new Proxy Stand STL from Javier, reslice with OrcaSlicer
- [ ] Physical inspection: nozzle board connector + power trace during print (key561 root cause still open)
- [ ] Re-seat 4 strain gauge connectors (error 3343 still pending) — @Javier
- [ ] Entware optional install via helper script if needed later

---

*— Claude, 2026-06-03*
