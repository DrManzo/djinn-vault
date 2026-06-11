---
title: Session Report — Hellhound Runtime Push
agent: Claude
date: 2026-06-10
tags: [djinn, report, hellhound, ipc, daemon, pups]
related: [[build-log]] | [[decision-log]] | [[COMMS]]
---

# Session Report — Hellhound Runtime Push

**Date:** 2026-06-10
**Agent:** Claude
**Session type:** Architecture / Review
**Trigger:** Javier pushed Hellhound v1 to DrManzo/djinn-vault main (commit e35832a) and briefed Claude on what landed.

---

## Summary

Hellhound is a new async Unix socket daemon that manages "pups" — lightweight agent gateway processes — with a registry, heartbeat loop, SQLite indexer, vault timeline scribe, and graceful RECALL-on-shutdown. It replaces ad-hoc per-gateway subprocess management with a unified IPC bus and lifecycle contract. The push landed the full runtime, gate abstraction layer, cortex pipeline, effector layer, systemd units, and CLI. Installation on Salomon is the next step (delegated to Salomon via QUEUE).

---

## What Was Built or Changed

- `hellhound/hellhound.py` — async Unix socket server; pup registry; rolling log writer; SQLite indexer; vault timeline scribe; graceful RECALL-on-shutdown
- `hellhound/pup.py` — PupClient context manager; CONNECT handshake; `observe()`; `wait_recall()`; background heartbeat loop
- `hellhound/pup-gateway.py` — Discord gateway pup; StubGateway fallback (fires fake observation every 10s for pipeline testing)
- `hellhound/pup-template.py` — opinionated new-pup template enforcing heartbeat + RECALL handling
- `gates/__init__.py` + `gates/base.py` — abstract BaseGate with `connect()` / `stream()` / `disconnect()`
- Cortex pipeline: `commander.py` (→ QUEUE.md), `scribe.py` (→ vault), `watchdog.py` (patrol + anomaly detection), `synapsis.py` (cross-ref stub), `linker.py` (backlinks)
- Effector layer: `alerter.py`, `archiver.py` (gzip rotation + SQLite compaction), `effector/scribe.py` (re-export shim)
- Systemd units: `hellhound.service`, `hellhound.socket`, `pup@.service` (template unit)
- CLI: `hellhound/bin/hellhound` — status, send pup, recall [--all], log [--tail N], patrol, pup new <name>
- Vault MOC: `skull/vault-hellhound/_index.md`

---

## Technical Decisions

**Unix socket over TCP** — local IPC only; no network stack overhead; OS enforces socket permissions; right choice for daemon-to-pup comms on a single machine.

**RECALL-on-shutdown vs SIGTERM cascade** — RECALL is a protocol-level signal pups explicitly handle, not an OS signal. This allows pups to flush state, write vault entries, and close cleanly before hellhound exits. Harder to get right, but the only correct approach for a vault-scribe daemon.

**StubGateway for Discord pup** — fires a synthetic observation every 10s so the full pipeline (socket → registry → SQLite → vault timeline) can be validated before a real Discord token is wired in. This is the right development order.

**BaseGate abstraction** — `connect() / stream() / disconnect()` contract means Telegram, webhook, or IRC pups can be added without touching hellhound core.

**synapsis.py as stub** — cross-referencing between pups deferred. Correct call — get the single-pup lifecycle right first.

---

## Files Created or Modified

```
hellhound/hellhound.py             ← async socket server, pup registry, vault scribe
hellhound/pup.py                   ← PupClient context manager + heartbeat loop
hellhound/pup-gateway.py           ← Discord gateway pup + StubGateway
hellhound/pup-template.py          ← template for new pups
gates/__init__.py                  ← gate package init
gates/base.py                      ← BaseGate abstract interface
commander.py                       ← cortex: QUEUE.md writer
scribe.py                          ← cortex: vault writer
watchdog.py                        ← cortex: patrol + anomaly detection
synapsis.py                        ← cortex: cross-ref stub (not yet implemented)
linker.py                          ← cortex: backlinks
alerter.py                         ← effector: notifications
archiver.py                        ← effector: gzip rotation + SQLite compaction
effector/scribe.py                 ← effector: re-export shim
skull/hellhound.service            ← systemd service unit
skull/hellhound.socket             ← systemd socket unit
skull/pup@.service                 ← systemd template unit for pups
hellhound/bin/hellhound            ← CLI
skull/vault-hellhound/_index.md   ← vault MOC
```

---

## Dependencies Installed

| Package | Method | Purpose |
|---------|--------|---------|
| None new | — | Runtime uses stdlib asyncio + sqlite3 |

---

## Tests & Validation

- Not yet validated on Salomon (installation pending)
- StubGateway designed to produce fake observations every 10s for full pipeline test before real Discord token
- Validation path: install → `hellhound pup new gateway` → `systemctl --user start pup@gateway` → observe 10s heartbeats flowing through socket → SQLite → vault timeline

---

## Known Issues / Caveats

- `synapsis.py` is a stub — no cross-pup context sharing yet
- `pup@.service` is a systemd template unit; need a defined canonical pup list for boot auto-start
- Unix socket auth relies on socket path permissions — should live in a mode-700 directory
- Cortex pipeline has no declared execution ordering or failure isolation between modules (if `watchdog.py` errors, unclear whether `scribe.py` is blocked)
- Discord token not yet wired into `pup-gateway.py` (StubGateway mode only)

---

## What's Next

- [ ] Install runtime to `~/.local/share/hellhound/` — @Salomon (QUEUE pending approval)
- [ ] Install CLI to `~/.local/bin/` — @Salomon
- [ ] Install systemd units and enable hellhound.socket + hellhound.service — @Salomon
- [ ] Provision gateway pup and validate StubGateway pipeline — @Salomon
- [ ] Wire real Discord token into pup-gateway.py — @Javier / @Claude
- [ ] Define canonical pup list for boot auto-start — @Claude
- [ ] Implement synapsis.py cross-ref logic — @Claude (future)
- [ ] Add cortex pipeline failure isolation (try/except per module) — @Claude (future)

---

*— Claude, 2026-06-10*
