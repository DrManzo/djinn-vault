# Marcus Build Prompt — forge-slicer

## Context

You are building `forge-slicer`, a Docker container that wraps Creality Print for headless STL slicing. This is part of the Djinn/Forge 3D printing pipeline for Typhon's Forge, a 3D printing commission business.

**The problem you are solving:** Creality Print's flatpak CLI crashes on the host during engine initialization (`calc_exclude_triangles` during `StaticPrintConfigs`). The root cause is almost certainly missing display/OpenGL context — the CLI tries to init rendering even in headless mode. The fix is running it inside Docker with Xvfb (virtual display) + Mesa + a clean Ubuntu environment.

**Why Creality Print specifically:** It is the only slicer that works reliably on this system. Others (CuraEngine, PrusaSlicer) were previously tried and failed. The GUI works perfectly. We are containerizing the same engine the GUI uses.

---

## What To Build

Read the full spec at:
`~/Obsidian/djinn/printer/forge-slicer/SPEC.md`

Summary of deliverables:

1. **`Dockerfile`** — Ubuntu 22.04, Xvfb, Mesa, downloads and extracts Creality Print v7.1.1 AppImage
2. **`entrypoint.py`** — takes `--stl`, `--machine`, `--process`, `--filament`, `--output` args, runs CrealityPrint via xvfb-run, parses gcode for time/filament, outputs JSON
3. **`profiles/`** — machine, process (Proto/Production/Quality), filament (PLA-Blue/PETG/ABS) in Creality Print 7.x flat JSON format
4. **`slice.sh`** — host-side shell wrapper: `slice.sh <stl> <profile> <material>` → calls docker run → returns JSON
5. **`build.sh`** — `docker build -t forge-slicer .`

All files go in: `~/Obsidian/djinn/printer/forge-slicer/`

---

## Critical Technical Details

### AppImage extraction (preferred over FUSE)
```dockerfile
RUN ./CrealityPrint.AppImage --appimage-extract && \
    mv squashfs-root /opt/creality-print
```
Then run `/opt/creality-print/AppRun` instead of the AppImage directly. This avoids needing FUSE inside Docker.

### Xvfb usage
```bash
xvfb-run --server-args="-screen 0 1024x768x24" /opt/creality-print/AppRun \
  --load-settings "<machine>;<process>" \
  --load-filaments "<filament>" \
  --slice 0 \
  --outputdir /output/ \
  /input/model.stl
```

### Profile format — CRITICAL
Creality Print 7.x uses flat JSON, NOT the old `engine_data` wrapped format. Wrong format = immediate crash with `from  unsupported` error.

**Correct process profile format:**
```json
{
  "type": "process",
  "from": "User",
  "inherits": "0.25mm Standard @Creality Ender-3 V3 Plus 0.4 nozzle",
  "name": "Calliope-Proto",
  "print_settings_id": "Calliope-Proto",
  "version": "26.1.31.15",
  "compatible_printers": ["Creality Ender-3 V3 Plus 0.4 nozzle"],
  "layer_height": "0.28",
  "wall_loops": "2",
  "sparse_infill_density": "8",
  "sparse_infill_pattern": "gyroid",
  "outer_wall_speed": "60",
  "inner_wall_speed": "80",
  "sparse_infill_speed": "80",
  "bottom_shell_layers": "2",
  "top_shell_layers": "2",
  "brim_type": "no_brim",
  "enable_support": "0"
}
```

**`compatible_printers` must be explicitly set** — it is NOT inherited from the parent profile. Without it, slicing fails with "process not compatible with printer".

**Correct filament profile format:**
```json
{
  "type": "filament",
  "from": "User",
  "inherits": "Hyper PLA @Creality Ender-3 V3 Plus 0.4 nozzle",
  "name": "Calliope-PLA-Blue",
  "filament_settings_id": "Calliope-PLA-Blue",
  "version": "26.1.31.15",
  "nozzle_temperature": "215",
  "nozzle_temperature_initial_layer": "215",
  "cool_plate_temp": "60",
  "cool_plate_temp_initial_layer": "60",
  "pressure_advance": "0.042",
  "fan_min_speed": "100",
  "fan_max_speed": "100"
}
```

**For the machine profile:** use the bundled system profile from inside the AppImage at:
`/opt/creality-print/resources/profiles/Creality/machine/Creality Ender-3 V3 Plus 0.4 nozzle.json`
Pass this directly to `--load-settings` — no need to copy/modify it.

### entrypoint.py JSON output
Parse these from the gcode file (Creality Print writes them as comments):
- `; estimated printing time (normal mode) = Xh Xm Xs` → `print_time_raw` + `print_time_s`
- `; total filament used [g] = X.XX` → `filament_g`
- `; total filament used [mm] = XXXX` → `filament_mm`

Output format:
```json
{
  "success": true,
  "gcode_path": "/output/model_proto.gcode",
  "print_time_raw": "1h 23m",
  "print_time_s": 4980,
  "filament_g": 14.2,
  "filament_mm": 4821,
  "error": null
}
```

