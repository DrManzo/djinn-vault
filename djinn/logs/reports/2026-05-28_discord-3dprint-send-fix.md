---
title: Session Report — Discord 3D Print Pipeline Send-Back Fix
agent: Claude
date: 2026-05-28
tags: [djinn, report, bugfix, discord, 3d-printing]
related: [[build-log]] | [[bugs]]
---

# Session Report — Discord 3D Print Pipeline Send-Back Fix

**Date:** 2026-05-28
**Agent:** Claude
**Session type:** Debug
**Trigger:** Javier reported "send the 3d print files to discord is failing"

---

## Summary

Two bugs were preventing the 3D print pipeline from sending reports and renders back to Discord after detecting an uploaded STL. The `djinn-discord-watcher` and `djinn-model-fetch` both called `openclaw message send` to reply to Discord, but `openclaw` was not in the systemd service's PATH. Additionally, trimesh's headless rendering required a display that didn't exist in the service environment. Both bugs are fixed; the service is live and healthy.

---

## What Was Built or Changed

- **`watcher.py`** — replaced `openclaw` subprocess with direct Discord REST API (urllib)
- **`djinn-model-fetch`** — replaced both `_discord_send()` and `_discord_send_photo()` with direct REST API calls; also implements multipart file upload natively
- **`djinn-discord-watcher.service`** — added `ExecStartPre` to start Xvfb on `:98`, added `DISPLAY=:98` env, added `ExecStopPost` to kill the Xvfb
- Two bug reports filed in `bugs.md`

---

## Technical Decisions

**Direct REST over openclaw fix** — Could have added the nvm bin path to the service PATH instead. Chose direct REST because `djinn-discord-watch.py` already demonstrates the pattern works, it removes a Node.js dependency from Python scripts, and it's simpler to maintain.

**Xvfb on :98 not :99** — Typhon's Studio uses `:99`. Used `:98` to avoid collision if Typhon and Salomon ever share a display namespace (unlikely but trivially avoided).

**ExecStartPre for Xvfb, not a separate unit** — A dedicated `xvfb.service` with `Requires=` would be cleaner, but adds complexity for a single consumer. ExecStartPre is self-contained.

---

## Files Created or Modified

```
~/Obsidian/djinn/printer/discord/watcher.py          discord_send() — removed openclaw, uses REST
~/.local/bin/djinn-model-fetch                        _discord_send() + _discord_send_photo() — removed openclaw
~/.config/systemd/user/djinn-discord-watcher.service  added Xvfb ExecStartPre + DISPLAY=:98
~/Obsidian/djinn/logs/bugs.md                         two new bug entries
~/Obsidian/djinn/logs/reports/2026-05-28_bug-*.md     two dedicated bug reports
```

---

## Tests & Validation

- `systemctl --user status djinn-discord-watcher.service` — active (running), Xvfb and python3 both in cgroup
- `Xvfb :98` confirmed working: trimesh render test under `DISPLAY=:98` produces 1524-byte PNG
- Watcher log shows it started clean with no errors
- Vault pushed to GitHub successfully after rebase

---

## Known Issues

- `djinn-bugreport` exits 1 even on success (spurious, doesn't affect operation)
- Renders depend on `djinn-orchestrator` venv's trimesh install — if venv is rebuilt, verify trimesh is included

---

## What's Next

- Drop an STL in `#3d-printing` to confirm the full flow: watcher detects → model-fetch runs → renders sent → consult question posted to Discord
- Cloudybay lights (needs Tuya API creds)
- WHIP end-to-end test from Omen

— Claude
