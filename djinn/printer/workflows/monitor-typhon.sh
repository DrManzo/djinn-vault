#!/bin/bash
# Typhon-based print monitor — reusable template
# Usage: update MODEL_DIR and PIDFILE before running
# Salomon pushes this via SCP when a print starts

VAULT="/home/tf-tthq/Obsidian"
MODEL_DIR="$VAULT/djinn/printer/prints/YYYY-MM-DD_ModelName"
LOGFILE="$MODEL_DIR/monitor.log"
PRINTER="192.168.1.114:7125"
PIDFILE="/tmp/print-monitor.pid"

mkdir -p "$MODEL_DIR"
echo $$ > "$PIDFILE"

while true; do
    STATE=$(curl -s --connect-timeout 5 "http://$PRINTER/printer/objects/query?print_stats" 2>/dev/null | \
      python3 -c "import sys,json; d=json.load(sys.stdin); print(d['result']['status']['print_stats']['state'])" 2>/dev/null)
    
    if [ -z "$STATE" ] || [ "$STATE" = "standby" ] || [ "$STATE" = "complete" ] || [ "$STATE" = "error" ]; then
        echo "--- $(date -u '+%Y-%m-%d %H:%M UTC') — Print ended (state=$STATE) ---" >> "$LOGFILE"
        if [ "$STATE" = "error" ]; then
            curl -s "http://$PRINTER/server/files/klippy.log" 2>/dev/null | tail -100 > "$MODEL_DIR/error_capture.gcode" 2>/dev/null
        fi
        rm -f "$PIDFILE"
        exit 0
    fi
    
    echo "--- $(date -u '+%Y-%m-%d %H:%M UTC') ---" >> "$LOGFILE"
    curl -s --connect-timeout 5 "http://$PRINTER/printer/objects/query?print_stats&extruder&heater_bed" >> "$LOGFILE" 2>/dev/null
    echo "" >> "$LOGFILE"
    
    cd "$VAULT" && git pull --rebase --quiet 2>/dev/null
    git add "$LOGFILE" 2>/dev/null
    git -c user.name="Typhons Forge" -c user.email="typhon@djinn" commit -m "monitor: update $(date -u '+%Y-%m-%d %H:%M UTC')" --quiet 2>/dev/null || true
    git push --quiet 2>/dev/null || true
    
    sleep 60
done
