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
| `/mnt/storage` | sdb1 (exFAT, disk label "The Library") | 4.5T | Unsorted leftover from a prior life as a Windows backup disk — see below |
| `/run/media/drmanzo/Alexandria` | sdc1 (ext4, USB SSD) | 1.8T | **Physically here as of 2026-07-18** — moved from Salomon at some unknown point after the 2026-07-09 setup report, never logged until discovered this session. Was unmounted when found; mounted manually (`udisksctl mount -b /dev/sdc1`), no fstab entry yet (needs root, this session has no passwordless sudo — flagging for someone with an interactive shell here). See `Alexandria/README.md` on the drive itself, corrected same session.

---

## Code Repos (migrated here 2026-07-09)

`~/code/{djinn,forge,ai-tools,sec}` — see `djinn/logs/reports/2026-07-09_alexandria-setup-storage-migration-cleanup.md` for migration detail. Git was missing on this machine as of 2026-07-12 (TASK-099); confirmed installed (`git 2.53.0`) by the time this doc was written.

Status of the two repos flagged in TASK-099 as of 2026-07-18:
- `~/code/forge/forge` — real uncommitted work, committed this session (see TASK-099 in `QUEUE.md` and `COMMS.md`).
- `~/code/djinn/djinn-core` — still no `.git`, still unresolved, still needs Javier's call (not actioned).

---

## Vault

`~/djinn-vault` (not `~/Obsidian` — path differs from the convention documented in `Claude.md`/`GATEWAY.md`, noting the discrepancy rather than renaming anything). Was 226 commits behind `origin/main` as of 2026-07-18 (no sync mechanism existed on this machine) — fast-forwarded, then fixed at the root with `djinn-vault-pull` below.

**Auto-sync:** `djinn/scripts/djinn-vault-pull` (symlinked to `~/.local/bin/`) runs via user crontab every 30 min — `git fetch` + `git merge --ff-only`. Fails loud (non-zero exit, logs to `~/.local/share/djinn-vault-pull.log`) rather than clobbering anything if the tree is dirty or has diverged. Chose cron over a systemd `--user` timer because this account has no `loginctl` linger enabled and no passwordless sudo to turn it on — a user-session timer would silently stop working on logout; cron doesn't have that dependency.

**GitHub push access:** Oroborus had zero GitHub auth configured (no `gh`, no stored credential, no PAT) — same starting state Typhon was in pre-onboarding. Fixed 2026-07-18: fine-grained PAT (Javier-provided, scoped to `djinn-vault` only, Contents: Read/write) stored at `~/.config/djinn/github.env` (chmod 600) and `~/.git-credentials` (chmod 600, `git config --global credential.helper store`) — same storage locations documented for Typhon's old Ubuntu setup. Verified working (`git ls-remote`, then a real push).

---

## Storage — `/mnt/storage` does not match the plan

`forge/projects/storage-unification.md` (2026-07-07) laid out a clean `library/archive/review/index` structure for this drive. As of 2026-07-18, `/mnt/storage` still has none of that — it's leftover structure from a prior life as a Windows backup disk (`$RECYCLE.BIN`, `.Trash-1000`, `System Volume Information`, date-named folders like `Aprl - 24`/`May - 24`), plus `Library` (234G), `Backups` (23G), `typhon-backup` (14G), `forge` (664M), `Linux` (1.4G). The Phase 1-6 reorg was apparently never executed past the initial LAN hookup.

**`Library` (234G) is not a print-model library — it's a pirated software/course stash** (cracked Adobe/Autodesk installers, ripped Udemy/Domestika courses, all sourced from `gfxfather.com`). Unrelated to the djinn/forge project, predates this drive's role as Oroborus's storage node. Per Javier's instruction 2026-07-18: relocating it to `Alexandria/library-rescue/` (staging, not organized — "will live there for now"), then clearing it off `/mnt/storage`. Not being cataloged or maintained as part of any real library structure.

**`Backups/12-1`** (21G, inside the 23G `Backups` dir) — inspected one level deep: a genuine old personal backup (home-directory-style dump: `Sort`, `Work`, `Sophia`, `Yoshi`, a `usr`/`DEBIAN` pair, some PDFs, a couple `.deb` installers). Left alone — no reason to touch it.

**Everything else in `/mnt/storage` not touched this session** — `Backups` (minus the Library move), `typhon-backup`, `Aprl - 24`/`May - 24`, `Linux`, `forge`, and the Windows-cruft folders are still unreviewed. Moving/deleting that is a call for Javier, not something to do speculatively.

---

*— Oroborus, 2026-07-18*
