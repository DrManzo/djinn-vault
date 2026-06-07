#!/bin/bash
# Heartbeat — Typhon
# Drop this at ~/.local/bin/heartbeat on Typhon (192.168.1.113)
# and restart the heartbeat.service there.
#
# Requires: djinn/tools/delta-guard/ in the vault (already committed)
# On Typhon: cp ~/Obsidian/djinn/tools/delta-guard/typhon-heartbeat.sh ~/.local/bin/heartbeat
#            chmod +x ~/.local/bin/heartbeat
#            systemctl --user restart heartbeat

VAULT="$HOME/Obsidian"
HEARTBEAT="$VAULT/djinn/communications/HEARTBEAT-typhon.md"
DELTA_GUARD_PY="$VAULT/djinn/tools/delta-guard"

_GPU=$(nvidia-smi --query-gpu=name,temperature.gpu,utilization.gpu,memory.used,memory.total \
       --format=csv,noheader,nounits 2>/dev/null || echo "N/A")
_OLLAMA=$(curl -s http://localhost:11434/api/tags 2>/dev/null \
          | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'{len(d[\"models\"])} models loaded')" \
          2>/dev/null || echo "N/A")
_DISK=$(df -h / | awk 'NR==2{print $5 " used (" $4 " free)"}')
_RAM=$(free -h | awk 'NR==2{print $3 "/" $2 " used, " $4 " free"}')
_UPTIME=$(uptime -p 2>/dev/null || echo "N/A")

cat > "$HEARTBEAT" << EOF
# Heartbeat — Typhon

**Last beat:** $(date -u '+%Y-%m-%d %H:%M:%S UTC')
**Machine:** Typhon (192.168.1.113)
**Status:** Alive

## System

- **Uptime:** $_UPTIME
- **GPU:** $_GPU
- **Ollama:** $_OLLAMA
- **Disk:** $_DISK
- **RAM:** $_RAM
EOF

# Only commit + push when system metrics change
python3 - <<PYEOF
import sys, json
sys.path.insert(0, "$DELTA_GUARD_PY")
from delta_guard import should_fire
from timer_states import normalize_state

raw_state = {
    "gpu":    """$_GPU""",
    "ollama": """$_OLLAMA""",
    "disk":   """$_DISK""",
    "ram":    """$_RAM""",
}
state = normalize_state(raw_state, "heartbeat-typhon-push")
sys.exit(0 if should_fire(state, "heartbeat-typhon-push") else 1)
PYEOF

if [[ $? -eq 0 ]]; then
    cd "$VAULT" || exit 1
    git add -A \
    && git commit -m "heartbeat: $(date -u '+%Y-%m-%dT%H:%MZ') — Typhon" --quiet \
    && git push --quiet
fi
