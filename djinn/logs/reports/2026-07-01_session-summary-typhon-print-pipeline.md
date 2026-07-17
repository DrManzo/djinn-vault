---
title: Session Summary — Typhon Onboarding + Print Pipeline Architecture
agent: Claude
date: 2026-07-01
tags: [djinn, report, session-summary, typhon, printer, gcode-sync]
related:
  - "[[machines/TF-TTHQ]]"
  - "[[2026-07-01_typhon-windows-onboarding-audit]]"
  - "[[2026-07-01_typhon-windows-remote-onboarding]]"
  - "[[2026-07-01_print-library-migration]]"
  - "[[2026-07-01_djinn-gcode-sync]]"
---

# Session Summary — Typhon Onboarding + Print Pipeline Architecture

**Date:** 2026-07-01
**Agent:** Claude
**Session type:** Ops / Build (multi-part, single continuous session)
**Trigger:** Javier asked to get Typhon (reinstalled to Windows, repurposed as a shop machine)
onboarded, then to settle and build out where print files should live and how they should
move between machines.

This is an index/summary tying together five separate detailed reports written the same day.
Read this first for the overall arc; follow the links below for full technical detail on any
one piece.

---

## The Arc, in Order

### 1. Typhon Windows onboarding — audit, then live remote setup

Typhon (the MSI laptop) had been silently reinstalled from Ubuntu to Windows and repurposed as
"Typhon's Forge" — a dedicated shop machine for slicing, commissions, content, and accounting —
but none of the vault docs reflected this, and the machine wasn't actually reachable yet.

- **Audit pass:** found the docs were stale (still describing the old Ubuntu storage/sync
  role), found a hard blocker (`djinn/scripts/bootstrap-node.sh`, referenced by the Windows
  setup script, never existed), and live-probed the network to establish real state.
  → [[2026-07-01_typhon-windows-onboarding-audit]]
- **Live remote setup:** once Javier installed Claude Code + Tailscale locally on Typhon, drove
  the rest of onboarding entirely remotely from Salomon over SSH/Tailscale — authenticated
  Claude Code via credential transfer, cloned all three Djinn repos, built the `C:\Forge`
  directory tree, and installed ~18 pipeline applications (Ollama, Obsidian, Office, Blender,
  Creality Print, OrcaSlicer, FFmpeg, rclone, Discord, OpenCode, and more). **Deliberately
  skipped WSL2** in favor of native Windows — logged as a real architecture decision, not just
  an artifact of expedience. Along the way, diagnosed and worked around a Windows Session-0
  isolation issue where GUI installers and background services silently hang or crash when
  launched over a non-interactive SSH session.
  → [[2026-07-01_typhon-windows-remote-onboarding]], bug: [[2026-07-01_bug-typhon-session0-noninteractive-hangs]]
- **Debloat + reboot:** ran the previously-skipped bloatware removal, then rebooted — came back
  clean, `sshd`/Tailscale auto-started as configured. Bonus: the reboot fixed an unrelated
  1Password install failure (SID-mapping issue from the earlier account rename). Confirmed the
  Ollama Session-0 crash is *not* reboot-fixable — it's tied to the SSH session type itself.

### 2. Settling the print-file architecture (planning, no action)

Before touching any files, worked through where print files should actually live now that two
machines are in the picture:
- Ruled out routing the *live* print pipeline through a third machine (Oroborus, a separate
  storage box) — third-machine dependency, unconfirmed uptime, unclear share auth. Chose a
  direct Typhon↔Salomon Tailscale connection instead — already proven reliable this session.
- Oroborus was kept in the picture for a *different* purpose: cold/archival storage, where
  reliability doesn't matter, which is a genuinely different requirement than the live pipeline.

### 3. Print library migration — Salomon → Typhon (active) / Oroborus (archive)

Salomon's print-file library was scattered across ~9G and 632 files in four different
locations with no source of truth. Consolidated into a three-tier structure: Typhon holds the
full active working library, Oroborus holds cold archive material, Salomon keeps only piece
reports and a small confirmed-working set. Camood was excluded entirely throughout (active
troubleshooting, hands off, per explicit instruction).

Two things worth remembering from this piece: a sub-agent's classification of one directory as
"a stale duplicate, safe to delete" was **checksum-verified false** before acting on it —
archived instead of deleted, avoiding real data loss. And a `tar --exclude` argument-ordering
bug briefly leaked one Camood file into a transfer before being caught by a post-transfer check
and fixed.

A new checklist, `printer/library/UNCONFIRMED-PRINTS.md`, was created for the 17 pieces that
have design work logged but no confirmed print outcome anywhere — genuinely under-documented,
not failed, except `applacrabus` which is separately flagged as ON HOLD (a real known failure).

→ [[2026-07-01_print-library-migration]]

### 4. djinn-gcode-sync — the actual live handoff mechanism

