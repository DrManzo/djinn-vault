# forge-slicer — Spec v1.0

**Owner:** Typhon's Forge  
**Status:** Ready for implementation  
**Assigned to:** Marcus  

---

## What This Is

A Docker container that wraps Creality Print in a controlled Ubuntu environment with a virtual display (Xvfb), exposing a clean CLI interface for headless STL → gcode slicing. This replaces the broken Creality Print flatpak CLI on the host.

It is a first-class Forge service — not a workaround. It will be used in production for commission and design job slicing, and is designed to be portable (runs on Salomon, Orin, or any Linux host).

---

## Why Docker + Creality Print AppImage

- Creality Print GUI is the only slicer that works reliably on this system (others failed)
- The flatpak CLI crashes on init (`calc_exclude_triangles`) — almost certainly a missing display/GL context on the host
- The AppImage (v7.1.1) is self-contained with all dependencies
- Docker gives us a clean Ubuntu + Xvfb + Mesa environment where the CLI will work
- v7.1.1 AppImage is newer than the installed flatpak (6.2.0) — likely fixes the crash

---

## Directory Structure

```
~/Obsidian/djinn/printer/forge-slicer/
  SPEC.md                        ← this file
  Dockerfile
  entrypoint.py                  ← thin wrapper: args → CrealityPrint CLI → JSON output
  profiles/
    machine/
      Calliope.json              ← Ender-3 V3 Plus 0.4 nozzle (flat format)
    process/
      Calliope-Proto.json        ← 0.28mm, 2 walls, 8% gyroid, fast
      Calliope-Production.json   ← 0.20mm, 4 walls, 18% gyroid, standard
      Calliope-Quality.json      ← 0.12mm, 4 walls, 15% crosshatch, fine
    filament/
      Calliope-PLA-Blue.json     ← Creality 1kg Blue PLA, 215°C, PA=0.042
      Calliope-PETG.json         ← generic PETG settings
      Calliope-ABS.json          ← generic ABS settings
  build.sh                       ← docker build helper
  slice.sh                       ← thin shell wrapper around docker run
```

---

## Dockerfile Requirements

Base: `ubuntu:22.04`

Dependencies to install:
- `xvfb` — virtual display (the missing piece causing flatpak CLI crash)
- `libfuse2` — required to run AppImage
- `libgl1-mesa-glx` or `libgl1` — OpenGL for slicer engine
- `libglib2.0-0`, `libdbus-1-3`, `libnss3`, `libx11-6`, `libxext6` — standard X11/Qt deps
- `python3` — for entrypoint.py
- `ca-certificates`, `curl` — for AppImage download during build

AppImage:
- Download `CrealityPrint-V7.1.1.4472-x86_64-Release.AppImage` from GitHub releases during build
- Extract it (AppImages can be run with `--appimage-extract`) to avoid FUSE requirement inside Docker
- Or mount with `--privileged` and run directly — extraction is cleaner

---

## entrypoint.py Interface

```
python3 entrypoint.py \
  --stl /input/model.stl \
  --machine /profiles/machine/Calliope.json \
  --process /profiles/process/Calliope-Proto.json \
  --filament /profiles/filament/Calliope-PLA-Blue.json \
  --output /output/ \
  [--supports yes|no]
```

Internally runs:
```bash
xvfb-run CrealityPrint \
  --load-settings "<machine>;<process>" \
  --load-filaments "<filament>" \
  --slice 0 \
  --outputdir /output/ \
  <stl>
```

Stdout: JSON on success, JSON error on failure:
```json
{
  "success": true,
  "gcode_path": "/output/model_proto_1h23m.gcode",
  "print_time_raw": "1h 23m",
  "print_time_s": 4980,
  "filament_g": 14.2,
  "filament_mm": 4821,
  "error": null
}
```

Parse print time and filament from gcode comments (Creality Print writes these as `; estimated printing time` and `; total filament used`).

---

## slice.sh (host-side wrapper)

```bash
#!/bin/bash
# Usage: slice.sh <stl_path> <process> <material> [supports=yes|no]
# Returns JSON to stdout

docker run --rm \
  -v "$(dirname $1)":/input \
  -v "$HOME/.local/share/forge/gcode":/output \
  forge-slicer \
  --stl "/input/$(basename $1)" \
  --process "$2" \
  --material "$3" \
  ${4:+--supports $4}
```

---

## Profile Format

All profiles use the flat Creality Print 7.x JSON format (NOT the old engine_data wrapped format).

**Machine profile key fields:**
```json
{
  "from": "system",
  "inherits": "fdm_creality_common",
  "instantiation": "true",
  "name": "Calliope",
  "printable_area": "0x0,300x0,300x300,0x300",
  "printable_height": "330",
  "gcode_flavor": "klipper",
  "machine_start_gcode": "M140 S0\nM104 S0\nSTART_PRINT EXTRUDER_TEMP=[nozzle_temperature_initial_layer] BED_TEMP=[bed_temperature_initial_layer]",
  "machine_end_gcode": "END_PRINT",
  "nozzle_diameter": "0.4"
}
```

**Process profile key fields (Calliope-Proto example):**
```json
{
  "type": "process",
  "from": "User",
  "inherits": "0.25mm Standard @Creality Ender-3 V3 Plus 0.4 nozzle",
  "name": "Calliope-Proto",
  "compatible_printers": ["Creality Ender-3 V3 Plus 0.4 nozzle"],
  "layer_height": "0.28",
  "wall_loops": "2",
  "sparse_infill_density": "8",
  "sparse_infill_pattern": "gyroid"
}
```

**Filament profile key fields (Calliope-PLA-Blue example):**
```json
{
  "type": "filament",
  "from": "User",
  "inherits": "Hyper PLA @Creality Ender-3 V3 Plus 0.4 nozzle",
  "name": "Calliope-PLA-Blue",
  "nozzle_temperature": "215",
  "cool_plate_temp": "60",
  "pressure_advance": "0.042"
}
```

The bundled system profiles (in the AppImage) handle all inheritance — our profiles only override what differs.

---

## build.sh

```bash
#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
docker build -t forge-slicer "$SCRIPT_DIR"
echo "forge-slicer built successfully"
```

---

## Integration with djinn-model-slice

After this is built, `djinn-model-slice` will be updated to call `slice.sh` instead of the flatpak directly. The JSON output maps directly to what djinn-model-slice already expects (gcode_path, print_time, filament_g).

---

## Validation Checklist (Marcus to verify before handoff)

- [ ] `docker build -t forge-slicer .` completes without error
- [ ] `slice.sh ~/printer-files/queue/plate_job3.stl proto pla` produces a `.gcode` file in `~/.local/share/forge/gcode/`
- [ ] JSON output includes `print_time_s` and `filament_g` (non-zero)
- [ ] `slice.sh` works with `production` and `quality` profiles too
- [ ] Container exits cleanly (exit 0 on success, exit 1 on slice failure)
- [ ] No zombie Xvfb processes left after container exits

---

## Notes

- The `compatible_printers` field must be explicitly set in process profiles — it is NOT inherited from parent profiles (verified during investigation)
- The machine profile `inherits` chain: `Calliope` → `fdm_creality_common` (bundled in AppImage)
- AppImage extraction preferred over FUSE mount for Docker — use `CrealityPrint.AppImage --appimage-extract` during build
- The `--normative-check` flag exists in CLI but takes no argument (boolean) — may be needed if normative validation blocks slicing
- WiFi send to Calliope (Moonraker at 192.168.1.114:7125) is handled separately by `djinn-confirm-print` — the container only produces gcode

---

*— Claude, 2026-06-14*
