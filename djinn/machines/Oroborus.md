---
title: Machine — Oroborus
tags: [djinn, machine, oroborus, hardware, storage, claude]
created: 2026-07-18
updated: 2026-07-18
---

# Machine: Oroborus

**Callsign:** Oroborus
**Network name:** `oroborus` (hostname confirmed)
**Role:** Storage node (cold archive + code host) + first Claude Code host outside Salomon/Typhon. Not part of the live print pipeline — see `forge/projects/storage-unification.md`.
**IP:** LAN `192.168.1.154` (dynamic, `wlp2s0`)
**SSH:** `drmanzo@192.168.1.154`
**Claude Code:** ✅ Live as of 2026-07-18 — this session is the first Claude Code run on this machine, fulfilling the "Claude-on-Oroborus" role left open in `QUEUE.md`/`COMMS.md` since 2026-07-12 (TASK-099).
**opencode:** ✅ Installed at `~/.opencode/bin/opencode`. No default model configured in `~/.config/opencode/opencode.jsonc` (schema stub only) — no remote Ollama providers wired up here, unlike Salomon/Typhon. Available models are opencode's own free-tier set (`opencode/*`).
**Related:** [[SYSTEM-STATE]] | [[ROUTING]] | [[GATEWAY]] | `forge/projects/storage-unification.md`

Changes from this machine are signed: `— Oroborus`

---

## Hardware

| Component | Spec |
|-----------|------|
| **CPU** | AMD Athlon Gold 3150U w/ Radeon Graphics — 2C/4T |
| **RAM** | 5.2GB (small — not a compute node, don't route inference here) |
| **OS Drive** | 476.9GB NVMe SSD — `/` (48G used) |
| **Bulk Storage** | 4.5TB HDD (`/dev/sdb1`) — `/mnt/storage` |
| **OS** | Ubuntu 26.04 LTS |

Note: earlier planning docs (`forge/projects/storage-unification.md`, 2026-07-07) described this machine as "2TB SSD" — actual bulk storage is a 4.5TB HDD at `/mnt/storage`. Correcting here; not chasing down every stale reference elsewhere in the vault in this pass.

---

## Storage Layout

| Mount | Device | Size | Contents |
|-------|--------|------|----------|
| `/` | nvme0n1p2 | 468G | OS, apps, `~/code/`, `~/djinn-vault/` |
| `/mnt/storage` | sdb1 | 4.5T | Cold archive per `forge/projects/storage-unification.md` |

---

## Code Repos (migrated here 2026-07-09)

`~/code/{djinn,forge,ai-tools,sec}` — see `djinn/logs/reports/2026-07-09_alexandria-setup-storage-migration-cleanup.md` for migration detail. Git was missing on this machine as of 2026-07-12 (TASK-099); confirmed installed (`git 2.53.0`) by the time this doc was written.

Status of the two repos flagged in TASK-099 as of 2026-07-18:
- `~/code/forge/forge` — real uncommitted work, committed this session (see TASK-099 in `QUEUE.md` and `COMMS.md`).
- `~/code/djinn/djinn-core` — still no `.git`, still unresolved, still needs Javier's call (not actioned).

---

## Vault

`~/djinn-vault` (not `~/Obsidian` — path differs from the convention documented in `Claude.md`/`GATEWAY.md`, noting the discrepancy rather than renaming anything). Clean clone of `origin/main` as of 2026-07-18.

---

*— Oroborus, 2026-07-18*
