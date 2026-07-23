---
title: Machine — Oroborus
tags: [djinn, machine, oroborus, hardware, storage, claude]
created: 2026-07-18
updated: 2026-07-23
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

## Storage — `/dev/sdb` ("The Library", `/mnt/storage`) is a failing drive — emergency rescue completed 2026-07-18/19

`forge/projects/storage-unification.md` (2026-07-07) laid out a clean `library/archive/review/index` structure for this drive. As of 2026-07-18, `/mnt/storage` had none of that — leftover structure from a prior life as a Windows backup disk (`$RECYCLE.BIN`, `.Trash-1000`, `System Volume Information`, date-named folders `Aprl - 24`/`May - 24`), plus `Library` (234G), `Backups` (23G), `typhon-backup` (14G), `forge` (664M), `Linux` (1.4G). The Phase 1-6 reorg was never executed past the initial LAN hookup.

**Mid-transfer, the drive itself turned out to be failing.** Started moving `Library` (confirmed pirated software/course stash from `gfxfather.com`, unrelated to the djinn/forge project) to `Alexandria/library-rescue/` per Javier's instruction. Six hours in, throughput had collapsed from ~40-90MB/s to 150-220**kB**/s. `journalctl -k` showed the root cause: **4,442 `critical medium error` / `Unrecovered read error` events**, spanning sectors ~313,088 to ~692,097,520 — scattered across nearly the entire used capacity, not one bad patch. No `smartctl` available (not installed, no root to install it) to get a real health verdict, but the symptom profile (widespread, not localized) reads as a drive whose reallocation pool is exhausted or with genuine broad media/head degradation. **Verdict: don't trust this drive with anything you'd be upset to lose, ever again.** Retire it, don't try to "fix" it.

**Emergency response (2026-07-18/19):** Killed the stalled Library copy (already had 135G of the 234G — kept, since even partial piracy-stash salvage was free at that point) and pivoted to rescuing everything else on the drive that might be real, since digging in showed `Aprl - 24`/`May - 24`/`Linux`/`forge` were **not** just more junk as first assumed — they had genuine college coursework, CAD/SketchUp files, business estimates, an old home-directory backup (with an `Obsidian/` folder in it), and named `forge/` print-project folders (`applacrabus`, `kraken`, `med-core`, `tardis`, etc.) mixed in with more gfxfather piracy. Ran six parallel rsync jobs to `Alexandria/archive/oroborus-*-rescue/`:

| Source | Rescued | Files lost to bad sectors | What was lost |
|---|---|---|---|
| `Library` | 135G/234G (stopped early, disposable) | many | pirated software, not tracked |
| `Backups` | 22G/23G | 15 files | **real personal photos/video** (JPG/HEIC/MOV in `12-1/Sort`, `12-1/Work/Pics to post`, `12-1/Yoshi`) — Javier confirmed acceptable loss, not pursuing `ddrescue` recovery |
| `typhon-backup` | 443M/14G | 33 files | all Ollama model blobs + Python venv site-packages — 100% re-downloadable/rebuildable, nothing real lost |
| `Linux` | 489M/1.4G, 7,962/7,962 files processed | 1 file | a single Python tzdata file, trivial |
| `forge` | 645M/664M | 0 | clean |
| `Aprl - 24` | 21G/21G | 0 | clean |
| `May - 24` | 42G/57G | 6 files | more gfxfather ISOs/rars, disposable |

**Net result:** everything on this drive that was plausibly irreplaceable is now also on Alexandria (`archive/oroborus-*-rescue/`), except the 15 photos/videos in `Backups/12-1` — genuinely lost, Javier accepted this rather than attempt `ddrescue`. Original copies were **left in place on `/mnt/storage`** — not deleted, since there's no pressing need and further write/delete operations on a drive already dying isn't obviously worth doing. Javier hasn't yet said whether to wipe, retire, or physically pull this drive — open decision, not actioned further.

---

*— Oroborus, 2026-07-23*
