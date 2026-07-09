#!/bin/bash
# Build the forge-slicer Docker image.
# Run from anywhere — script resolves its own directory.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "[forge-slicer] Building Docker image..."
docker build -t forge-slicer "$SCRIPT_DIR"
echo "[forge-slicer] Build complete. Image tag: forge-slicer"
