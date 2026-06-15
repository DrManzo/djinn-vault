#!/bin/bash
# Usage: slice.sh <abs_stl_path> <profile: proto|production|quality> <material: pla|petg|abs> [supports: yes|no]
# Returns JSON to stdout.
# Example: slice.sh ~/printer-files/queue/plate_job3.stl proto pla

set -euo pipefail

STL="${1:-}"
PROFILE="${2:-}"
MATERIAL="${3:-}"
SUPPORTS="${4:-no}"

if [[ -z "$STL" || -z "$PROFILE" || -z "$MATERIAL" ]]; then
    echo '{"success":false,"error":"Usage: slice.sh <stl> <profile: proto|production|quality> <material: pla|petg|abs> [supports: yes|no]"}'
    exit 1
fi

if [[ ! -f "$STL" ]]; then
    echo "{\"success\":false,\"error\":\"STL file not found: $STL\"}"
    exit 1
fi

# Capitalise profile name: proto → Proto, production → Production, quality → Quality
PROFILE_CAP="$(tr '[:lower:]' '[:upper:]' <<< "${PROFILE:0:1}")${PROFILE:1}"
# Uppercase material: pla → PLA
MATERIAL_UP="$(tr '[:lower:]' '[:upper:]' <<< "$MATERIAL")"

PROFILE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/profiles && pwd)"
OUTPUT_DIR="${HOME}/.local/share/forge/gcode"
mkdir -p "$OUTPUT_DIR"

# AppImage resources are mounted at /creality-profiles inside the container.
# On the host they live at /opt/creality-print/resources/profiles/Creality
# (populated when the container image is built via AppImage extraction).
# We mount the host path in so entrypoint.py can find the bundled machine profile.
CREALITY_RESOURCES="/opt/creality-print/resources/profiles/Creality"
# If the host doesn't have the extracted AppImage, fall back to what's inside
# the image by skipping the machine mount — the image already has it.
MACHINE_MOUNT_ARGS=()
if [[ -d "$CREALITY_RESOURCES" ]]; then
    MACHINE_MOUNT_ARGS=("-v" "${CREALITY_RESOURCES}:/creality-profiles:ro")
    MACHINE_ARG="/creality-profiles/machine/Creality Ender-3 V3 Plus 0.4 nozzle.json"
else
    # Fall back: machine profile is baked into the image at /opt/creality-print
    MACHINE_ARG="/opt/creality-print/resources/profiles/Creality/machine/Creality Ender-3 V3 Plus 0.4 nozzle.json"
fi

# Filament file: prefer colour-specific (e.g. Calliope-PLA-Blue.json),
# fall back to generic (e.g. Calliope-PLA.json).
FILAMENT_FILE_PREF="${PROFILE_DIR}/filament/Calliope-${MATERIAL_UP}-Blue.json"
FILAMENT_FILE_GENERIC="${PROFILE_DIR}/filament/Calliope-${MATERIAL_UP}.json"
if [[ -f "$FILAMENT_FILE_PREF" ]]; then
    FILAMENT_CONTAINER="/profiles/filament/Calliope-${MATERIAL_UP}-Blue.json"
elif [[ -f "$FILAMENT_FILE_GENERIC" ]]; then
    FILAMENT_CONTAINER="/profiles/filament/Calliope-${MATERIAL_UP}.json"
else
    echo "{\"success\":false,\"error\":\"No filament profile for material: ${MATERIAL_UP}\"}"
    exit 1
fi

docker run --rm \
    -v "$(dirname "$STL")":/input:ro \
    -v "$OUTPUT_DIR":/output \
    -v "$PROFILE_DIR":/profiles:ro \
    "${MACHINE_MOUNT_ARGS[@]}" \
    forge-slicer \
    --stl "/input/$(basename "$STL")" \
    --machine "$MACHINE_ARG" \
    --process "/profiles/process/Calliope-${PROFILE_CAP}.json" \
    --filament "$FILAMENT_CONTAINER" \
    --output /output \
    --supports "$SUPPORTS"
