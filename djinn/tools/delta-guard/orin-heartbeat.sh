#!/bin/bash
# Heartbeat — Orin (macOS iMac, Intel, CPU inference)
# Deploy: cp orin-heartbeat.sh ~/.local/bin/heartbeat && chmod +x ~/.local/bin/heartbeat
# Scheduled: ~/Library/LaunchAgents/com.djinn.heartbeat.plist (every 5 min)

VAULT="$HOME/Obsidian"
HEARTBEAT="$VAULT/djinn/communications/HEARTBEAT-orin.md"
DELTA_GUARD_PY="$VAULT/djinn/tools/delta-guard"

_OLLAMA=$(curl -s http://localhost:11434/api/tags 2>/dev/null \
          | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'{len(d[\"models\"])} models loaded')" \
          2>/dev/null || echo "N/A")
_DISK=$(df -h / | awk 'NR==2{print $5 " used (" $4 " free)"}')
_RAM=$(vm_stat 2>/dev/null | python3 -c "
import sys
stats = {}
for line in sys.stdin:
    if ':' in line:
        k, v = line.split(':', 1)
        stats[k.strip()] = v.strip().rstrip('.')
pages = 4096
free = int(stats.get('Pages free', '0').replace(',',''))
wired = int(stats.get('Pages wired down', '0').replace(',',''))
active = int(stats.get('Pages active', '0').replace(',',''))
used = (wired + active) * pages // (1024**3)
avail = free * pages // (1024**3)
print(f'{used}GB used, {avail}GB free')
" 2>/dev/null || echo "N/A")
_UPTIME=$(uptime | sed 's/.*up /up /' | sed 's/,.*//')

cat > "$HEARTBEAT" << EOF
# Heartbeat — Orin

**Last beat:** $(date -u '+%Y-%m-%d %H:%M:%S UTC')
**Machine:** Orin (192.168.1.177)
**Status:** Alive

## System

- **Uptime:** $_UPTIME
- **GPU:** Intel integrated (CPU inference only)
- **Ollama:** $_OLLAMA
- **Disk:** $_DISK
- **RAM:** $_RAM
EOF

# Only commit + push when metrics change
python3 - <<PYEOF
import sys, json
sys.path.insert(0, "$DELTA_GUARD_PY")
from delta_guard import should_fire
from timer_states import normalize_state

raw_state = {
    "ollama": """$_OLLAMA""",
    "disk":   """$_DISK""",
    "ram":    """$_RAM""",
}
state = normalize_state(raw_state, "heartbeat-orin-push")
sys.exit(0 if should_fire(state, "heartbeat-orin-push") else 1)
PYEOF

if [[ $? -eq 0 ]]; then
    cd "$VAULT" || exit 1
    git pull --rebase --quiet 2>/dev/null || true
    git add -A \
    && git commit -m "heartbeat: $(date -u '+%Y-%m-%dT%H:%MZ') — Orin" --quiet \
    && git push --quiet
fi
