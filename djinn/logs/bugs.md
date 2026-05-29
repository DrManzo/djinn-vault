---
subject: Djinn Bug Log
tags: [djinn, bugs]
created: 2026-05-28
---

# Bug Log

Running index of all bugs discovered across Djinn systems. Each entry links to a full bug report.

| Date | Agent | System | Severity | Status | Summary | Report |
|------|-------|--------|----------|--------|---------|--------|
| 2026-05-28 | Claude | Typhon Studio / Vue 3 frontend | medium | fixed | `_tsToTime` prefixed with `_` — Vue 3 drops `_`-prefixed properties from template proxy; caused silent ReferenceError → browser reload loop | [[2026-05-28_typhons-studio-guardian-final]] |
| 2026-05-28 | Claude | Typhon Studio / copilot_agent.py | high | fixed | SyntaxError on line 109 — bad `sed` replacement broke f-string in `log.warning()` line; service failed to import | [[2026-05-28_typhons-studio-phase5]] |

---

*Auto-updated by `djinn-bugreport`. Full reports in `reports/`.*
| 2026-05-28 | Claude | djinn-discord-watcher | high | fixed | openclaw not in systemd PATH — Discord sends fail | [[2026-05-28_bug-openclaw-not-in-systemd-path-discord-sends-fail]] |
