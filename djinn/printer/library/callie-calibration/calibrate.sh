#!/usr/bin/env bash
# Callie Calibration Orchestrator
# Queues benchmark tests to the Ender-3 V3 Plus via Moonraker API
#
# Usage:
#   ./calibrate.sh status          — check printer state
#   ./calibrate.sh temp-tower      — slice & queue temp tower (OrcaSlicer GUI needed)
#   ./calibrate.sh cube            — slice & queue calibration cube
#   ./calibrate.sh first-layer     — slice & queue first layer square
#   ./calibrate.sh upload <gcode>  — upload gcode to Moonraker and start print
#   ./calibrate.sh list            — list queued/completed jobs

MOONRAKER="http://192.168.1.114:7125"
MODEL_DIR="/home/drmanzo/Obsidian/djinn/printer/library/callie-calibration/models"
GCODE_DIR="/home/drmanzo/Obsidian/djinn/printer/library/callie-calibration/gcode"
QUEUE="/home/drmanzo/.local/share/djinn/print-queue.json"
PRUSA="prusa-slicer"
PLA_TEMP="${PLA_TEMP:-220}"
BED_TEMP="60"
PROFILE="/home/drmanzo/.config/djinn/ender3-v3-plus.ini"

mkdir -p "$GCODE_DIR"

status() {
    echo "=== Callie Status ==="
    curl -s "$MOONRAKER/printer/info" | python3 -m json.tool 2>/dev/null
    echo ""
    curl -s "$MOONRAKER/printer/objects/query?print_stats" | python3 -c "
import sys,json
d=json.load(sys.stdin)
s=d['result']['status']['print_stats']
print(f'State: {s[\"state\"]}')
print(f'File: {s[\"filename\"] or \"(none)\"}')
print(f'Progress: {s.get(\"print_duration\",0):.0f}s')
" 2>/dev/null || echo "Moonraker unreachable"
}

upload_and_print() {
    local gcode="$1"
    local name=$(basename "$gcode" .gcode)

    echo "=== Uploading $name ==="
    curl -s -X POST "$MOONRAKER/server/files/upload" \
        -F "file=@$gcode" \
        -F "path=gcodes/calibration/" | python3 -m json.tool 2>/dev/null

    echo "=== Starting print ==="
    curl -s -X POST "$MOONRAKER/printer/print/start" \
        -d "{\"filename\":\"calibration/$name.gcode\"}" \
        -H "Content-Type: application/json" | python3 -m json.tool 2>/dev/null

    echo "=== Done! Print started. ==="
}

slice_cube() {
    local temp="${1:-$PLA_TEMP}"
    local out="$GCODE_DIR/calibration-cube-20mm-fixed.gcode"
    local stl="$MODEL_DIR/20mm_XYZ_EdgelessSafetyCalibrationCube.stl"

    echo "=== Slicing Calibration Cube (20mm) at ${temp}°C ==="
    cp "$PROFILE" /tmp/cube.ini
    sed -i "s/temperature = [0-9]*/temperature = $temp/" /tmp/cube.ini
    sed -i "s/first_layer_temperature = [0-9]*/first_layer_temperature = $temp/" /tmp/cube.ini
    sed -i "s/bed_temperature = [0-9]*/bed_temperature = $BED_TEMP/" /tmp/cube.ini
    sed -i "s/first_layer_bed_temperature = [0-9]*/first_layer_bed_temperature = $BED_TEMP/" /tmp/cube.ini

    $PRUSA --export-gcode --load /tmp/cube.ini \
        --output "$out" "$stl" 2>&1

    if [ -f "$out" ]; then
        echo "Cube gcode: $out ($(du -h "$out" | cut -f1))"
    else
        echo "ERROR: Slicing failed!"
        return 1
    fi
}

