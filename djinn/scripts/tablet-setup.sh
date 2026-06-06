#!/usr/bin/env bash
# =============================================================================
# tablet-setup.sh — Djinn Tablet Bootstrap
# Run from: Salomon (drmanzo@192.168.1.225)
# Target:   Samsung Galaxy Tab S (R52T10BL3BV)
# Purpose:  Configure the Tablet as a full Djinn development node
#           — vault sync, SSH keys, dev tooling, Termux bootstrap
# =============================================================================
# Usage:
#   chmod +x tablet-setup.sh
#   ./tablet-setup.sh
#
# Requirements on Salomon:
#   - adb (Android Debug Bridge)   → sudo apt install adb
#   - Android USB Debugging ON     → Settings > Developer Options > USB Debugging
#   - Tablet connected via USB
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
TABLET_SERIAL="R52T10BL3BV"
SALOMON_IP="192.168.1.225"
OLLAMA_PORT="11434"
OPENCLAW_PORT="18789"
SSH_KEY="$HOME/.ssh/tablet_ed25519"  # Key we generate FOR the tablet
REPO_URL="https://github.com/DrManzo/djinn-vault.git"

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
    err "No tablet detected. Enable USB Debugging and reconnect."
fi

# Check Termux is installed
if ! adb shell pm list packages 2>/dev/null | grep -q 'com.termux'; then
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
# STEP 3 — Push SSH Keys into Termux
# =============================================================================
info "Step 3: Pushing SSH keys into Termux..."

# Create .ssh dir in Termux
adb shell run-as com.termux mkdir -p "$TERMUX_SSH" 2>/dev/null || \
adb shell "su -c 'mkdir -p $TERMUX_SSH'" 2>/dev/null || \
adb shell am startservice --user 0 -n com.termux/.app.TermuxService 2>/dev/null || true

# Push private key
adb push "$SSH_KEY" "/sdcard/tablet_ed25519"
adb shell run-as com.termux cp /sdcard/tablet_ed25519 "$TERMUX_SSH/id_ed25519" 2>/dev/null || \
    warn "Could not copy key into Termux automatically — do it manually in Termux:"
    warn "  cp /sdcard/tablet_ed25519 ~/.ssh/id_ed25519 && chmod 600 ~/.ssh/id_ed25519"

# Push public key
adb push "${SSH_KEY}.pub" "/sdcard/tablet_ed25519.pub"

log "SSH keys pushed to /sdcard/ — complete setup in Termux (Step 9)"

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

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║     DJINN TERMUX BOOTSTRAP — Tablet Node         ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

# ── Package setup ────────────────────────────────────────
info "Updating Termux packages..."
pkg update -y && pkg upgrade -y

info "Installing core packages..."
pkg install -y \
    openssh \
    git \
    curl \
    wget \
    python \
    nodejs \
    jq \
    vim \
    nano \
    tmux \
    htop \
    tree \
    zip \
    unzip \
    rsync \
    nmap \
    netcat-openbsd \
    termux-api
log "Core packages installed"

# ── Storage access ───────────────────────────────────────
info "Requesting storage access..."
termux-setup-storage
log "Storage setup initiated — approve the permission popup"

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
log "Git configured"

# ── Clone djinn-vault ─────────────────────────────────────
info "Cloning djinn-vault..."
VAULT_DIR="$HOME/djinn-vault"
if [[ -d "$VAULT_DIR" ]]; then
    warn "djinn-vault already exists — pulling latest"
    git -C "$VAULT_DIR" pull
else
    git clone "$VAULT_REPO" "$VAULT_DIR"
    log "djinn-vault cloned to $VAULT_DIR"
fi

# ── Symlink vault for Obsidian ────────────────────────────
info "Linking vault to shared storage for Obsidian..."
mkdir -p ~/storage/shared
if [[ ! -L ~/storage/shared/djinn-vault ]]; then
    ln -s "$VAULT_DIR" ~/storage/shared/djinn-vault
    log "Symlink: ~/storage/shared/djinn-vault → $VAULT_DIR"
else
    warn "Symlink already exists"
fi

# ── Djinn CLI aliases ─────────────────────────────────────
info "Writing djinn shell aliases..."
cat >> ~/.bashrc << 'ALIASES'

# ── Djinn Fleet ─────────────────────────────────────────
export SALOMON="192.168.1.225"
export TYPHON="192.168.1.113"
export ORION="192.168.1.176"
export VAULT="$HOME/djinn-vault"

alias djinn-ssh-salomon='ssh salomon'
alias djinn-ssh-typhon='ssh typhon'
alias djinn-ssh-orion='ssh orion'
alias vault-pull='git -C $VAULT pull'
alias vault-log='git -C $VAULT log --oneline -20'

