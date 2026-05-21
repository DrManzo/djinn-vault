#!/bin/bash
# djinn-bootstrap — Rebuild Djinn on a fresh Ubuntu machine
# Prerequisites: Ubuntu 22.04+, internet connection, GitHub access
# Runtime: ~20-30 min (mostly Ollama model pulls)
#
# Usage: bash bootstrap.sh [--machine salomon|typhon]

set -euo pipefail

MACHINE="${1:-salomon}"
GITHUB_VAULT="https://github.com/DrManzo/djinn-vault.git"
VAULT="$HOME/Obsidian"

echo "=== Djinn Bootstrap — $MACHINE ==="
echo "This will rebuild Djinn from vault. Takes ~20-30 min."
echo ""

# ── 1. System dependencies ────────────────────────────────────────────────────
echo "[1/9] Installing system dependencies..."
sudo apt-get update -qq
sudo apt-get install -y -qq \
    curl git rsync nodejs npm \
    openssh-server \
    cpupower-gui 2>/dev/null || sudo apt-get install -y -qq linux-tools-common linux-tools-$(uname -r) || true

# ── 2. Ollama ─────────────────────────────────────────────────────────────────
echo "[2/9] Installing Ollama..."
if ! command -v ollama &>/dev/null; then
    curl -fsSL https://ollama.com/install.sh | sh
fi
sudo systemctl enable --now ollama
echo "  Ollama $(ollama --version)"

# ── 3. Claude Code ────────────────────────────────────────────────────────────
echo "[3/9] Installing Claude Code..."
if ! command -v claude &>/dev/null; then
    curl -fsSL https://claude.ai/install.sh | bash
fi
echo "  Claude Code $(claude --version 2>/dev/null | head -1)"

# ── 4. OpenCode ───────────────────────────────────────────────────────────────
echo "[4/9] Installing OpenCode..."
if ! command -v opencode &>/dev/null; then
    curl -fsSL https://opencode.ai/install | sh
fi

# ── 5. Clone vault ────────────────────────────────────────────────────────────
echo "[5/9] Cloning vault..."
if [ -d "$VAULT/.git" ]; then
    git -C "$VAULT" pull --quiet
    echo "  Vault updated ($(git -C "$VAULT" rev-parse --short HEAD))"
else
    git clone "$GITHUB_VAULT" "$VAULT"
    echo "  Vault cloned"
fi

# ── 6. Install djinn scripts ──────────────────────────────────────────────────
echo "[6/9] Installing djinn scripts..."
mkdir -p ~/.local/bin
SCRIPTS_SRC="$VAULT/djinn/migration/scripts"
if [ -d "$SCRIPTS_SRC" ]; then
    cp "$SCRIPTS_SRC"/djinn-* ~/.local/bin/
    chmod +x ~/.local/bin/djinn-*
    echo "  Scripts installed from vault"
else
    echo "  WARNING: $SCRIPTS_SRC not found — scripts must be manually restored"
fi

# ── 7. Systemd timers ─────────────────────────────────────────────────────────
echo "[7/9] Installing systemd timers..."
mkdir -p ~/.config/systemd/user

# heartbeat
cat > ~/.config/systemd/user/heartbeat.service << 'EOF'
[Unit]
Description=Djinn Heartbeat — Salomon
[Service]
Type=oneshot
ExecStart=%h/.local/bin/heartbeat
EOF
cat > ~/.config/systemd/user/heartbeat.timer << 'EOF'
[Unit]
Description=Djinn Heartbeat (5-min)
[Timer]
OnBootSec=60
OnUnitActiveSec=5min
Persistent=true
[Install]
WantedBy=timers.target
EOF

# vault-sync (2-min)
cat > ~/.config/systemd/user/vault-sync.service << 'EOF'
[Unit]
Description=Djinn Vault Sync
[Service]
Type=oneshot
ExecStart=%h/.local/bin/djinn-sync
EOF
cat > ~/.config/systemd/user/vault-sync.timer << 'EOF'
[Unit]
Description=Djinn Vault Sync (2-min)
[Timer]
OnBootSec=30
OnUnitActiveSec=2min
Persistent=true
[Install]
WantedBy=timers.target
EOF

# djinn-daily (8 AM)
cat > ~/.config/systemd/user/djinn-daily.service << 'EOF'
[Unit]
Description=Djinn morning prompt
After=network-online.target
[Service]
Type=oneshot
ExecStart=%h/.local/bin/djinn-morning
EOF
cat > ~/.config/systemd/user/djinn-daily.timer << 'EOF'
[Unit]
Description=Djinn morning prompt (8 AM)
[Timer]
OnCalendar=*-*-* 08:00:00
Persistent=true
[Install]
WantedBy=timers.target
EOF

# djinn-weekly (Sunday 20:00)
cat > ~/.config/systemd/user/djinn-weekly.service << 'EOF'
[Unit]
Description=Djinn weekly review
After=network-online.target
[Service]
Type=oneshot
ExecStart=%h/.local/bin/djinn-weekly
EOF
cat > ~/.config/systemd/user/djinn-weekly.timer << 'EOF'
[Unit]
Description=Djinn weekly review (Sunday 20:00)
[Timer]
OnCalendar=Sun *-*-* 20:00:00
Persistent=true
[Install]
WantedBy=timers.target
EOF

systemctl --user daemon-reload
systemctl --user enable --now heartbeat.timer vault-sync.timer djinn-daily.timer djinn-weekly.timer
echo "  Timers enabled"

# ── 8. Ollama models ──────────────────────────────────────────────────────────
echo "[8/9] Pulling Ollama models..."
if [ "$MACHINE" = "salomon" ]; then
    MODELS="qwen2.5:7b deepseek-r1:7b nomic-embed-text:latest"
    ONDEMAND="qwen2.5-coder:7b phi4:14b llama3.2-vision:11b-instruct-q4_K_M"
else
    # Typhon — lighter set
    MODELS="qwen2.5:7b deepseek-r1:7b nomic-embed-text:latest qwen2.5:1.5b"
    ONDEMAND="qwen2.5-coder:7b"
fi
for model in $MODELS; do
    echo "  Pulling $model (always-warm)..."
    ollama pull "$model"
done
echo "  On-demand models (pull when needed): $ONDEMAND"

# ── 9. Auth — requires manual steps ──────────────────────────────────────────
echo "[9/9] Auth — manual steps required:"
echo ""
echo "  a) Claude Code:"
echo "     claude /login"
echo "     (or: copy ~/.claude/.credentials.json from another machine)"
echo ""
echo "  b) Telegram + Discord tokens:"
echo "     Copy ~/.openclaw/openclaw.json from Salomon"
echo "     Contains: botToken, Discord token, gateway auth"
echo ""
echo "  c) Telegram config for scripts:"
echo "     mkdir -p ~/.config/djinn"
echo "     echo 'BOT_TOKEN=<token>' > ~/.config/djinn/telegram.conf"
echo "     echo 'CHAT_ID=7620067588' >> ~/.config/djinn/telegram.conf"
echo "     chmod 600 ~/.config/djinn/telegram.conf"
echo ""
echo "=== Bootstrap complete — auth steps above are the only manual work ==="
