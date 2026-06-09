#!/usr/bin/env bash
# TASK-001 Batch 3 — Verify all four fixes are live
# Run after batch3-apply.sh

set -euo pipefail
PASS=0; FAIL=0

check() {
  local label="$1" result="$2"
  if [ "$result" = 'pass' ]; then
    echo "  ✅ $label"
    ((PASS++))
  else
    echo "  ❌ $label"
    ((FAIL++))
  fi
}

echo "=== Batch 3 Verify — $(date) ==="

# Fix 1 — ctx-router session guard
if grep -q 'SESSION_GUARD' ~/.local/bin/djinn-ctx-router 2>/dev/null; then
  check 'ctx-router session guard' pass
else
  check 'ctx-router session guard' fail
fi

# Fix 2 — chromadb incremental default
if grep -q 'INCREMENTAL_GUARD' ~/.local/bin/djinn-vault-indexer 2>/dev/null; then
  check 'chromadb incremental guard' pass
else
  check 'chromadb incremental guard' fail
fi

# Fix 3 — clerk watchdog path unit
if systemctl --user is-enabled djinn-clerk.path &>/dev/null; then
  check 'djinn-clerk.path watchdog enabled' pass
else
  check 'djinn-clerk.path watchdog enabled' fail
fi
if ! systemctl --user is-enabled djinn-clerk.timer &>/dev/null; then
  check 'djinn-clerk.timer disabled' pass
else
  check 'djinn-clerk.timer still enabled (should be off)' fail
fi

# Fix 4 — printer error state guard
if grep -q 'ERROR_STATE_GUARD' ~/.local/bin/printer-error-logger 2>/dev/null; then
  check 'printer-error-logger state guard' pass
else
  check 'printer-error-logger state guard' fail
fi

echo ''
echo "Results: $PASS passed, $FAIL failed"
[ $FAIL -eq 0 ] && echo 'Batch 3 VERIFIED ✅' || echo 'Batch 3 needs attention ❌'