Built and deployed the real thing: a 5-minute systemd timer on Salomon (`djinn-gcode-sync`)
that pulls new gcode from Typhon's `C:\Forge\gcode\{calliope,penelope}` over Tailscale SSH.
Calliope files auto-queue into the existing `print-queue.json`/`djinn-confirm-print` pipeline
(still requires the normal password-gated confirm — nothing auto-prints). Penelope files land
locally, ready for a manual `djinn-penelope upload`. Tested end-to-end with a real gcode file
before enabling the timer; found and fixed a real bug along the way (`scp` silently fails on
backslash remote paths against Windows OpenSSH).

→ [[2026-07-01_djinn-gcode-sync]]

### 5. Clarifying what "moving to Typhon" actually means for the printers

Late in the session, confirmed a point of potential confusion: Penelope does **not** need to
move anywhere, physically or in terms of control software. She stays wired to Salomon exactly
as before. What's already built (`djinn-gcode-sync` + the existing `djinn-penelope` CLI, which
talks to OctoPrint over the network rather than requiring SD-card swaps) already satisfies the
actual requirement — gcode reaching Salomon and being sendable to Penelope without any physical
intervention. No new work was needed here; this was a matter of confirming the existing design
already covers it, and explicitly recommending *against* routing this through Oroborus (would
reintroduce the exact third-machine risk that was ruled out in step 2, for no benefit).

A real, live example surfaced during this conversation: `proxy_holster_bore_fixed` printed
successfully on Calliope directly via Creality Print's own upload-and-print (not through the
Djinn queue) — 48 minutes, PETG, 18.5g, confirmed complete via Moonraker history. Its source
STL was found sitting in a fragile location (another session's ephemeral job temp directory)
and was moved to Typhon's library (`C:\Forge\models\library\originals\proxy-parts\holster\`)
for safekeeping. Reslicing it for Penelope specifically was discussed but not executed this
session — Penelope has process profiles already (`forge-slicer/profiles/process/Penelope-*`)
but no PETG filament profile yet, only PLA.

---

## What Changed, End to End

**On Typhon (Windows, native, no WSL2):**
- Fully reachable over Tailscale (`typhon@100.69.41.74`), SSH key auth via a physically
  USB-delivered pubkey (no other path existed at the time)
- Claude Code authenticated (credential-file transfer from Salomon)
- All three Djinn repos cloned
- `C:\Forge\*` directory tree, including the migrated print library (`models\library`,
  `models\review`) and the gcode drop zones (`gcode\calliope`, `gcode\penelope`) that
  `djinn-gcode-sync` watches
- ~18 pipeline applications installed and working; two (`ollama serve`, `claude --bg`) still
  need one human interactive/RDP session to unstick from a Windows Session-0 quirk

**On Salomon:**
- New: `djinn-gcode-sync` (script + 5-min systemd timer), pulling gcode from Typhon
  automatically and wiring Calliope jobs into the existing queue
- Print library trimmed from ~9G scattered across four locations down to just reports + a
  small confirmed-working set
- All existing safety gates preserved — nothing in any of this bypasses
  `djinn-confirm-print`'s auth prompt or `djinn-penelope`'s manual upload/print steps

**On Oroborus:**
- New: `~/print-library-archive/` — cold storage only, explicitly not part of the live
  pipeline, ~2.7G (genuine historical batches + low-value calibration/staging material)

**Untouched throughout, by explicit instruction:** all Camood-related files, everywhere.

---

## Known Gaps Left Open

- `ollama serve` and `claude --bg` on Typhon both need one interactive/RDP session to work
  past a Windows Session-0 launch issue — not fixable remotely.
- No Penelope PETG filament profile exists yet (only PLA) — relevant if reslicing PETG pieces
  for Penelope specifically.
- `djinn-model-slice` (the automated CLI) is still Calliope-only; there's no automated
  Penelope slicing path, only manual GUI slicing using the existing profiles.
- The `Z:` network drive mapping in the original `setup-typhon.ps1` plan (to Oroborus) was
  never realized and is superseded by the direct-Tailscale approach anyway.
- 17 pieces in `UNCONFIRMED-PRINTS.md` still need Javier to confirm or flag them.
- `applacrabus` needs an actual rework decision (known claw-support failure), separate from
  the confirmation checklist.

---

## Note on Vault Drift

This report is being committed after a significant real-time gap — the vault has moved well
past this session's work by the time of commit (COMMS.md and bugs.md show substantial activity
through 2026-07-17 from other sessions, including what looks like a further Typhon SSH/SMB
issue "post-reinstall" that this report has no visibility into). Everything above describes
**only** what happened in this specific session, dated accurately to 2026-07-01. It should not
be read as a current-state claim about Typhon or the print pipeline as of whenever this is
being read — check `machines/TF-TTHQ.md` and recent COMMS/build-log entries for that.

---

*— Claude, 2026-07-01*
