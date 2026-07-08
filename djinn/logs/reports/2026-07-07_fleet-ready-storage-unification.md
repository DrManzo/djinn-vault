---
title: Session Report — Fleet Production-Ready + Storage Unification Begin
agent: Claude
date: 2026-07-07
tags: [djinn, report, fleet, printers, oroborus, storage, nemesis, iris, calliope]
related: [[2026-07-06_iris-profile-fix-fleet-up]] | [[build-log]] | [[decision-log]]
---

# Session Report — Fleet Production-Ready + Storage Unification Begin

**Date:** 2026-07-07
**Agent:** Claude
**Session type:** Infrastructure + Build + Architecture
**Trigger:** Continued from prior session (Iris/Nemesis fixes). Fleet validation complete, production planning, Oroborus storage node discovered and activated.

---

## Summary

Full fleet validated and profiled. Nemesis SAVE_CONFIG bug permanently fixed. Fleet capability matrix built with Marcus. Slicer routing locked to Typhon. Sisters (Clotho, Lachesis, Atropos) named and documented. Calliope bring-up checklist written. Oroborus (192.168.1.154) discovered on LAN — Linux storage node with 4.6TB cold + 1.8TB live. 3D print files moved to live storage. Typhon model library transfer initiated (in progress at session close).

---

## What Was Built or Changed

### Printer Configs (applied live)

**Nemesis (192.168.1.51) — SAVE_CONFIG permanent fix:**
- Moved `[probe]` section from `/opt/config/printer.base.cfg` (included file) to `/opt/config/printer.cfg` (top-level)
- Root cause: Klipper's `SAVE_CONFIG` cannot write to sections defined in `[include]` files — z_offset writes were failing silently, requiring manual SSH edits after every `PROBE_CALIBRATE`
- Fix verified: `FIRMWARE_RESTART` → state `ready`, probe registered, zero stalls

**Nemesis start gcode verified:**
- OrcaSlicer machine profile already has `M140` + `M104` before `START_PRINT` — stock FlashForge touchscreen compatibility confirmed

### Vault Documents Created/Updated

| File | Action | Content |
|---|---|---|
| `djinn/hardware/fleet-capability-matrix.md` | Created + updated | Full per-machine profiles, enclosure corrections, slicer routing, sisters section |
| `djinn/printer/SUPPORT-SETTINGS.md` | Pulled (Marcus) | Per-machine support settings, IFS dissimilar-material strategy for Iris |
| `djinn/printer/PRINT-PROFILES.md` | Updated | Iris/Nemesis profiles added, slicer routing table, bambufy status corrected |
| `djinn/printer/config/fan-cap-calliope.cfg` | Pulled (Marcus) | Klipper M106 override macro, S128 hard cap, BUG-014 EMI protection |
| `djinn/communications/QUEUE.md` | Updated | Calliope bring-up checklist (physical + software) |
| `djinn/machines/TF-TTHQ.md` | Updated | Role clarified (creative workstation, not pipeline controller), Bambu Studio confirmed installed |
| `djinn/machines/devices.md` | Updated | Oroborus storage node noted |
| `djinn/projects/storage-unification.md` | Created | 6-phase storage unification plan |

### Fleet Naming — The Sisters

Three new machine names established following the Moirai (Fates) naming convention:
- **Clotho** — Bambu P1S + AMS (planned) — spins the thread
- **Lachesis** — Bambu P1S + AMS (planned) — measures the thread
- **Atropos** — TBD machine (incoming) — cuts the thread

All sisters: Bambu Studio on Typhon. Same slicer family as Iris.

### Storage Node — Oroborus

