---
title: Session Report — Forge-Slicer Migration to Orca Slicer
agent: Claude
date: 2026-06-15
tags: [djinn, report, forge-slicer, orca-slicer]
related: [[build-log]] | [[decision-log]] | [[TASK-forge-slicer-glbc-fix]]
---

# Session Report — Forge-Slicer Migration to Orca Slicer

**Date:** 2026-06-14
**Agent:** Claude
**Session type:** Debug + Build
**Trigger:** CrealityPrint segfault on `--slice 0` in Docker container

---

## Summary

CrealityPrint's CLI slicing (`--slice 0`) is broken in ALL v6+ Linux builds (v6.1.2 through v7.1.1) with a null pointer dereference in `Slic3r::GUI::PartPlate::set_shape`. v5.1.7 has no headless CLI. After version bisection, Orca Slicer v2.3.2 was installed as the forge-slicer backend. It slices reliably via CLI with exit 0, no crashes.

---

## What Was Built or Changed

- **Root-caused** CrealityPrint segfault: null dereference at offset 0x9d8 in `PartPlate::set_shape`, triggered by `--slice 0` on all machines with `support_multi_bed_types: 1`. Present in every v6+ Linux build.
- **Installed** Orca Slicer v2.3.2: extracted AppImage to `/opt/orca-slicer/`, symlinked to `/usr/local/bin/orca-slicer`
- **Rewrote** `slice.sh`: removed Docker dependency, calls Orca Slicer directly on host
- **Deprecated** Docker-based forge-slicer pipeline: `Dockerfile`, `entrypoint.py` still in vault but obsolete
- **Removed** `/log → /tmp` symlink and CrealityPrint AppImage artifacts from debug sessions

---

## Technical Decisions

- **Orca Slicer over CrealityPrint** — CrealityPrint's CLI is broken across 7 versions tested (v6.1.2-v7.1.1). Orca is actively maintained, has native Ender-3 V3 Plus support, reliable CLI, and exit 0 on same workloads.
- **Host-side execution over Docker** — CrealityPrint Flatpak was the correct runtime all along; Docker added complexity (cross-device link errors tied to tmpfs mounts) without benefit. Orca runs natively on host, no container needed.
- **Persistent AppImage extraction over FUSE** — Extracting to `/opt/orca-slicer/` avoids FUSE dependency and provides reliable access to bundled profiles.

---

## Files Created or Modified

```
~/Obsidian/djinn/printer/forge-slicer/slice.sh    ← Rewritten: removed Docker, uses Orca Slicer directly
~/Obsidian/djinn/printer/forge-slicer/Dockerfile   ← Deprecated (left in place for reference)
~/Obsidian/djinn/printer/forge-slicer/entrypoint.py ← Deprecated (left in place for reference)
/opt/orca-slicer/                                    ← New: extracted Orca Slicer installation
/usr/local/bin/orca-slicer                           ← New: symlink to /opt/orca-slicer/AppRun
```

---

## Dependencies Installed

| Package | Method | Purpose |
|---------|--------|---------|
| Orca Slicer v2.3.2 | AppImage extracted to /opt | CLI 3D slicing for Ender-3 V3 Plus |

---

## Tests & Validation

- CrealityPrint v6.1.2 / v6.2.2 / v6.3.1 / v7.0.1 / v7.1.1: all segfault on `--slice 0`
- CrealityPrint v5.1.7: no headless CLI (GUI-only, no `--slice 0` support)
- Orca Slicer v2.3.2: `slice.sh proto pla` → exit 0, gcode produced, result.json with `"return_code": 0`
- Orca Slicer v2.3.2: `slice.sh production pla` → exit 0, gcode produced

---

## Known Issues / Caveats

- Orca Slicer output filenames are always `plate_1.gcode` (not input STL name)
- `result.json` from Orca reports `triangle_count` but not `print_time_s` or `filament_g` — those fields are null in JSON output
- Old Docker-based `forge-slicer` image is still in local Docker registry; purge with `docker rmi forge-slicer` if desired

---

## What's Next

- [ ] Install Orca Slicer on Typhon/Orin nodes for distributed slicing — @Salomon
- [ ] Remove deprecated Dockerfile/entrypoint.py from forge-slicer dir after 1 week — @Claude
- [ ] Wire `slice.sh` into `djinn-print-queue` dispatcher — @Salomon

---

*— Claude, 2026-06-14*