# Ollama API shortcuts (route to fleet)
djinn-ask() {
    local model="${2:-qwen2.5:7b}"
    local host="${3:-$SALOMON}"
    curl -s "http://$host:11434/api/generate" \
        -d "{\"model\":\"$model\",\"prompt\":\"$1\",\"stream\":false}" \
        | python -c "import sys,json; print(json.load(sys.stdin)['response'])"
}

djinn-ask-orion() {
    djinn-ask "$1" "llama3.3:70b" "$ORION"
}

# Push a note to vault inbox via SSH
djinn-note() {
    local note="$1"
    local date=$(date +%Y-%m-%d)
    echo "$note" | ssh salomon "cat >> ~/Obsidian/djinn/inbox/${date}-tablet.md"
    echo "Note sent to vault inbox"
}

# Quick fleet status
djinn-status() {
    echo "--- Fleet Ping ---"
    for host in salomon typhon orion; do
        if ping -c1 -W1 $host &>/dev/null 2>&1; then
            echo "  ✓ $host online"
        else
            echo "  ✗ $host offline"
        fi
    done
}
ALIASES
log "Shell aliases written to ~/.bashrc"

# ── Python dev setup ─────────────────────────────────────
info "Installing Python dev tools..."
pip install --upgrade pip
pip install \
    requests \
    httpx \
    ollama \
    openai \
    rich \
    typer \
    pydantic \
    python-dotenv
log "Python packages installed"

# ── Node/npm tools ────────────────────────────────────────
info "Installing Node tools..."
npm install -g \
    prettier \
    typescript \
    ts-node
log "Node tools installed"

# ── Vault sync cron (optional) ───────────────────────────
info "Setting up vault sync..."
# Termux doesn't have cron by default — use Termux:Boot for auto-start
pkg install -y termux-services 2>/dev/null || true
mkdir -p ~/.termux/boot
cat > ~/.termux/boot/vault-sync.sh << 'BOOT'
#!/data/data/com.termux/files/usr/bin/bash
# Auto-pull vault on Termux boot
while true; do
    git -C "$HOME/djinn-vault" pull --ff-only 2>/dev/null
    sleep 300  # every 5 minutes
done &
BOOT
chmod +x ~/.termux/boot/vault-sync.sh
log "Vault sync boot script written"

# ── SSH connection tests ──────────────────────────────────
info "Testing SSH connections to fleet..."
for entry in "salomon $SALOMON_IP" "typhon $TYPHON_IP" "orion $ORION_IP"; do
    name=$(echo $entry | cut -d' ' -f1)
    ip=$(echo $entry | cut -d' ' -f2)
    if ssh -o ConnectTimeout=5 -o BatchMode=yes $name 'echo ok' &>/dev/null; then
        log "SSH → $name ($ip): OK"
    else
        warn "SSH → $name ($ip): FAILED (may need to add key to authorized_keys)"
    fi
done

# ── Ollama API test ───────────────────────────────────────
info "Testing Ollama API on Salomon..."
if curl -s --connect-timeout 5 "http://$SALOMON_IP:11434/api/tags" | python -c "import sys,json; models=json.load(sys.stdin)['models']; [print(' ',m['name']) for m in models]" 2>/dev/null; then
    log "Ollama API on Salomon: reachable"
else
    warn "Ollama API on Salomon: not reachable (check WiFi / Salomon status)"
fi

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║         TABLET BOOTSTRAP COMPLETE                ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "  1. source ~/.bashrc"
echo "  2. Open Obsidian → point vault to /sdcard/djinn-vault/"
echo "  3. Test: ssh salomon"
echo "  4. Test: djinn-status"
echo "  5. Test: djinn-ask 'Hello from tablet'"
echo ""
echo "  Vault:      ~/djinn-vault/"
echo "  Key files:  ~/djinn-vault/djinn/AGENTS.md"
echo "              ~/djinn-vault/djinn/TABLET.md"
echo "              ~/djinn-vault/djinn/INFRASTRUCTURE.md"
echo ""
TERMUX_EOF

log "Termux bootstrap script built"

# =============================================================================
# STEP 5 — Push Bootstrap Script to Tablet via ADB
# =============================================================================
info "Step 5: Pushing bootstrap script to tablet..."

adb push "$TERMUX_BOOTSTRAP" "/sdcard/djinn-termux-bootstrap.sh"
log "Bootstrap script pushed to /sdcard/djinn-termux-bootstrap.sh"

# =============================================================================
# STEP 6 — Push Critical Vault Files to Tablet SD Card
# =============================================================================
info "Step 6: Pushing critical vault docs to /sdcard/djinn-docs/..."

adb shell mkdir -p /sdcard/djinn-docs/

# Core Djinn docs the tablet needs to read immediately
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
        adb push "$f" "/sdcard/djinn-docs/"
        log "Pushed: $(basename $f)"
    else
        warn "Missing: $f — skipping"
    fi
done

# =============================================================================
# STEP 7 — Write Obsidian Vault Config Hint
# =============================================================================
info "Step 7: Writing Obsidian setup hint..."

