#!/bin/bash
# typhon-bootstrap.sh — Phase 0/1 runtime setup for new-Typhon (Ubuntu 26.04.1 Server)
#
# Installs the exact runtime stack the migrated Djinn command-center services
# expect, matching what's actually running on Salomon (checked live 2026-09-10,
# not assumed):
#   - pyenv 2.6.31 + Python 3.11.11 (used directly by hellhound, via shims by
#     djinn-shop-dashboard/djinn-dm-cleanup and most other djinn-* scripts)
#   - nvm v0.40.4 + Node v22.22.3 (openclaw-gateway)
#   - Docker CE via Docker's official apt repo — NOT Ubuntu's docker.io package,
#     Salomon uses docker-ce/docker-ce-cli/containerd.io/docker-ce-rootless-extras
#   - rclone via Ubuntu's own repo (gdrive-sync, vault-sync)
#
# Deliberately does NOT install Ollama — that's an open decision (see
# djinn/machines/salomon-typhon-role-swap-migration.md, "Ollama / local LLM
# serving") not yet resolved as of this script's writing.
#
# Idempotent — safe to re-run if a step fails partway through.
#
# — Claude, 2026-09-10

set -euo pipefail

echo "=== typhon-bootstrap: starting $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="

# ── apt base ──────────────────────────────────────────────────────────────────
echo "--- apt update + base packages ---"
sudo apt-get update -y
sudo apt-get install -y \
    git curl wget build-essential \
    libssl-dev libbz2-dev libreadline-dev libsqlite3-dev libffi-dev liblzma-dev zlib1g-dev \
    ca-certificates gnupg \
    rclone

# ── pyenv + Python 3.11.11 ──────────────────────────────────────────────────
echo "--- pyenv ---"
if [ ! -d "$HOME/.pyenv" ]; then
    git clone --branch v2.6.31 --depth 1 https://github.com/pyenv/pyenv.git "$HOME/.pyenv"
else
    echo "pyenv already present, skipping clone"
fi

export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"

if ! grep -q 'PYENV_ROOT' "$HOME/.bashrc" 2>/dev/null; then
    {
        echo ''
        echo '# pyenv'
        echo 'export PYENV_ROOT="$HOME/.pyenv"'
        echo 'export PATH="$PYENV_ROOT/bin:$PATH"'
        echo 'eval "$(pyenv init -)"'
    } >> "$HOME/.bashrc"
fi

if ! pyenv versions --bare | grep -q "^3.11.11$"; then
    pyenv install 3.11.11
else
    echo "Python 3.11.11 already installed via pyenv, skipping"
fi
pyenv global 3.11.11

# ── nvm + Node v22.22.3 ──────────────────────────────────────────────────────
echo "--- nvm ---"
if [ ! -d "$HOME/.nvm" ]; then
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.4/install.sh | bash
else
    echo "nvm already present, skipping install"
fi

export NVM_DIR="$HOME/.nvm"
# shellcheck disable=SC1091
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

if ! nvm ls 22.22.3 >/dev/null 2>&1; then
    nvm install 22.22.3
fi
nvm alias default 22.22.3
nvm use default

# ── Docker CE (official repo, matching Salomon exactly) ────────────────────
echo "--- Docker CE ---"
if ! command -v docker >/dev/null 2>&1; then
    sudo install -m 0755 -d /etc/apt/keyrings
    if [ ! -f /etc/apt/keyrings/docker.asc ]; then
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.asc
        sudo chmod a+r /etc/apt/keyrings/docker.asc
    fi
    ARCH="$(dpkg --print-architecture)"
    CODENAME="$(. /etc/os-release && echo "$VERSION_CODENAME")"
    echo "deb [arch=$ARCH signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $CODENAME stable" | \
        sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update -y
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-ce-rootless-extras
    sudo usermod -aG docker "$USER"
    echo "NOTE: added $USER to docker group — log out/in (or reboot) for this to take effect without sudo"
else
    echo "docker already installed, skipping"
fi

# ── openclaw (pinned to Salomon's actual running version, NOT latest) ──────
echo "--- openclaw ---"
# Salomon runs openclaw@2026.5.22 as of 2026-09-10 — latest on npm is 2026.9.3.
# Installing latest here would silently hand new-Typhon a different, unverified
# version than the one openclaw-gateway.service was actually tuned against.
# Bump this pin deliberately (and re-verify the gateway still behaves) if
# Salomon's own version is intentionally upgraded before cutover.
if ! npm list -g --depth=0 2>/dev/null | grep -q "openclaw@2026.5.22"; then
    npm install -g openclaw@2026.5.22
else
    echo "openclaw@2026.5.22 already installed, skipping"
fi

# ── Summary / verification ──────────────────────────────────────────────────
echo
echo "=== typhon-bootstrap: verification ==="
echo "pyenv:   $(pyenv --version 2>&1)"
echo "python:  $(pyenv exec python3 --version 2>&1)"
echo "node:    $(node --version 2>&1)"
echo "npm:     $(npm --version 2>&1)"
echo "docker:  $(docker --version 2>&1)"
echo "rclone:  $(rclone version 2>&1 | head -1)"
echo "openclaw: $(npm list -g --depth=0 2>/dev/null | grep openclaw || echo 'NOT FOUND')"
echo
echo "=== typhon-bootstrap: done $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
echo "Still needed before the command-center stack can run:"
echo "  - the actual djinn-*/forge-*/studio-* scripts + systemd units (Phase 2)"
echo "  - the 7 credential/secret env files (Phase 2, transfer securely)"
echo "  - Ollama decision still open — not installed by this script"
