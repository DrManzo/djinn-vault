#!/usr/bin/env bash
# =============================================================================
# tablet-setup.sh — Djinn Tablet Bootstrap
# Run from: Salomon (drmanzo@192.168.1.225)
# Target:   Samsung Galaxy Tab S (SM-T738U / 192.168.1.45)
# Purpose:  Configure the Tablet as a full Djinn development node
#           — vault sync, SSH keys, dev tooling, Termux bootstrap
# =============================================================================
# Usage:
#   chmod +x tablet-setup.sh
#   ./tablet-setup.sh
#
# Requirements on Salomon:
#   - adb (Android Debug Bridge)   → sudo apt install adb
#   - Tablet reachable via WiFi ADB or USB
#
# Requirements on Tablet (install manually before running):
#   - Termux (from F-Droid — NOT Play Store)
#   - Termux:API
#   - Obsidian Mobile
#   - GitHub Mobile (optional but recommended)
# =============================================================================

set -euo pipefail

# ── Colors ────────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

log()  { echo -e "${GREEN}[✓]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
info() { echo -e "${BLUE}[→]${NC} $1"; }
err()  { echo -e "${RED}[✗]${NC} $1"; exit 1; }

# ── Config ────────────────────────────────────────────────────────────────────
VAULT="$HOME/Obsidian"
DJINN="$VAULT/djinn"
TABLET_SERIAL="192.168.1.45:5555"       # WiFi ADB — SM-T738U on LAN
SALOMON_IP="192.168.1.225"
OLLAMA_PORT="11434"
OPENCLAW_PORT="18789"
SSH_KEY="$HOME/.ssh/tablet_ed25519"      # Key we generate FOR the tablet
REPO_URL="https://github.com/DrManzo/djinn-vault.git"

# Vault location on the tablet (confirmed path)
TABLET_VAULT_PATH="/storage/emulated/0/Obsidian"

# Termux home on the tablet (ADB shell context)
TERMUX_HOME="/data/data/com.termux/files/home"
TERMUX_SSH="$TERMUX_HOME/.ssh"

# ── Banner ────────────────────────────────────────────────────────────────────
echo -e ""
echo -e "${BOLD}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║       DJINN TABLET BOOTSTRAP — Salomon → Tablet      ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════════════════════╝${NC}"
echo -e ""

# =============================================================================
# STEP 1 — Verify ADB + Tablet Connected
# =============================================================================
info "Step 1: Verifying ADB connection..."

if ! command -v adb &>/dev/null; then
    err "adb not found. Run: sudo apt install adb"
fi

adb start-server &>/dev/null

DEVICES=$(adb devices | grep -v 'List of devices' | grep -v '^$')
if echo "$DEVICES" | grep -q "$TABLET_SERIAL"; then
    log "Tablet found: $TABLET_SERIAL"
elif echo "$DEVICES" | grep -q 'device$'; then
    warn "Tablet connected but serial not matched — proceeding anyway"
else
    err "No tablet detected. Check: adb connect 192.168.1.45:5555"
fi

# Check Termux is installed
if ! adb -s "$TABLET_SERIAL" shell pm list packages 2>/dev/null | grep -q 'com.termux'; then
    err "Termux not found on tablet. Install from F-Droid first: https://f-droid.org/packages/com.termux/"
fi
log "Termux detected on tablet"

# =============================================================================
# STEP 2 — Generate SSH Key for Tablet (on Salomon)
# =============================================================================
info "Step 2: Generating tablet SSH key pair on Salomon..."

if [[ -f "$SSH_KEY" ]]; then
    warn "Key already exists at $SSH_KEY — skipping generation"
else
    ssh-keygen -t ed25519 -C "tablet@djinn" -f "$SSH_KEY" -N ""
    log "Generated: $SSH_KEY"
fi

TABLET_PUBKEY=$(cat "${SSH_KEY}.pub")

# Add tablet's public key to Salomon's authorized_keys
if ! grep -qF "$TABLET_PUBKEY" "$HOME/.ssh/authorized_keys" 2>/dev/null; then
    echo "$TABLET_PUBKEY" >> "$HOME/.ssh/authorized_keys"
    log "Tablet public key added to Salomon authorized_keys"
else
    warn "Tablet public key already in Salomon authorized_keys"
fi

# Add to Typhon's authorized_keys via SSH
info "Adding tablet key to Typhon..."
if ssh -o ConnectTimeout=5 tf-tthq@192.168.1.113 \
    "echo '$TABLET_PUBKEY' >> ~/.ssh/authorized_keys && echo 'added'" 2>/dev/null; then
    log "Tablet key added to Typhon"
else
    warn "Could not reach Typhon — add manually later"
fi

# Add to Orion's authorized_keys via SSH
info "Adding tablet key to Orion..."
if ssh -o ConnectTimeout=5 orin \
    "echo '$TABLET_PUBKEY' >> ~/.ssh/authorized_keys && echo 'added'" 2>/dev/null; then
    log "Tablet key added to Orion"
else
    warn "Could not reach Orion — add manually later"
fi

# =============================================================================
# STEP 3 — Push SSH Keys to Tablet
# =============================================================================
info "Step 3: Pushing SSH keys to tablet /sdcard/..."

adb -s "$TABLET_SERIAL" push "$SSH_KEY" "/sdcard/tablet_ed25519"
adb -s "$TABLET_SERIAL" push "${SSH_KEY}.pub" "/sdcard/tablet_ed25519.pub"
log "SSH keys pushed to /sdcard/"

# =============================================================================
# STEP 4 — Build Termux Bootstrap Script
# =============================================================================
info "Step 4: Building Termux bootstrap script..."

TERMUX_BOOTSTRAP="/tmp/djinn-termux-bootstrap.sh"

cat > "$TERMUX_BOOTSTRAP" << 'TERMUX_EOF'
#!/data/data/com.termux/files/usr/bin/bash
# ============================================================
# djinn-termux-bootstrap.sh
# Run INSIDE Termux on the Tablet
# ============================================================
set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'
log()  { echo -e "${GREEN}[✓]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
info() { echo -e "${BLUE}[→]${NC} $1"; }

SALOMON_IP="192.168.1.225"
TYPHON_IP="192.168.1.113"
ORION_IP="192.168.1.176"
VAULT_REPO="https://github.com/DrManzo/djinn-vault.git"

# ── Confirmed vault location on this tablet
OBSIDIAN_VAULT="/storage/emulated/0/Obsidian"

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║     DJINN TERMUX BOOTSTRAP — Tablet Node         ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

# ── Storage access first (needed before anything else) ───
info "Requesting storage access..."
termux-setup-storage
echo ""
warn ">>> APPROVE the storage permission popup NOW, then press ENTER to continue"
read -r _
log "Storage access granted — continuing"

# ── Package setup ────────────────────────────────────────
info "Updating Termux packages..."
termux-change-repo
pkg update -y && pkg upgrade -y

info "Installing core packages..."
pkg install -y \
    openssh \
    git \
    curl \
    wget \
    python \
    nodejs-lts \
    jq \
    vim \
    nano \
    tmux \
    htop \
    tree \
    zip \
    unzip \
    tar \
    rsync \
    nmap \
    netcat-openbsd \
    iproute2 \
    dnsutils \
    clang \
    make \
    termux-api
log "Core packages installed"

# ── SSH key setup ─────────────────────────────────────────
info "Setting up SSH keys..."
mkdir -p ~/.ssh
chmod 700 ~/.ssh

if [[ -f /sdcard/tablet_ed25519 ]]; then
    cp /sdcard/tablet_ed25519 ~/.ssh/id_ed25519
    cp /sdcard/tablet_ed25519.pub ~/.ssh/id_ed25519.pub
    chmod 600 ~/.ssh/id_ed25519
    chmod 644 ~/.ssh/id_ed25519.pub
    log "SSH key installed from /sdcard/"
else
    warn "SSH key not found at /sdcard/tablet_ed25519 — generating new pair"
    ssh-keygen -t ed25519 -C "tablet@djinn" -f ~/.ssh/id_ed25519 -N ""
    warn "Public key (add to Salomon/Typhon/Orion authorized_keys):"
    cat ~/.ssh/id_ed25519.pub
fi

# ── SSH config ────────────────────────────────────────────
info "Writing SSH config..."
cat > ~/.ssh/config << 'SSH_CONF'
Host salomon
    HostName 192.168.1.225
    User drmanzo
    IdentityFile ~/.ssh/id_ed25519
    ServerAliveInterval 60

Host typhon
    HostName 192.168.1.113
    User tf-tthq
    IdentityFile ~/.ssh/id_ed25519
    ServerAliveInterval 60

Host orion
    HostName 192.168.1.176
    User javiermanzo
    IdentityFile ~/.ssh/id_ed25519
    ServerAliveInterval 60
SSH_CONF
chmod 600 ~/.ssh/config
log "SSH config written"

# ── Git setup ─────────────────────────────────────────────
info "Configuring git..."
git config --global user.name "DrManzo"
git config --global user.email "djinnstudio@gmail.com"
git config --global core.editor "nano"
git config --global pull.rebase false
git config --global init.defaultBranch main
git config --global credential.helper store
log "Git configured"

# ── Sync vault into Obsidian folder ──────────────────────
# Vault lives at /storage/emulated/0/Obsidian (confirmed path)
# Git-manage it directly there so Obsidian picks it up immediately
info "Syncing djinn-vault into $OBSIDIAN_VAULT ..."

if [[ -d "$OBSIDIAN_VAULT/.git" ]]; then
    warn "Vault already a git repo — pulling latest"
    git -C "$OBSIDIAN_VAULT" pull
elif [[ -d "$OBSIDIAN_VAULT" ]] && [[ "$(ls -A $OBSIDIAN_VAULT)" ]]; then
    warn "$OBSIDIAN_VAULT exists with files but is not a git repo"
    warn "Initializing git in existing vault and setting remote..."
    git -C "$OBSIDIAN_VAULT" init
    git -C "$OBSIDIAN_VAULT" remote add origin "$VAULT_REPO"
    git -C "$OBSIDIAN_VAULT" fetch origin
    git -C "$OBSIDIAN_VAULT" checkout -b main --track origin/main 2>/dev/null || \
    git -C "$OBSIDIAN_VAULT" branch --set-upstream-to=origin/main main
    git -C "$OBSIDIAN_VAULT" pull origin main
    log "Vault initialized and synced at $OBSIDIAN_VAULT"
else
    # Empty or missing — clone directly into it
    mkdir -p "$(dirname $OBSIDIAN_VAULT)"
    git clone "$VAULT_REPO" "$OBSIDIAN_VAULT"
    log "Vault cloned to $OBSIDIAN_VAULT"
fi

# Also keep a Termux-home reference symlink
if [[ ! -L "$HOME/vault" ]]; then
    ln -s "$OBSIDIAN_VAULT" "$HOME/vault"
    log "Symlink: ~/vault → $OBSIDIAN_VAULT"
fi

# ── Djinn CLI aliases ─────────────────────────────────────
info "Writing djinn shell aliases..."
cat >> ~/.bashrc << 'ALIASES'

# ── Djinn Fleet ──────────────────────────────────────────
export SALOMON="192.168.1.225"
export TYPHON="192.168.1.113"
export ORION="192.168.1.176"
export VAULT="/storage/emulated/0/Obsidian"

alias djinn-ssh-salomon='ssh salomon'
alias djinn-ssh-typhon='ssh typhon'
alias djinn-ssh-orion='ssh orion'
alias vault-pull='git -C "$VAULT" pull'
alias vault-push='git -C "$VAULT" add -A && git -C "$VAULT" commit -m "tablet: $(date +%Y-%m-%d %H:%M)" && git -C "$VAULT" push'
alias vault-log='git -C "$VAULT" log --oneline -20'
alias vault-status='git -C "$VAULT" status'

# Query Ollama on Salomon
djinn-ask() {
    local prompt="$1"
    local model="${2:-qwen2.5:7b}"
    local host="${3:-$SALOMON}"
    curl -s "http://$host:11434/api/generate" \
        -d "{\"model\":\"$model\",\"prompt\":\"$prompt\",\"stream\":false}" \
        | python -c "import sys,json; print(json.load(sys.stdin)['response'])"
}

# Query heavy model on Orion
djinn-ask-orion() {
    djinn-ask "$1" "llama3.3:70b" "$ORION"
}

# Push a note into vault inbox
djinn-note() {
    local note="$1"
    local ts=$(date +%Y-%m-%d)
    local inbox="$VAULT/djinn/inbox/${ts}-tablet.md"
    echo -e "\n## $(date +%H:%M)\n$note" >> "$inbox"
    echo "Note saved to $inbox"
}

# Fleet ping status
djinn-status() {
    echo "--- Fleet Ping ---"
    for ip in "salomon:192.168.1.225" "typhon:192.168.1.113" "orion:192.168.1.176"; do
        name=$(echo $ip | cut -d: -f1)
        addr=$(echo $ip | cut -d: -f2)
        if ping -c1 -W1 "$addr" &>/dev/null 2>&1; then
            echo "  ✓ $name ($addr) online"
        else
            echo "  ✗ $name ($addr) offline"
        fi
    done
}

# List Ollama models available on Salomon
djinn-models() {
    curl -s "http://$SALOMON:11434/api/tags" \
        | python -c "import sys,json; [print(' ',m['name']) for m in json.load(sys.stdin)['models']]"
}
ALIASES
log "Shell aliases written to ~/.bashrc"

# ── Python dev setup ─────────────────────────────────────
info "Installing Python dev tools..."
pip install --upgrade pip setuptools wheel
pip install \
    requests \
    httpx \
    rich \
    typer \
    pydantic \
    python-dotenv \
    ollama \
    openai
log "Python packages installed"

# ── Node/npm tools ────────────────────────────────────────
info "Installing Node tools..."
npm install -g prettier typescript ts-node
log "Node tools installed"

# ── Vault auto-sync boot script ───────────────────────────
info "Setting up vault auto-sync on boot..."
pkg install -y termux-services 2>/dev/null || true
mkdir -p ~/.termux/boot
cat > ~/.termux/boot/vault-sync.sh << 'BOOT'
#!/data/data/com.termux/files/usr/bin/bash
# Auto-pull vault every 5 min after Termux boots
while true; do
    git -C "/storage/emulated/0/Obsidian" pull --ff-only 2>/dev/null
    sleep 300
done &
BOOT
chmod +x ~/.termux/boot/vault-sync.sh
log "Boot sync script written (~/.termux/boot/vault-sync.sh)"

# ── SSH connection tests ──────────────────────────────────
info "Testing SSH connections to fleet..."
for entry in "salomon $SALOMON_IP" "typhon $TYPHON_IP" "orion $ORION_IP"; do
    name=$(echo $entry | cut -d' ' -f1)
    ip=$(echo $entry | cut -d' ' -f2)
    if ssh -o ConnectTimeout=5 -o BatchMode=yes "$name" 'echo ok' &>/dev/null; then
        log "SSH → $name ($ip): OK"
    else
        warn "SSH → $name ($ip): FAILED (key may need to be added to authorized_keys)"
    fi
done

# ── Ollama API test ───────────────────────────────────────
info "Testing Ollama API on Salomon..."
if curl -s --connect-timeout 5 "http://$SALOMON_IP:11434/api/tags" \
    | python -c "import sys,json; models=json.load(sys.stdin)['models']; [print(' ',m['name']) for m in models]" 2>/dev/null; then
    log "Ollama API: reachable — models listed above"
else
    warn "Ollama API: not reachable (check WiFi / Salomon status)"
fi

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║         TABLET BOOTSTRAP COMPLETE ✓              ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""
echo "  Vault:       /storage/emulated/0/Obsidian"
echo "  Vault link:  ~/vault"
echo ""
echo "  Run now:"
echo "    source ~/.bashrc"
echo "    ssh salomon          ← SSH into Salomon"
echo "    djinn-status         ← ping fleet"
echo "    djinn-models         ← list Ollama models"
echo "    djinn-ask 'hello'    ← test AI query"
echo "    vault-pull           ← sync vault"
echo ""
echo "  Obsidian:"
echo "    Vault is already at /storage/emulated/0/Obsidian"
echo "    Open Obsidian → it should auto-detect the existing vault"
echo ""
TERMUX_EOF

log "Termux bootstrap script built"

# =============================================================================
# STEP 5 — Push Bootstrap Script to Tablet
# =============================================================================
info "Step 5: Pushing bootstrap script to tablet..."
adb -s "$TABLET_SERIAL" push "$TERMUX_BOOTSTRAP" "/sdcard/djinn-termux-bootstrap.sh"
log "Bootstrap pushed to /sdcard/djinn-termux-bootstrap.sh"

# =============================================================================
# STEP 6 — Push Critical Vault Docs
# =============================================================================
info "Step 6: Pushing critical vault docs to /sdcard/djinn-docs/..."
adb -s "$TABLET_SERIAL" shell mkdir -p /sdcard/djinn-docs/

CRITICAL_FILES=(
    "$DJINN/AGENTS.md"
    "$DJINN/INFRASTRUCTURE.md"
    "$DJINN/SYSTEM-STATE.md"
    "$DJINN/ROUTING.md"
    "$DJINN/GATEWAY.md"
    "$DJINN/machines/TABLET.md"
    "$DJINN/djinn-cli-guide.md"
    "$DJINN/communications/COMMS.md"
)

for f in "${CRITICAL_FILES[@]}"; do
    if [[ -f "$f" ]]; then
        adb -s "$TABLET_SERIAL" push "$f" "/sdcard/djinn-docs/"
        log "Pushed: $(basename $f)"
    else
        warn "Missing: $f — skipping"
    fi
done

# =============================================================================
# STEP 7 — Final Instructions
# =============================================================================
echo ""
echo -e "${BOLD}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║           SALOMON-SIDE SETUP COMPLETE ✓                   ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Pushed to tablet:${NC}"
echo "  /sdcard/djinn-termux-bootstrap.sh  ← run this inside Termux"
echo "  /sdcard/tablet_ed25519             ← private SSH key"
echo "  /sdcard/tablet_ed25519.pub         ← public SSH key"
echo "  /sdcard/djinn-docs/*.md            ← critical vault docs"
echo ""
echo -e "${YELLOW}NOW on the Tablet — open Termux and run:${NC}"
echo ""
echo "    bash /sdcard/djinn-termux-bootstrap.sh"
echo ""
echo -e "${BLUE}Vault path on tablet:${NC} /storage/emulated/0/Obsidian"
echo -e "${BLUE}Tablet SSH pubkey:${NC}"
cat "${SSH_KEY}.pub"
echo ""

# Write + commit vault report
REPORT="$DJINN/logs/reports/$(date +%Y-%m-%d)_tablet-setup.md"
mkdir -p "$(dirname $REPORT)"
cat > "$REPORT" << REPORT_EOF
---
title: Tablet Setup Report
date: $(date +%Y-%m-%d)
tags: [djinn, tablet, setup, bootstrap]
---

# Tablet Setup Report — $(date +%Y-%m-%d)

## Device
- Model: SM-T738U (Galaxy Tab S7 FE)
- ADB: 192.168.1.45:5555
- Vault path: /storage/emulated/0/Obsidian

## Status
Salomon-side setup complete. Bootstrap script pushed to tablet.

## Keys
- Private: $SSH_KEY
- Public:  ${SSH_KEY}.pub
- Added to: Salomon, Typhon (if reachable), Orion (if reachable)

## Next Steps
- [ ] Run bootstrap in Termux: bash /sdcard/djinn-termux-bootstrap.sh
- [ ] Verify SSH: ssh salomon
- [ ] Test AI: djinn-ask 'hello'
- [ ] Open Obsidian → confirm vault at /storage/emulated/0/Obsidian
- [ ] Add tablet static IP to INFRASTRUCTURE.md

*— drmanzo, $(date +%Y-%m-%d)*
REPORT_EOF

if git -C "$VAULT" status --porcelain 2>/dev/null | grep -q .; then
    git -C "$VAULT" add -A
    git -C "$VAULT" commit -m "chore: tablet setup report $(date +%Y-%m-%d)"
    git -C "$VAULT" push
    log "Vault report committed and pushed"
fi

echo -e "${GREEN}${BOLD}Done. Run the bootstrap script on the tablet to finish.${NC}"