OBSIDIAN_HINT="/tmp/OBSIDIAN-SETUP.md"
cat > "$OBSIDIAN_HINT" << 'OBS_EOF'
# Obsidian Mobile Setup — Djinn Vault

## Vault Location
After running the Termux bootstrap:
- Vault cloned to: `~/djinn-vault/` (Termux home)
- Symlinked to:    `/sdcard/djinn-vault/` (visible to Obsidian)

## Steps
1. Open Obsidian Mobile
2. Tap "Open folder as vault"
3. Navigate to: Internal Storage > djinn-vault
4. Select the `djinn/` subfolder as the vault root
5. Obsidian will index all notes automatically

## Sync
- Vault syncs via `vault-pull` alias in Termux (runs git pull)
- Auto-sync every 5 min via boot script (requires Termux:Boot)
- To push a change: `git -C ~/djinn-vault add -A && git commit -m "..." && git push`
  (GitHub auth required — run `git config credential.helper store` first)

## Key Files to Bookmark in Obsidian
- djinn/AGENTS.md         — Fleet rules + lane assignments
- djinn/TABLET.md         — This device's full spec and role
- djinn/INFRASTRUCTURE.md — Full fleet topology
- djinn/SYSTEM-STATE.md   — Live services and machine status
- djinn/ROUTING.md        — Model routing rules
OBS_EOF

adb push "$OBSIDIAN_HINT" "/sdcard/djinn-docs/OBSIDIAN-SETUP.md"
log "Obsidian setup guide pushed"

# =============================================================================
# STEP 8 — Final Instructions
# =============================================================================
echo ""
echo -e "${BOLD}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║           SALOMON-SIDE SETUP COMPLETE                     ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Files pushed to tablet /sdcard/:${NC}"
echo "  /sdcard/djinn-termux-bootstrap.sh  ← run this in Termux"
echo "  /sdcard/tablet_ed25519             ← private SSH key"
echo "  /sdcard/tablet_ed25519.pub         ← public SSH key"
echo "  /sdcard/djinn-docs/*.md            ← critical vault docs"
echo ""
echo -e "${YELLOW}NOW DO THIS ON THE TABLET:${NC}"
echo ""
echo "  1. Open Termux"
echo "  2. Run:"
echo ""
echo "       bash /sdcard/djinn-termux-bootstrap.sh"
echo ""
echo "  3. When prompted — approve storage permission"
echo "  4. After bootstrap finishes:"
echo "       source ~/.bashrc"
echo "       ssh salomon          ← should connect to Salomon"
echo "       djinn-status         ← should ping all fleet nodes"
echo "       djinn-ask 'test'     ← should get Ollama response from Salomon"
echo ""
echo -e "${YELLOW}OBSIDIAN:${NC}"
echo "  Open Obsidian → vault → /sdcard/djinn-vault/"
echo "  Read /sdcard/djinn-docs/OBSIDIAN-SETUP.md for full steps"
echo ""
echo -e "${GREEN}Tablet SSH public key (add anywhere needed):${NC}"
cat "${SSH_KEY}.pub"
echo ""

# Log to vault
REPORT="$DJINN/logs/reports/$(date +%Y-%m-%d)_tablet-setup.md"
mkdir -p "$(dirname $REPORT)"
cat > "$REPORT" << REPORT_EOF
---
title: Tablet Setup Report
date: $(date +%Y-%m-%d)
tags: [djinn, tablet, setup, bootstrap]
---

# Tablet Setup Report — $(date +%Y-%m-%d)

## Status
Salomon-side setup complete. Bootstrap script pushed to tablet.

## Keys Generated
- Private key: $SSH_KEY
- Public key: ${SSH_KEY}.pub
- Added to: Salomon authorized_keys

## Files Pushed
- /sdcard/djinn-termux-bootstrap.sh
- /sdcard/tablet_ed25519 (private key)
- /sdcard/tablet_ed25519.pub
- /sdcard/djinn-docs/ ($(ls $DJINN/*.md $DJINN/machines/TABLET.md 2>/dev/null | wc -l) files)

## Next Steps
- [ ] Run bootstrap in Termux
- [ ] Verify SSH to Salomon/Typhon/Orion
- [ ] Configure Obsidian Mobile vault
- [ ] Add tablet IP to INFRASTRUCTURE.md
- [ ] Set up Tasker webhooks (optional)

*— Marcus, $(date +%Y-%m-%d)*
REPORT_EOF

log "Report written: $REPORT"

# Commit report
if git -C "$VAULT" status --porcelain 2>/dev/null | grep -q .; then
    git -C "$VAULT" add -A
    git -C "$VAULT" commit -m "chore: tablet setup report $(date +%Y-%m-%d)"
    git -C "$VAULT" push
    log "Vault committed and pushed"
fi

echo -e "${GREEN}${BOLD}Done. Tablet setup initiated from Salomon.${NC}"
