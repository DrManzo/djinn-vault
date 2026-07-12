---
title: Session Report — Hellhound Real Rebuild (Outbound Audit + Inbound Probe)
agent: Claude
date: 2026-07-12
tags: [djinn, report, hellhound, security]
related: [[TASK-081_hellhound-proactive-rebuild]] | [[build-log]] | [[decision-log]]
---

# Session Report — Hellhound Real Rebuild (Outbound Audit + Inbound Probe)

**Date:** 2026-07-12
**Agent:** Claude (with Marcus — research/code drafts via Perplexity, GitHub-only access)
**Session type:** Build / Security
**Trigger:** Priority-1 item from the day's vault audit — hellhound had been dark for 27 days. Javier: script-based/deterministic detection, AI only for reporting; Marcus writes code, Claude does 100% of the live-system connection work.

---

## Summary

Hellhound's one existing pup ran a StubGateway that never connected to anything real — confirmed by Marcus's TASK-081 audit and verified live. This session built and deployed the first real gate: SSH + Forge-dashboard brute-force/recon detection with auto-block (ufw) and Telegram alerting, plus an outbound audit path for Javier's own Telegram commands. Along the way, fixed three bugs that would have silently broken the rebuild (a stale vault path in the master daemon, a systemd specifier bug that's been latent since install, and a wrong Telegram credential). Fully live-tested (synthetic test IPs, real Telegram delivery, real ufw block/unblock) before being left running.

---

## What Was Built or Changed