- **Discovered:** `oroborus.lan` at `192.168.1.154` — already on LAN, previously listed as 192.168.1.176 (wrong)
- **Hardware:** Linux (Ubuntu), NVMe 468GB OS, `/dev/sdb1` 4.6TB cold storage (`/mnt/storage`), `/dev/sda1` 1.8TB live storage (`/mnt/archive`)
- **Action taken:** `rsync` of `/mnt/storage/forge/` → `/mnt/archive/printer-files/forge/` (278MB, 16 design folders)
- **In progress:** Typhon `C:\Forge\models\` → `/mnt/archive/printer-files/models/` via tar pipe through Salomon (running at session close)

### Slicer Routing — Finalized

| Machine | Slicer | Station |
|---|---|---|
| Iris, Clotho, Lachesis, Atropos | Bambu Studio | Typhon |
| Nemesis, Penelope | OrcaSlicer | Typhon |
| Calliope | OrcaSlicer or Creality Print | Typhon |

Typhon = unified slicing station. Salomon = orchestration + observation. Not interchangeable.

---

## Technical Decisions

**Nemesis probe in printer.cfg not printer.base.cfg** — SAVE_CONFIG writes to the top-level config file only. Sections in `[include]` files are read-only from Klipper's perspective. Moving `[probe]` to `printer.cfg` permanently resolves the z_offset write failure without changing probe behavior.

**Marcus's M106 macro over Claude's** — Marcus's implementation correctly branches on `params.P is defined` (avoids passing P when absent), uses `action_respond_info()` (correct Klipper idiom vs `RESPOND TYPE=command`), and references BUG-014 in the log message for traceability.

**Oroborus drive role assignment (Javier):** `/mnt/storage` (4.6TB) = cold, `/mnt/archive` (1.8TB) = live. Mount names are counterintuitive but kept as-is to avoid disrupting existing references.

**Tar pipe for Typhon→Oroborus transfer** — Oroborus and Typhon have no direct SSH trust; Typhon's LAN ports are filtered (Tailscale only). Piping `tar czf` from Typhon through Salomon to Oroborus avoids intermediate storage on Salomon and requires no new SSH key setup.

**Creality Print now available for Calliope** — With Typhon as Windows slicing station, Creality Print 7.1.1 (already installed) is a valid slicer for Calliope. Safe because M106 S128 cap is enforced at the Klipper level via `fan-cap-calliope.cfg`, not at the slicer.

---

## Files Created or Modified

```
/opt/config/printer.cfg (Nemesis, 192.168.1.51)          ← [probe] moved here from printer.base.cfg
/opt/config/printer.base.cfg (Nemesis)                    ← [probe] removed
~/Obsidian/djinn/hardware/fleet-capability-matrix.md      ← created
~/Obsidian/djinn/printer/SUPPORT-SETTINGS.md              ← pulled from Marcus
~/Obsidian/djinn/printer/PRINT-PROFILES.md               ← updated (Iris/Nemesis sections, slicer table)
~/Obsidian/djinn/printer/config/fan-cap-calliope.cfg      ← pulled from Marcus
~/Obsidian/djinn/communications/QUEUE.md                  ← Calliope bring-up checklist appended
~/Obsidian/djinn/machines/TF-TTHQ.md                     ← role clarified, Bambu Studio confirmed
~/Obsidian/djinn/machines/devices.md                      ← Oroborus noted
~/Obsidian/djinn/projects/storage-unification.md          ← created
/mnt/archive/printer-files/forge/ (Oroborus)              ← 278MB, 16 design folders from cold storage
/mnt/archive/printer-files/models/ (Oroborus)             ← in progress from Typhon at session close
```

---

## Tests & Validation

- Nemesis `FIRMWARE_RESTART` after probe move → state `ready`, probe registered, MESH_DATA loaded, PA 0.035, zero stalls ✓
- Nemesis `SAVE_CONFIG` fix confirmed by config inspection — `[probe]` in `printer.cfg`, absent from `printer.base.cfg` ✓
- Oroborus forge copy verified: `ls /mnt/archive/printer-files/forge/` shows all 16 folders, `du -sh` = 278MB ✓
- Oroborus LAN connectivity: `oroborus.lan` resolves to `192.168.1.154`, SSH as `drmanzo` ✓
- Clamp_frame Nemesis print: completed successfully (log shows `Done printing file` at 11:50:04, ~5h runtime) — prior "halfway" report was a mid-run check, not a failure ✓

---

## Known Issues / Open Items

- **Calliope bring-up pending** — cable + drag chain install required before deployment. `fan-cap-calliope.cfg` ready to deploy when host at `192.168.1.114` comes online.
- **`djinn-gcode-safety` source missing** — only `.pyc` in `__pycache__`. `djinn-print-safety` exists (runtime MCU monitor) but is not a gcode post-processor. M106 cap is now handled by Klipper macro — script may be redundant for fan purposes.
- **`djinn-print-safety` wrong default URL** — hardcoded to `192.168.1.113` (Typhon), Calliope is at `192.168.1.114`. Must set `DJINN_MOONRAKER=http://192.168.1.114:7125` when launching.
- **Typhon → Oroborus model transfer in progress** — `C:\Forge\models\` (~3.87GB) piping via tar. Verify after completion.
- **Oroborus cold storage forge copy** — original at `/mnt/storage/forge/` kept until Javier confirms live copy is good, then trash.
- **Storage unification Phase 2+** — Typhon handoff instructions, library index, SMB share setup all pending next dedicated session.
- **Atropos** — name reserved, machine TBD.
- **Nemesis bed tram** — right side still physically low ~1.3mm. Mesh compensates but re-tram recommended warm for best first layers.

---

## What's Next

- [ ] Verify Typhon → Oroborus model transfer completed cleanly
- [ ] Calliope: cable + drag chain install → fan-cap deploy → bed mesh → test print
- [ ] Oroborus: set up SMB share so Typhon can map Z:\ directly
- [ ] Storage unification Phase 2: Typhon handoff instructions + library index
- [ ] Atropos: identify machine
- [ ] Nemesis: physical bed tram while warm
- [ ] Typhon: `claude --bg` interactive disclaimer (needs physical/RDP session)
- [ ] Typhon: Ollama serve (needs interactive session, Session 0 issue)

---

*— Claude, 2026-07-07*
