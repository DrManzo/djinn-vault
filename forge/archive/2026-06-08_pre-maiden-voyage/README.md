# Pre-Maiden Voyage Archive

**Date archived:** 2026-06-08
**System state:** djinn-print-track v2 — WebSocket-driven, all 4 automation gaps closed

## Contents

| Directory | Description |
|-----------|-------------|
| `data/` | prints.json (5 records), print-queue.json (5 jobs), current.json, filament-inventory.json (3 spools), session.csv |
| `backups/` | 3-generation backup chain for all data files + pre-v2-backup + May 26 queue backup |
| `pre-v2/` | Snapshot of v1 data taken just before v2 upgrade |
| `prints/` | 34 structured print record directories + 8 loose markdown records |
| `scripts/` | v1 script backup (`djinn-print-track.v1.bak`) |
| `state/` | Discord watch state, watcher state |

## Why This Exists

Archived for the Typhon's Forge **maiden voyage** — the first official commission under the clean system. All prior data was development and testing. This snapshot preserves it for future reference without cluttering the live system.

## Notable Records

- **Terp Tribe cup (Camood)** — First successful production piece, 89g, 160min
- **CRtestcube** — v2 WebSocket live test, 11g, 26min (all 4 closures verified)
- **Mario Pipe (ORD-012)** — Backfilled legacy print, 60g, 167min
- **AnybodyWantCoffee (ORD-013)** — Backfilled legacy print, 26g, 102min
- **Vase collection (Jun 1)** — 26 directories across 4 models, many failed iterations

## Maiden Voyage System State

- Filament: PLA Black (ANYCUBE) — SPOOL-003, 1000g
- Daemon: djinn-print-track v2 (WebSocket)
- Queue: Empty, `next_id: 1`
- Moonraker `[job_queue]`: `load_on_startup: true`, `automatic_transition: true`
