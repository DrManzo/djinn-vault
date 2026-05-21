#!/usr/bin/env bash
# djinn-typhon-claude-setup.sh
# Run on Salomon to provision Claude Code on Typhon with Salomon's OAuth credentials.
# Typhon does NOT need a browser login — credentials are transferred over SSH.
#
# Usage: bash ~/djinn-typhon-claude-setup.sh
#        Optionally: TYPHON_USER=someuser bash ~/djinn-typhon-claude-setup.sh

set -euo pipefail

TYPHON_IP="192.168.50.113"
TYPHON_USER="${TYPHON_USER:-drmanzo}"
TYPHON="${TYPHON_USER}@${TYPHON_IP}"
CREDS_SRC="$HOME/.claude/.credentials.json"

echo "=== Djinn: Typhon Claude Code Setup ==="
echo "Target: $TYPHON"

# Verify Typhon is reachable
if ! ssh -o ConnectTimeout=8 "$TYPHON" "echo ok" &>/dev/null; then
  echo "ERROR: Cannot reach $TYPHON — is Typhon online?"
  exit 1
fi
echo "[1/4] Typhon reachable."

# Install Claude Code on Typhon if not present
if ! ssh "$TYPHON" "command -v claude" &>/dev/null; then
  echo "[2/4] Installing Claude Code on Typhon..."
  ssh "$TYPHON" "curl -fsSL https://claude.ai/install.sh | bash"
else
  echo "[2/4] Claude Code already installed on Typhon."
fi

# Transfer credentials — shared OAuth session (same Pro account, same user)
echo "[3/4] Transferring credentials..."
ssh "$TYPHON" "mkdir -p ~/.claude"
scp "$CREDS_SRC" "${TYPHON}:~/.claude/.credentials.json"
ssh "$TYPHON" "chmod 600 ~/.claude/.credentials.json"

# Verify
echo "[4/4] Verifying..."
if ssh "$TYPHON" 'claude -p "ping" 2>&1 | grep -qi "error\|not logged\|unauthorized"'; then
  echo "WARNING: Claude Code responded with an error — may need manual 'claude /login' on Typhon."
else
  echo "Claude Code on Typhon: OK"
fi

echo ""
echo "=== Setup complete ==="
echo "Typhon can now run 'claude' natively."
echo ""
echo "To verify on Typhon:"
echo "  ssh $TYPHON 'claude -p \"hello\" 2>&1 | head -3'"
echo ""
echo "The handoff doc (JOB 4 Step 6) described deauthing Typhon after setup."
echo "Since you want permanent access, skip that step — leave credentials in place."
echo "Refresh happens automatically; no maintenance needed."