- `hellhound/hellhound.py` — fixed `VAULT_BASE` (was `djinn/hellhound`, now `hellhound`)
- `hellhound/skull/hellhound.service` — matching `ReadWritePaths` fix
- `hellhound/skull/pup@.service` — `%I` → `%i` fix (see bug report); `Type=notify`, `WatchdogSec=30`
- `hellhound/pup.py` — dependency-free `sd_notify()` (manual `$NOTIFY_SOCKET` protocol) + watchdog loop, benefits every current/future pup, not just this one
- `hellhound/pup-inbound-probe.py` (new) — real detection pup: rapid-auth-fail, ssh-new-user-attempt, port-scan-signature, new-source-ip-forge, request-rate-spike. Watches SSH (journalctl) and the Forge dashboard (journalctl, `djinn-shop-dashboard.service`) — explicitly does NOT watch Moonraker, which runs on each printer's own board, not Salomon
- `hellhound/gates/inbound_probe_rules.py`, `inbound_probe_block.py`, `inbound_probe_incident.py` — mostly Marcus's design as delivered, minor fixes (YAML boolean formatting, `sudo -n` for non-interactive safety)
- `hellhound/gates/inbound_probe_notify.py` — rewritten to use the correct credential source (see bugs)
- `hellhound/gates/audit_client.py` — rewritten as a sync client against the real `skull.sock` CONNECT/OBSERVE protocol (Marcus's version invented a separate socket+JSONL system; this reuses hellhound's existing SQLite/timeline infra instead)
- `hellhound/config/trusted-ips.txt` (new) — seeded with Salomon + fleet IPs, human-editable
- `~/.local/bin/djinn-telegram-gateway` (outside vault, live edit) — two `audit_client.record()` call sites (text + voice message paths)
- Deployed to `~/.local/share/hellhound/` (runtime location); `pup@inbound-probe.service` enabled and running
- `ufw` enabled (default-allow policy — Salomon serves the whole fleet's Ollama API and other cross-machine services; auto-block only needs ufw active, not a locked-down default)

---

## Technical Decisions

**Rewrote Marcus's gate-loader/BaseGate pattern to match the real PupClient/skull.sock architecture — why:** Marcus had no shell access and explicitly flagged this uncertainty. The real `pup.py` is an async socket client library (`PupClient`), and `pup-gateway.py` (the actual dead stub) doesn't use the `gates/base.py` ABC at all. Building against Marcus's invented pattern would not have run.

**`audit_client.py` as a sync fire-and-forget client against the real master socket, not Marcus's separate outbound-audit daemon — why:** the master daemon already provides JSONL logging + SQLite indexing + vault timeline entries for every observation. Building a parallel audit-logging system would duplicate infrastructure that already works, for no benefit.

**Incidents write to the vault (`~/Obsidian/hellhound/incidents/`), not the local runtime dir — why:** matches `hellhound.py`'s own existing pattern of keeping meaningful, human-review-worthy output in the git-backed vault (timeline/) while high-frequency raw data (SQLite, JSONL) stays local. Marcus's version wrote incidents locally only.

**`new-source-ip-forge` deduped to once per hour per IP — why:** Marcus's original rule (threshold=1, no window) would fire on literally every request from an unrecognized device, spamming Telegram every few seconds during normal use from a new phone/laptop until the IP is added to the trusted list.

**LAN auto-block refined per Javier's actual threat model (brute-force/WiFi intrusion, not physical) — why:** `rapid-auth-fail`, `ssh-new-user-attempt`, and `port-scan-signature` auto-block on LAN too (nothing legitimately fails SSH auth repeatedly); `new-source-ip-forge` and `request-rate-spike` never auto-block LAN (could be tripped by legitimate fleet/dashboard traffic).

**ufw enabled with default-allow, not default-deny — why:** Salomon serves Ollama API to the whole Djinn fleet plus several other cross-machine services (netdata, prometheus, OctoPrint). Enumerating every port that needs to stay open risked breaking daily automation for other machines. The auto-block feature only requires ufw *active* to enforce specific per-IP deny rules — it doesn't need a restrictive baseline policy.

**Scoped out Moonraker monitoring — why:** Moonraker runs on each printer's own controller board, not on Salomon. Salomon is a client to those APIs, not a server — it has no visibility into traffic hitting them. Real protection there needs an agent on each printer host, a separate future task, not something to fake here.

**Scoped out Discord — why:** confirmed with Javier mid-build that Discord is shop/business-only, not a Djinn control channel. Telegram is the only outbound-audit hook needed.

---

## Files Created or Modified

```
hellhound/hellhound.py                        ← VAULT_BASE path fix
hellhound/pup.py                              ← sd_notify() + watchdog loop (shared library)
hellhound/pup-inbound-probe.py                ← new — real detection pup
hellhound/gates/inbound_probe_rules.py        ← new
hellhound/gates/inbound_probe_block.py        ← new
hellhound/gates/inbound_probe_incident.py     ← new
hellhound/gates/inbound_probe_notify.py       ← new
hellhound/gates/audit_client.py               ← new
hellhound/config/trusted-ips.txt              ← new
hellhound/skull/hellhound.service             ← ReadWritePaths fix
hellhound/skull/pup@.service                  ← %I→%i fix, Type=notify/WatchdogSec
~/.local/bin/djinn-telegram-gateway           ← outbound audit hooks (outside vault)
~/.config/systemd/user/hellhound-inbound-probe.env  ← new (outside vault, has secret)
~/.local/share/hellhound/skull/pups/{inbound-probe,outbound-audit}.json ← new tokens
```

---

## Tests & Validation

- `py_compile` on every new/changed Python file — clean.
- Master daemon (`hellhound.service`) restarted, confirmed new vault paths created correctly, confirmed stale `djinn/hellhound` path did NOT get recreated.
- `pup-inbound-probe.py` run manually in foreground first — connected, registered, produced a **real** (not synthetic) timeline entry: first genuine observation in Hellhound's history.
- Full detection pipeline tested end-to-end against synthetic TEST-NET-3 IPs (203.0.113.0/24, IANA-reserved, never real infrastructure): `rapid-auth-fail` and `ssh-new-user-attempt` both triggered correctly — ufw rule inserted and verified present, incident file written with correct (and then corrected) YAML frontmatter, Telegram alert delivered and confirmed via HTTP 200 + real message ID in Javier's actual chat. All test ufw rules and incident files cleaned up afterward.
- `pup@inbound-probe.service` enabled via systemd, confirmed survives past the 30s watchdog window (`hb=26s+ ago` in `hellhound status`, service still `active`), confirming the watchdog fix genuinely works, not just defaulting to a lenient state.
- `djinn-telegram-gateway.service` restarted after the audit-hook edit — starts clean, existing startup behavior (Claude-queue-alert check) unaffected.
- Confirmed dashboard (`curl localhost:8420/api/status` → 302) and SSH (`nc -zv localhost 22`) still reachable after `ufw enable`.

---

## Known Issues / Caveats

- Moonraker (Calliope/Nemesis/Iris) is not monitored — no visibility from Salomon. A future task would need an agent on each printer host.
- `trusted-ips.txt` only has the fleet + Salomon seeded — Javier's own phone/laptop/tablet aren't in it yet, so his own devices will trigger `new-source-ip-forge` alerts (deduped to once/hour) until added.
- Forge dashboard has no authentication — Hellhound detects/alerts on unrecognized traffic to it, but doesn't replace the missing auth layer. Separate task already agreed to be queued.
- `outbound-audit` pup identity is registered/unregistered on every single `audit_client.record()` call (connect → observe → disconnect each time) rather than maintaining a persistent connection — simplest correct design for sync callers, slightly noisier in the registry than a long-lived pup, but functionally fine at Javier's actual command frequency.
- No Oroborus-side pull redundancy for any of this — if Salomon goes down, detection stops (matches how the rest of the fleet already depends on Salomon).

---

## What's Next

- [ ] Javier: add personal devices (phone/laptop/tablet) to `hellhound/config/trusted-ips.txt`
- [ ] Forge dashboard authentication — separate queued task (already agreed)
- [ ] Consider a per-printer monitoring agent for real Moonraker visibility — future, not started
- [ ] Watch the first few real days of `hellhound/incidents/` and `hellhound/timeline/` to confirm no false-positive noise from legitimate fleet/dashboard traffic

---

*— Claude, 2026-07-12*
