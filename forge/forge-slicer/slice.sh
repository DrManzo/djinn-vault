#!/bin/bash
# Usage: slice.sh <abs_stl_path> <profile: proto|production|quality> <material: pla|petg|abs> [supports: yes|no]
# Returns JSON to stdout.
# Example: slice.sh ~/printer-files/queue/plate_job3.stl proto pla

set -euo pipefail

STL="${1:-}"
PROFILE="${2:-}"
MATERIAL="${3:-}"
SUPPORTS="${4:-no}"
SUPPORT_TYPE="${5:-normal}"

if [[ -z "$STL" || -z "$PROFILE" || -z "$MATERIAL" ]]; then
    echo '{"success":false,"error":"Usage: slice.sh <stl> <profile: proto|production|quality> <material: pla|petg|abs> [supports: yes|no]"}'
    exit 1
fi

if [[ ! -f "$STL" ]]; then
    echo "{\"success\":false,\"error\":\"STL file not found: $STL\"}"
    exit 1
fi

# Uppercase material: pla → PLA
MATERIAL_UP="$(tr '[:lower:]' '[:upper:]' <<< "$MATERIAL")"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROFILE_DIR="${SCRIPT_DIR}/profiles"
OUTPUT_DIR="${HOME}/.local/share/forge/gcode"
mkdir -p "$OUTPUT_DIR"

# Orca Slicer binary
ORCA="/opt/orca-slicer/AppRun"

# Built-in machine profile
MACHINE="Creality Ender-3 V3 Plus 0.4 nozzle"
# Map profile names to process profile files
case "$PROFILE" in
    proto)      PROCESS_PROFILE="Calliope-Proto.json" ;;
    production) PROCESS_PROFILE="Calliope-Production.json" ;;
    quality)    PROCESS_PROFILE="Calliope-Quality.json" ;;
    airtight)   PROCESS_PROFILE="Calliope-Airtight.json" ;;
    *)
        echo "{\"success\":false,\"error\":\"Unknown profile: $PROFILE. Valid: proto, production, quality, airtight\"}"
        exit 1
        ;;
esac

# Filament file: prefer colour-specific, fall back to generic
FILENAME_PREF="Calliope-${MATERIAL_UP}-Blue.json"
FILENAME_GENERIC="Calliope-${MATERIAL_UP}.json"
if [[ -f "${PROFILE_DIR}/filament/${FILENAME_PREF}" ]]; then
    FILAMENT="${PROFILE_DIR}/filament/${FILENAME_PREF}"
elif [[ -f "${PROFILE_DIR}/filament/${FILENAME_GENERIC}" ]]; then
    FILAMENT="${PROFILE_DIR}/filament/${FILENAME_GENERIC}"
else
    echo "{\"success\":false,\"error\":\"No filament profile for material: ${MATERIAL_UP}\"}"
    exit 1
fi

# Run Orca Slicer
$ORCA \
    --load-settings \
        "/opt/orca-slicer/resources/profiles/Creality/machine/${MACHINE}.json;${PROFILE_DIR}/process/${PROCESS_PROFILE}" \
    --load-filaments "$FILAMENT" \
    --slice 0 \
    --outputdir "$OUTPUT_DIR" \
    "$STL" 2>/dev/null

ORCA_EXIT=$?

# Orca names output files plate_{n}.gcode, always starting at 1
OUTPUT_FILE="${OUTPUT_DIR}/plate_1.gcode"
RESULT_JSON="${OUTPUT_DIR}/result.json"

if [[ $ORCA_EXIT -ne 0 ]]; then
    echo "{\"success\":false,\"error\":\"OrcaSlicer exited with code ${ORCA_EXIT}\",\"gcode_path\":null}"
    exit 0
fi

if [[ ! -f "$OUTPUT_FILE" ]]; then
    echo "{\"success\":false,\"error\":\"No gcode produced at ${OUTPUT_FILE}\",\"gcode_path\":null}"
    exit 0
fi

# Extract metadata from result.json
if [[ -f "$RESULT_JSON" ]]; then
    python3 -c "
import json
with open('${RESULT_JSON}') as f:
    r = json.load(f)
plates = r.get('sliced_plates', [])
layer_count = plates[0].get('triangle_count') if plates else None
print(json.dumps({
    'success': True,
    'gcode_path': '${OUTPUT_FILE}',
    'print_time_s': None,
    'filament_g': None,
    'filament_mm': None,
    'layer_count': layer_count
}))
"
else
    echo "{\"success\":true,\"gcode_path\":\"${OUTPUT_FILE}\",\"print_time_s\":null,\"filament_g\":null,\"filament_mm\":null,\"layer_count\":null}"
fi
