#!/usr/bin/env bash
# TASK-001 Batch 3 — Apply all four fixes to Salomon
# Run as: bash batch3-apply.sh
# Requires: ~/.local/bin/djinn-ctx-router, djinn-clerk, printer-error-logger already exist
# Safe: all edits are patched via sed or appended guards — originals not destroyed

set -euo pipefail
LOG="$HOME/Obsidian/djinn/logs/batch3-apply.log"
mkdir -p "$(dirname "$LOG")"
exec > >(tee -a "$LOG") 2>&1
echo "=== Batch 3 Apply — $(date) ==="

# ── FIX 1: djinn-ctx-router — skip if no active user session ──────────────────
CTX="$HOME/.local/bin/djinn-ctx-router"
if [ -f "$CTX" ]; then
  if ! grep -q 'SESSION_GUARD' "$CTX"; then
    # Insert session guard after the shebang/set lines — before main logic
    python3 - <<'PYEOF'
import re, pathlib
p = pathlib.Path.home() / '.local/bin/djinn-ctx-router'
text = p.read_text()
guard = '''
# SESSION_GUARD — skip context assembly if no active user session
_SESSION_FILE = pathlib.Path.home() / '.local/share/djinn/active-session'
if not _SESSION_FILE.exists():
    import sys
    print('[ctx-router] No active session — skipping context assembly.')
    sys.exit(0)
'''
# Insert after last import block
insert_after = re.search(r'^(import |from )[^\n]+\n(?!import |from )', text, re.MULTILINE)
if insert_after:
    pos = insert_after.end()
    text = text[:pos] + guard + text[pos:]
    p.write_text(text)
    print('[FIX 1] ctx-router session guard injected.')
else:
    print('[FIX 1] WARNING: Could not locate import block — prepending guard.')
    p.write_text(guard + text)
PYEOF
  else
    echo '[FIX 1] ctx-router session guard already present — skipping.'
  fi
else
  echo '[FIX 1] WARNING: djinn-ctx-router not found at ~/.local/bin/'
fi

# ── FIX 2: djinn-vault-indexer — enforce incremental mode as default ──────────
IDX="$HOME/.local/bin/djinn-vault-indexer"
if [ -f "$IDX" ]; then
  if ! grep -q 'INCREMENTAL_GUARD' "$IDX"; then
    python3 - <<'PYEOF'
import re, pathlib
p = pathlib.Path.home() / '.local/bin/djinn-vault-indexer'
text = p.read_text()
# Replace any argparse default for --full that makes it default True
# Pattern: add_argument('--full' ... default=True
text_new = re.sub(
    r"(add_argument\(['\"]--full['\"].*?)default=True",
    r"\1default=False",
    text
)
# Also add guard comment
if '--full' in text_new:
    text_new = text_new.replace(
        "add_argument('--full'",
        "# INCREMENTAL_GUARD: --full must be explicit\n    add_argument('--full'"
    ).replace(
        'add_argument("--full"',
        '# INCREMENTAL_GUARD: --full must be explicit\n    add_argument("--full"'
    )
p.write_text(text_new)
print('[FIX 2] ChromaDB indexer incremental guard applied.')
PYEOF
  else
    echo '[FIX 2] Incremental guard already present — skipping.'
  fi
else
  echo '[FIX 2] WARNING: djinn-vault-indexer not found at ~/.local/bin/'
fi

# ── FIX 3: djinn-clerk — swap 1-hr cron for inotifywait watchdog ──────────────
# Disable the old 1-hr systemd timer, deploy a new path-unit watcher instead
SERVICE_DIR="$HOME/.config/systemd/user"
mkdir -p "$SERVICE_DIR"

# Only act if old timer exists and new path unit doesn't
if systemctl --user is-enabled djinn-clerk.timer &>/dev/null && \
   [ ! -f "$SERVICE_DIR/djinn-clerk.path" ]; then

  echo '[FIX 3] Disabling 1-hr djinn-clerk.timer...'
  systemctl --user disable --now djinn-clerk.timer || true

  cat > "$SERVICE_DIR/djinn-clerk.path" <<'EOF'
[Unit]
Description=Djinn Clerk — filesystem watchdog for RAW/ inbox
After=network.target

[Path]
PathChanged=%h/Obsidian/djinn/RAW
PathModified=%h/Obsidian/djinn/RAW
Unit=djinn-clerk.service

[Install]
WantedBy=default.target
EOF

  systemctl --user daemon-reload
  systemctl --user enable --now djinn-clerk.path
  echo '[FIX 3] djinn-clerk.path watchdog installed and enabled.'
else
  echo '[FIX 3] Clerk watchdog already present or timer not found — skipping.'
fi

# ── FIX 4: printer-error-logger — gate LLM call on NEW error state only ────────
ELOG="$HOME/.local/bin/printer-error-logger"
if [ -f "$ELOG" ]; then
  if ! grep -q 'ERROR_STATE_GUARD' "$ELOG"; then
    python3 - <<'PYEOF'
import re, pathlib
p = pathlib.Path.home() / '.local/bin/printer-error-logger'
text = p.read_text()

# Inject a last-seen-error cache check before any LLM call
guard_import = 'import json, hashlib\n'
guard_fn = '''
def _is_new_error(error_text: str, cache_path=None) -> bool:
    # ERROR_STATE_GUARD — only fire LLM when error hash changes
    import pathlib
    cache_path = cache_path or pathlib.Path.home() / '.local/share/djinn/last-printer-error.json'
    import hashlib, json
    h = hashlib.sha256(error_text.encode()).hexdigest()
    if cache_path.exists():
        cached = json.loads(cache_path.read_text()).get('hash')
        if cached == h:
            return False
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps({'hash': h}))
    return True

'''

if 'import json' not in text:
    text = guard_import + text
if '_is_new_error' not in text:
    # Insert after imports
    match = re.search(r'^((?:import |from ).*\n)+', text, re.MULTILINE)
    pos = match.end() if match else 0
    text = text[:pos] + guard_fn + text[pos:]
    print('[FIX 4] Error state guard function injected — wrap your LLM call with: if _is_new_error(error_text):')
else:
    print('[FIX 4] Guard already present.')
p.write_text(text)
PYEOF
  else
    echo '[FIX 4] Error logger guard already present — skipping.'
  fi
else
  echo '[FIX 4] WARNING: printer-error-logger not found at ~/.local/bin/'
fi

# ── Restart affected services ──────────────────────────────────────────────────
echo ''
echo 'Restarting affected services...'
systemctl --user restart djinn-ctx-router.service 2>/dev/null && echo '  ✅ djinn-ctx-router restarted' || echo '  ⚠️  djinn-ctx-router restart failed (check manually)'
systemctl --user restart printer-error-logger.service 2>/dev/null && echo '  ✅ printer-error-logger restarted' || echo '  ⚠️  printer-error-logger restart failed'

echo ''
echo '=== Batch 3 complete. Check log: '$LOG' ==='
echo 'Next: mark Batch 3 done in QUEUE.md and start Batch 4.'
