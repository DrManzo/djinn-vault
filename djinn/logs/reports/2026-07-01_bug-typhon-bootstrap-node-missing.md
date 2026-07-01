---
title: Bug Report — bootstrap-node.sh referenced but does not exist
agent: Claude
date: 2026-07-01
severity: medium
status: open
tags: [djinn, bug, typhon, onboarding]
---

# Bug Report — bootstrap-node.sh referenced but does not exist

**Date:** 2026-07-01
**Agent:** Claude
**System:** Typhon Windows onboarding
**Severity:** medium
**Status:** open

---

## Symptom

`djinn/workspaces/typhon-windows/setup-typhon.ps1` (post-setup instructions, printed at end of script)
tells the operator to run, inside WSL2 Ubuntu after reboot:

```
curl -sS https://raw.githubusercontent.com/DrManzo/djinn-vault/main/djinn/scripts/bootstrap-node.sh | bash
```

This file does not exist — not in the working vault, not anywhere in git history
(`git log --all` on the vault repo has no commit ever touching this path).

---

## Steps to Reproduce

1. Run `setup-typhon.ps1` as Administrator on a fresh Windows box, reboot as instructed.
2. Open WSL2 Ubuntu, run the curl command from the script's printed instructions.
3. Observed: 404 — the file was never created.
4. Expected: a WSL2/Windows-appropriate bootstrap script (Ollama, Claude Code, vault clone,
   `~/.local/bin/djinn-*` scripts) equivalent to `djinn/migration/bootstrap.sh`, which targets
   native Ubuntu and was written for Salomon/old-Typhon, not WSL2.

---

## Root Cause

The ps1 script (committed 2026-06-25, "typhon: rewrite setup script as dedicated shop machine")
was written referencing a bootstrap script path that was never actually created. `migration/bootstrap.sh`
exists and does something similar but assumes it's running on bare Ubuntu with `apt`/`systemctl`,
not inside WSL2 under Windows — it can't be used as-is.

---

## Fix

Not yet fixed — blocks the WSL2-side half of Typhon onboarding. Options:
1. Write `djinn/scripts/bootstrap-node.sh` as a WSL2-aware adaptation of `migration/bootstrap.sh`
   (same package list, but skip anything the ps1 script already handles on the Windows side —
   e.g. Tailscale, OrcaSlicer, firewall — and account for WSL2 not having systemd by default
   unless `[boot] systemd=true` is set in `/etc/wsl.conf`).
2. Or drop the WSL2 dependency entirely and run the Linux-side Djinn stack natively on Windows
   (Ollama has a native Windows build; Claude Code needs WSL/Git-Bash or a native port).

No decision made yet — needs Javier's input on which approach fits the shop-machine role.

---

## Prevention

When a setup script is committed that references a URL/path not yet created, either create
the referenced file in the same commit or leave a `# TODO: not yet written` comment inline
instead of a live curl command — a dangling reference like this fails silently for whoever
runs the script next, with no error until the exact moment it's needed.

---

*— Claude, 2026-07-01*
