---
title: Session Report — Iris zmod Install + Slicer Setup + Typhon USB
agent: Claude
date: 2026-07-03
tags: [djinn, report, iris, nemesis, zmod, slicers, typhon, 3d-printing]
related: [[build-log]] | [[decision-log]] | [[INFRASTRUCTURE]]
---

# Session Report — Iris zmod Install + Slicer Setup + Typhon USB

**Date:** 2026-07-03
**Agent:** Claude
**Session type:** Build / Debug / Ops
**Trigger:** Resume — Iris zmod not starting after ENABLE file + cold reboot; then slicer setup for new printer fleet

---

## Summary

Diagnosed why Iris (Flashforge AD5X) wasn't starting Moonraker after the ENABLE file: the mod was never fully installed, only config files were present. Applied the full 206MB zmod package via USB — Iris is now fully online with zmod 1.7.1-49, Moonraker on port 7125, Klipper ready. Both Flashforge printers (Iris + Nemesis) confirmed operational. Downloaded OrcaSlicer and Bambu Studio installers to Salomon and Typhon USB, with autonomous setup scripts for when Typhon SSH is unlocked.

---

## What Was Built or Changed

- **Iris zmod 1.7.1-49 installed** — full USB install, took ~40 min, Moonraker live at 192.168.1.50:7125
- **Nemesis confirmed** — Moonraker live at 192.168.1.51:7125, Klipper ready
- **OrcaSlicer v2.4.1** downloaded to Salomon at `~/forge/slicers/` (132MB)
- **Bambu Studio v02.07.01.62** downloaded to Salomon at `~/forge/slicers/` (408MB)
- **Typhon USB populated** at `djinn/`:
  - `ssh-recovery/typhon-unlock.ps1` — enables password auth + drops Salomon SSH key permanently
  - `slicers/OrcaSlicer_Windows_Installer_V2.4.1_x64.exe`
  - `slicers/Bambu_Studio_win-v02.07.01.62.exe`
  - `slicers/install-slicers.ps1` — silent install script
  - `OPENCODE-PROMPT.md` — full autonomous prompt for Salomon/OpenCode
- **Salomon script** at `~/forge/slicer-setup/djinn-typhon-slicers.sh` — push + install on Typhon via SSH
- **INFRASTRUCTURE.md updated** — Iris and Nemesis entries updated with zmod firmware, Moonraker ports, SSH access details
- **Memory updated** — printer fleet table reflects Iris and Nemesis as ONLINE with correct IPs

---

## Technical Decisions

**Full zmod install vs ENABLE file — Why full:**
The ENABLE file (3.1KB, OpenSSL-encrypted) only re-enables zmod when it was previously fully installed and later disabled by a stock firmware update. Iris had partial config files in `/usr/data/config/mod_data/` but the core mod infrastructure (`/usr/data/config/mod/.shell/`, Python patches) was never installed. The fix_config.sh from the ENABLE package was failing silently because it couldn't find backup files to restore. Only the 206MB full install creates everything from scratch.

**Bambu Studio + bambufy over OrcaSlicer-only for Iris — Why:**
For 4-color commission printing, bambufy reduces material-to-waste ratio to under 50% by flushing purge into object infill/supports instead of a prime tower. OrcaSlicer works but wastes more. OrcaSlicer is the right call for Nemesis (single material, speed-focused). Bambufy install on Iris is deferred until Typhon SSH is working.

**Typhon USB as fallback — Why:**
Typhon Windows SSH rejects password auth (OpenSSH default: key-only). Rather than block on that, all assets were written to the physical USB so Javier can run `typhon-unlock.ps1` once manually and the system is fully automated afterward. The `administrators_authorized_keys` approach (vs per-user `~/.ssh/authorized_keys`) is required on Windows for admin-level SSH users.

---

## Files Created or Modified

```
~/Obsidian/djinn/INFRASTRUCTURE.md                            ← Iris + Nemesis updated to zmod, Moonraker, SSH
~/Obsidian/djinn/logs/reports/2026-07-03_iris-zmod-slicers-typhon-usb.md  ← this report

# On Salomon
~/forge/slicers/OrcaSlicer_Windows_Installer_V2.4.1_x64.exe  ← downloaded
~/forge/slicers/Bambu_Studio_win-v02.07.01.62.exe             ← downloaded
~/forge/slicer-setup/djinn-typhon-slicers.sh                  ← push+install automation

# On Typhon USB (djinn/)
ssh-recovery/typhon-unlock.ps1    ← SSH recovery script (run as Admin)
slicers/OrcaSlicer_Windows_Installer_V2.4.1_x64.exe
slicers/Bambu_Studio_win-v02.07.01.62.exe
slicers/install-slicers.ps1       ← silent install script
OPENCODE-PROMPT.md                ← full Salomon/OpenCode autonomous prompt
```

---

## Tests & Validation

- `curl http://192.168.1.50:7125/printer/info` → `state: ready` ✓
- `curl http://192.168.1.51:7125/printer/info` → `state: ready` ✓
- Iris zmod version: `1.7.1-49` ✓
- Salomon installer files: OrcaSlicer 132MB, Bambu Studio 408MB — size matches upstream ✓
- Typhon USB: both EXEs, both PS1 scripts, OPENCODE-PROMPT.md confirmed present ✓

---

## Known Issues

- **Typhon SSH still locked** — password auth disabled on Windows OpenSSH. Needs `typhon-unlock.ps1` run as Admin on Typhon once. All assets are on the USB ready to go.
- **bambufy not yet installed on Iris** — deferred; install via Klipper console: `ENABLE_PLUGIN name=bambufy` after restarting Iris once with Typhon's OrcaSlicer connected.
- **Iris + Nemesis not yet in Djinn CLI** — `djinn-iris` and `djinn-nemesis` commands not built yet; Moonraker API is identical to Calliope's so it's a straight port of `djinn-confirm-print`.
- **Iris clock stuck at 1970** — NTP not syncing on first boot. Should resolve on its own once the printer connects to the internet during normal use. Not blocking.

---

## What's Next

1. **Typhon**: Plug in USB, right-click `djinn/ssh-recovery/typhon-unlock.ps1` → Run as Admin. Once done, Salomon can push + install slicers autonomously via `djinn-typhon-slicers.sh`.
2. **bambufy on Iris**: After OrcaSlicer is on Typhon and connected to Iris, run `ENABLE_PLUGIN name=bambufy` in the Iris Klipper console (Fluidd at http://192.168.1.50).
3. **Djinn CLI**: Build `djinn-iris` and `djinn-nemesis` — Moonraker wrappers mirroring `djinn-confirm-print`. Wire into Telegram bot and Discord watcher.
4. **OrcaSlicer printer profiles**: Add Iris (AD5X) and Nemesis (AD5M Pro) profiles in OrcaSlicer on Typhon with Moonraker endpoints.

---

*— Claude, 2026-07-03*
