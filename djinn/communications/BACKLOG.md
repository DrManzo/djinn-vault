---
title: Djinn Backlog — Future Work
updated: 2026-06-15
tags: [djinn, backlog, someday]
---

# BACKLOG — Pull up when the queue is empty

Low-urgency items deferred from active sessions. Nothing here is broken. Nothing here blocks anything. Pick one when you have time and move it to QUEUE.md to activate it.

---

## Hellhound gateway wiring (TASK-074)
**What:** Wire Hellhound observations into the three gateways so it actually sees live traffic.
**Scope:**
1. `hh_observe()` calls in djinn-discord-gateway — order received, command routed, customer message
2. `hh_observe()` calls in djinn-telegram-gateway — confirm/deny, operator commands
3. `hh_observe()` calls in djinn-webcam-monitor — print start, milestone, failure, complete
4. Daily/on-demand report generator → Telegram summary
5. Replace StubGateway in pup-gateway.py with real observer

**Note:** Gateway pup does NOT replace djinn-discord-gateway — observe-only. Hellhound daemon and all modules are already deployed and running. This is purely the wiring layer.
**To activate:** Move to QUEUE.md, assign to claude, status: pending.

---

## Live order pipeline test
**What:** Drop a real STL in #3d-printing and run the full pipeline end to end.
**Why deferred:** Nothing to build — Javier has to do it. Just needs a moment when you have a file and want to test.
**What happens:** Buttons appear → pick profile/color → djinn-model-fetch processes → overhang map → auto-slice → confirm N → Calliope prints → webcam milestone clips fire.

---

## Orion Tailscale cleanup
**What:** Remove Tailscale from Orion (iMac) — it was only there for the tablet, which can reach Orion via Salomon's subnet route instead.
**Why deferred:** Orion is not Javier's machine — needs to coordinate with the owner.
**To do:** Ask whoever owns the iMac to run `sudo tailscale down` or remove Tailscale.

---

<!-- Add new items above this line — newest at bottom -->