On failure:
```json
{
  "success": false,
  "gcode_path": null,
  "print_time_raw": null,
  "print_time_s": null,
  "filament_g": null,
  "filament_mm": null,
  "error": "CrealityPrint exited with code 1: <stderr>"
}
```

### slice.sh (host-side)
```bash
#!/bin/bash
# Usage: slice.sh <abs_stl_path> <profile: proto|production|quality> <material: pla|petg|abs> [supports: yes|no]
STL="$1"
PROFILE="$2"
MATERIAL="$3"
SUPPORTS="${4:-no}"

PROFILE_DIR="$HOME/Obsidian/djinn/printer/forge-slicer/profiles"
APPIMAGE_DIR="/opt/creality-print/resources/profiles/Creality"

MACHINE="${APPIMAGE_DIR}/machine/Creality Ender-3 V3 Plus 0.4 nozzle.json"
PROCESS="${PROFILE_DIR}/process/Calliope-${PROFILE^}.json"
FILAMENT="${PROFILE_DIR}/filament/Calliope-${MATERIAL^^}-Blue.json"

# Fall back to generic filament if no color-specific one
[ ! -f "$FILAMENT" ] && FILAMENT="${PROFILE_DIR}/filament/Calliope-${MATERIAL^^}.json"

docker run --rm \
  -v "$(dirname "$STL")":/input:ro \
  -v "$HOME/.local/share/forge/gcode":/output \
  -v "$PROFILE_DIR":/profiles:ro \
  -v "${APPIMAGE_DIR}":/creality-profiles:ro \
  forge-slicer \
  --stl "/input/$(basename "$STL")" \
  --machine "/creality-profiles/machine/Creality Ender-3 V3 Plus 0.4 nozzle.json" \
  --process "/profiles/process/Calliope-${PROFILE^}.json" \
  --filament "/profiles/filament/Calliope-${MATERIAL^^}${5:+-$5}.json" \
  --output /output
```

---

## Profile Values Reference

### Calliope-Proto (fast prototype)
- layer_height: 0.28, initial_layer_print_height: 0.28
- wall_loops: 2, sparse_infill_density: 8, sparse_infill_pattern: gyroid
- outer_wall_speed: 60, inner_wall_speed: 80, sparse_infill_speed: 80
- bottom_shell_layers: 2, top_shell_layers: 2
- brim_type: no_brim, enable_support: 0

### Calliope-Production (standard)
- layer_height: 0.20, initial_layer_print_height: 0.20
- wall_loops: 4, sparse_infill_density: 18, sparse_infill_pattern: gyroid
- outer_wall_speed: 40, inner_wall_speed: 50, sparse_infill_speed: 60
- bottom_shell_layers: 3, top_shell_layers: 4
- brim_type: outer_brim, brim_width: 8, enable_support: 0

### Calliope-Quality (fine detail)
- layer_height: 0.12, initial_layer_print_height: 0.12
- wall_loops: 4, sparse_infill_density: 15, sparse_infill_pattern: crosshatch
- outer_wall_speed: 25, inner_wall_speed: 30, sparse_infill_speed: 40
- bottom_shell_layers: 4, top_shell_layers: 5
- brim_type: outer_brim, brim_width: 5, enable_support: 0

### Calliope-PLA-Blue
- nozzle_temperature: 215, bed: 60
- pressure_advance: 0.042
- fan_min_speed: 100, fan_max_speed: 100
- filament_max_volumetric_speed: 18

### Calliope-PETG
- nozzle_temperature: 235, bed: 70
- pressure_advance: 0.05
- fan_min_speed: 30, fan_max_speed: 70

### Calliope-ABS
- nozzle_temperature: 245, bed: 100
- pressure_advance: 0.04
- fan_min_speed: 0, fan_max_speed: 20

---

## Validation Steps Marcus Must Run

```bash
# 1. Build
cd ~/Obsidian/djinn/printer/forge-slicer
bash build.sh

# 2. Test with a real STL (use the wall hook from job3)
bash slice.sh ~/printer-files/queue/plate_job3.stl proto pla

# 3. Confirm output
ls ~/.local/share/forge/gcode/*.gcode
# Should see a gcode file with non-zero size

# 4. Confirm JSON output has time and filament
bash slice.sh ~/printer-files/queue/plate_job3.stl proto pla | python3 -m json.tool

# 5. Test production profile
bash slice.sh ~/printer-files/queue/plate_job3.stl production pla | python3 -m json.tool
```

---

## AppImage Download URL

```
https://github.com/CrealityOfficial/CrealityPrint/releases/download/v7.1.1/CrealityPrint-V7.1.1.4472-x86_64-Release.AppImage
```

SHA: verify after download (no official checksum published — check file size matches GitHub release page).

---

## Handoff

When done, report back:
1. Whether the AppImage CLI works inside the container (yes/no + any errors)
2. Whether xvfb-run was sufficient or additional flags were needed
3. Actual gcode filename format Creality Print uses (so we can parse it in entrypoint.py)
4. Any profile fields that needed adjustment

Do NOT modify `djinn-model-slice` — Claude will wire that up after validating the container works.

---

*Spec by Claude — 2026-06-14*
