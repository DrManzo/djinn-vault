#!/usr/bin/env bash
set -euo pipefail

INSTALL_BIN="${HOME}/.local/bin"
DATA_DIR="${HOME}/.local/share/djinn"
TRACK_DIR="${DATA_DIR}/print-track"
RECORDS_DIR="${HOME}/Obsidian/djinn/printer/prints"
SCRIPT_SRC="djinn-print-track-v2.py"

echo "djinn-print-track v2 — Install"
echo "================================"
echo ""

# ── Check websockets ──────────────────────────────────────────────────────────
echo "🔍  Checking dependencies..."
python3 -c "import websockets" 2>/dev/null || {
    echo "  websockets not found. Installing..."
    pip install --user --break-system-packages websockets
}
echo "  ✅  websockets: $(python3 -c "import websockets; print(websockets.__version__)")"

# ── Stop old service ──────────────────────────────────────────────────────────
echo ""
echo "📦  Stopping old service..."
if systemctl --user is-active djinn-print-track &>/dev/null; then
    systemctl --user stop djinn-print-track
    echo "  Service stopped."
else
    echo "  Service not running — OK."
fi

# ── Back up old script ────────────────────────────────────────────────────────
BACKUP_STAMP=$(date +%Y%m%d)
if [ -f "${INSTALL_BIN}/djinn-print-track" ]; then
    cp "${INSTALL_BIN}/djinn-print-track" "${INSTALL_BIN}/djinn-print-track.bak.${BACKUP_STAMP}"
    echo "  Backed up existing script → djinn-print-track.bak.${BACKUP_STAMP}"
fi

# ── Install new script ────────────────────────────────────────────────────────
mkdir -p "${INSTALL_BIN}"
cp "${SCRIPT_SRC}" "${INSTALL_BIN}/djinn-print-track"
chmod +x "${INSTALL_BIN}/djinn-print-track"
echo "  Installed: ${INSTALL_BIN}/djinn-print-track"

# ── Create directories ────────────────────────────────────────────────────────
mkdir -p "${TRACK_DIR}"
mkdir -p "${RECORDS_DIR}"
echo "  Ready:     ${TRACK_DIR}"
echo "  Ready:     ${RECORDS_DIR}"

# ── Filament inventory ────────────────────────────────────────────────────────
if [ ! -f "${DATA_DIR}/filament-inventory.json" ]; then
    if [ -f "filament-inventory.json" ]; then
        cp "filament-inventory.json" "${DATA_DIR}/"
        echo "  Created:   ${DATA_DIR}/filament-inventory.json"
    else
        echo '{"spools":[]}' > "${DATA_DIR}/filament-inventory.json"
        echo "  Created:   ${DATA_DIR}/filament-inventory.json (empty)"
    fi
else
    echo "  Skipped:   ${DATA_DIR}/filament-inventory.json (already exists)"
fi

# ── Systemd service ───────────────────────────────────────────────────────────
SERVICE_DIR="${HOME}/.config/systemd/user"
SERVICE_NAME="djinn-print-track.service"
mkdir -p "${SERVICE_DIR}"

if [ -f "djinn-print-track.service" ]; then
    cp "djinn-print-track.service" "${SERVICE_DIR}/${SERVICE_NAME}"
    echo "  Updated:   ${SERVICE_DIR}/${SERVICE_NAME}"
else
    # Create default service unit
    cat > "${SERVICE_DIR}/${SERVICE_NAME}" << 'SERVICEEOF'
[Unit]
Description=Djinn Print Tracker v2 — silent Moonraker print logger
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=%h/.local/bin/djinn-print-track start
Restart=on-failure
RestartSec=30

[Install]
WantedBy=default.target
SERVICEEOF
    echo "  Created:   ${SERVICE_DIR}/${SERVICE_NAME} (default)"
fi

systemctl --user daemon-reload

# ── Enable and start ──────────────────────────────────────────────────────────
echo ""
echo "🚀  Starting service..."
systemctl --user enable djinn-print-track
systemctl --user start djinn-print-track

sleep 2
if systemctl --user is-active djinn-print-track &>/dev/null; then
    echo "  ✅  Service active!"
else
    echo "  ❌  Service failed to start. Check: journalctl -u djinn-print-track -n 30 --no-pager"
fi

echo ""
echo "================================"
echo "Install complete."
echo ""
echo "  CLI:      djinn-print-track status"
echo "  Logs:     journalctl -u djinn-print-track -f"
echo "  Verify:   djinn-print-track verify"
