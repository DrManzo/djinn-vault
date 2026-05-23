# Print Job Workflow — Agent-Replayable

## Purpose

Standardized end-to-end workflow for any 3D print job on the Ender-3 V3 Plus. Any Djinn agent (Salomon, Typhon, Claude) can follow this to produce consistent gcode with full logging.

## Inputs

- **Source file:** STL or 3MF in `~/Downloads/`
- **Print directory:** `~/Obsidian/djinn/printer/prints/YYYY-MM-DD_ModelName/`
- **User decisions captured in:** `plan.md`

## Directory Structure

```
prints/YYYY-MM-DD_ModelName/
├── workflow.sh           ← exact commands run
├── plan.md               ← analysis + user decisions + rationale
├── model_analysis.json   ← machine-readable geometry report
├── model_raw.stl         ← original extracted model
├── model_centered.stl    ← model centered at origin
├── machine_profile.json  ← OrcaSlicer machine config used
├── process_profile.json  ← OrcaSlicer process config used  
├── filament_profile.json ← OrcaSlicer filament config used
├── plate_1.gcode         ← final gcode (rename on upload)
├── preflight.log         ← repair + slice output
├── monitor.log           ← per-layer progress (populated during print)
├── error_capture.gcode   ← last 50 lines before crash
└── postmortem.md         ← what happened and why
```

## Step-by-Step

### Step 0 — Prepare
```bash
mkdir -p "~/Obsidian/djinn/printer/prints/$(date +%F)_ModelName"
```

### Step 1 — Analyze Model
```bash
# Extract info from source
prusa-slicer --info "source.3mf" 2>&1 | tee model_analysis.txt

# Export STL
prusa-slicer --export-stl --output /tmp/model_raw.stl "source.3mf"

# Analyze overhangs (Python script — see printer/workflows/analyze.py)
python3 analyze_stl.py /tmp/model_raw.stl > model_analysis.json
```

### Step 2 — Center Model
```bash
prusa-slicer --align-xy 0,0 \
  --export-stl --output /tmp/model_centered.stl /tmp/model_raw.stl
```

### Step 3 — Create Profiles

Three JSON profiles are needed. Copy templates from `workflows/templates/`:

**Machine profile** — `machine_profile.json`:
```json
{
  "type": "machine",
  "name": "Creality Ender-3 V3 Plus 0.4 nozzle",
  "inherits": "Creality Ender-3 V3 Plus 0.4 nozzle",
  "from": "user",
  "instantiation": "true",
  "printable_area": ["0x0", "300x0", "300x300", "0x300"],
  "printable_height": "330",
  "machine_start_gcode": "M140 S[bed_temperature_initial_layer_single]\nM104 S[nozzle_temperature_initial_layer]\nG28\nM190 S[bed_temperature_initial_layer_single]\nM109 S[nozzle_temperature_initial_layer]\nSET_IDLE_TIMEOUT TIMEOUT=7200",
  "machine_end_gcode": "M104 S0\nM140 S0\nG28 X0\nM84\nSET_IDLE_TIMEOUT TIMEOUT=600"
}
```

**Filament profile** — `filament_profile.json`:
```json
{
  "type": "filament",
  "name": "Print PLA @Creality Ender3V3Plus",
  "inherits": "fdm_filament_pla",
  "from": "user",
  "instantiation": "true",
  "compatible_printers": ["Creality Ender-3 V3 Plus 0.4 nozzle"],
  "nozzle_temperature": ["220"],
  "nozzle_temperature_initial_layer": ["220"],
  "textured_plate_temp": ["55"],
  "textured_plate_temp_initial_layer": ["55"],
  "filament_max_volumetric_speed": ["15"]
}
```

**Process profile** — `process_profile.json`:
```json
{
  "type": "process",
  "name": "Print Job @Creality Ender3V3Plus",
  "inherits": "0.16mm Optimal @Creality Ender3V3Plus 0.4 nozzle",
  "from": "user",
  "instantiation": "true",
  "compatible_printers": ["Creality Ender-3 V3 Plus 0.4 nozzle"],
  "wall_loops": "4",
  "sparse_infill_density": "15%",
  "sparse_infill_pattern": "gyroid",
  "enable_support": "1",
  "support_type": "normal(auto)",
  "support_threshold_angle": "25",
  "support_on_build_plate_only": "1",
  "layer_change_gcode": "G92 E0"
}
```

### Step 4 — Slice
```bash
"/home/drmanzo/Applications/OrcaSlicer_V2.3.2.AppImage" \
  --load-filaments "filament_profile.json" \
  --load-settings "machine_profile.json;process_profile.json" \
  --slice 1 \
  --outputdir "prints/YYYY-MM-DD_ModelName/" \
  "/tmp/model_centered.stl" 2>&1 | tee preflight.log
```

### Step 5 — Verify Gcode
```bash
head -40 prints/YYYY-MM-DD_ModelName/plate_1.gcode
```
Check: nozzle temp (220°C), bed temp (55°C), M73 estimated time, support headers present.

### Step 6 — Upload to Printer (manual or automatic)
```bash
# Rename gcode
cp plate_1.gcode modelname.gcode

# Option A — via Moonraker API
curl -F "file=@modelname.gcode" \
  "http://192.168.1.114:7125/server/files/upload"

# Option B — via SCP (if Moonraker unreachable)
curl -X POST \
  -F "file=@modelname.gcode" \
  -F "print=true" \
  "http://192.168.1.114:7125/server/files/upload"
```

### Step 7 — Start Print
```bash
curl -X POST \
  "http://192.168.1.114:7125/printer/print/start" \
  -H "Content-Type: application/json" \
  -d '{"filename":"modelname.gcode"}'
```

### Step 8 — Monitor (during print)
Poll every 30s and log to `monitor.log`:
```bash
while true; do
  curl -s "http://192.168.1.114:7125/printer/objects/query?print_stats&extruder&heater_bed" \
    >> monitor.log 2>&1
  echo "---" >> monitor.log
  sleep 30
done
```

### Step 9 — Error Capture (on failure)
```bash
# Get last 50 gcode lines before failure
tail -50 plate_1.gcode > error_capture.gcode

# Get klippy log excerpt
curl -s "http://192.168.1.114:7125/server/files/klippy.log" | tail -100 >> error_capture.gcode

# Write postmortem
cat > postmortem.md << 'EOF'
# Postmortem — ModelName
**Status:** FAILED/COMPLETED
**Failure at layer:** X
**Error:** description
**Root cause:** analysis
**Fix for next attempt:** suggestion
EOF
```

### Step 10 — Report
Append to COMMS.md with summary: print name, status, duration, errors, link to print directory.

## Success Criteria
1. ✅ Gcode generated without errors
2. ✅ Temperatures: 220°C nozzle / 55°C bed (PLA)
3. ✅ Supports enabled for >25° overhangs
4. ✅ Brim present for tall prints
5. ✅ Estimated time < 24h
6. ✅ OrcaSlicer result.json shows "Success"

## Notes
- The `M140 S0 / M104 S0` before `START_PRINT` pattern is AVOIDED — use direct preheat instead
- `verify_heater` is relaxed in printer.cfg (check_gain_time: 120, max_error: 999)
- Layer change gcode must include `G92 E0` when using relative extrusion (`M83`)
- Always use `--load-filaments` for filament profiles (not `--load-settings`)