slice_first_layer() {
    local temp="${1:-$PLA_TEMP}"
    local out="$GCODE_DIR/first-layer-200x200mm-fixed.gcode"
    local stl="$MODEL_DIR/first_layer_200x200mm.stl"

    echo "=== Slicing First Layer Square (200×200mm) at ${temp}°C ==="
    cp "$PROFILE" /tmp/fl.ini
    sed -i "s/temperature = [0-9]*/temperature = $temp/" /tmp/fl.ini
    sed -i "s/first_layer_temperature = [0-9]*/first_layer_temperature = $temp/" /tmp/fl.ini
    sed -i "s/bed_temperature = [0-9]*/bed_temperature = $BED_TEMP/" /tmp/fl.ini
    sed -i "s/first_layer_bed_temperature = [0-9]*/first_layer_bed_temperature = $BED_TEMP/" /tmp/fl.ini
    sed -i "s/layer_height = [0-9.]*/layer_height = 0.3/" /tmp/fl.ini
    sed -i "s/first_layer_height = [0-9.]*/first_layer_height = 0.3/" /tmp/fl.ini
    sed -i "s/perimeter_speed = [0-9]*/perimeter_speed = 40/" /tmp/fl.ini
    sed -i "s/infill_speed = [0-9]*/infill_speed = 40/" /tmp/fl.ini
    sed -i "s/first_layer_speed = [0-9]*/first_layer_speed = 20/" /tmp/fl.ini

    $PRUSA --export-gcode --load /tmp/fl.ini \
        --output "$out" "$stl" 2>&1

    if [ -f "$out" ]; then
        echo "First layer gcode: $out ($(du -h "$out" | cut -f1))"
    else
        echo "ERROR: Slicing failed!"
        return 1
    fi
}

slice_temp_tower() {
    echo "=== Temperature Tower ==="
    echo ""
    echo "Path of least resistance: OrcaSlicer GUI"
    echo ""
    echo "Steps:"
    echo "  1. Launch: /home/drmanzo/Applications/OrcaSlicer_V2.3.2.AppImage"
    echo "  2. Load: $MODEL_DIR/temperature-tower-with-rounds-_v003.stl"
    echo "  3. Printer: Creality Ender-3 V3 Plus 0.4 nozzle"
    echo "  4. Process: 0.20mm Standard @Creality Ender3V3Plus"
    echo "  5. Calibration → Temperature → select tower STL"
    echo "  6. Range: 180-230°C, 5°C steps (PLA)"
    echo "  7. Slice → Export gcode"
    echo "  8. mv exported.gcode $GCODE_DIR/temp-tower-fixed.gcode"
    echo "  9. Run: $0 upload $GCODE_DIR/temp-tower-fixed.gcode"
    echo ""
    echo "Or manually upload via Moonraker:"
    echo "  curl -F \"file=@your-temp-tower-fixed.gcode\" $MOONRAKER/server/files/upload"
    echo "  curl -X POST $MOONRAKER/printer/print/start -d '{\"filename\":\"temp-tower-fixed.gcode\"}'"
}

list_queue() {
    echo "=== Queue Status ==="
    python3 -c "
import json
with open('$QUEUE') as f:
    q = json.load(f)
print(f'Next job ID: {q[\"next_id\"]}')
print(f'Total jobs: {len(q[\"jobs\"])}')
for j in q['jobs']:
    print(f'  Job {j[\"id\"]}: {j[\"status\"]} - {j.get(\"note\",\"(no note)\")}')
"
}

case "${1:-help}" in
    status)      status ;;
    cube)        slice_cube "$2" ;;
    first-layer) slice_first_layer "$2" ;;
    temp-tower)  slice_temp_tower ;;
    upload)      upload_and_print "$2" ;;
    list)        list_queue ;;
    *)
        echo "Usage: $0 {status|cube|first-layer|temp-tower|upload <gcode>|list}"
        echo ""
        echo "Environment:"
        echo "  PLA_TEMP=<temp>    Print temperature (default: 220)"
        exit 1
        ;;
esac
