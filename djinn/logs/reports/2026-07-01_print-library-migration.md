---
title: Session Report — Print Library Migration to Typhon/Oroborus
agent: Claude
date: 2026-07-01
tags: [djinn, report, printer, library, typhon, oroborus]
related: [[machines/TF-TTHQ]] | [[printer/library/README]] | [[printer/library/UNCONFIRMED-PRINTS]]
---

# Session Report — Print Library Migration to Typhon/Oroborus

**Date:** 2026-07-01
**Agent:** Claude
**Session type:** Ops / Build
**Trigger:** Following Typhon's Windows onboarding, Javier asked to settle where print files
should live going forward, then to execute a cleanup of the scattered print library on Salomon.

---

## Summary

Salomon's print-file library was scattered across four locations (`~/printer-files/`,
`~/Desktop/Review/`, stray `~/Downloads/` exports, and a small vault-adjacent set) totaling
~9G and 632 files, with no single source of truth. Consolidated this into a three-tier
architecture: Typhon (`C:\Forge\models`) now holds the active working library; Oroborus
(`192.168.1.154`) holds cold/historical archive material; Salomon keeps only piece reports and
a small confirmed-working set needed for actual print execution. Camood files were excluded
from the entire operation per explicit instruction (active troubleshooting, hands off).

---

## What Was Built or Changed

**Architecture decision (made earlier in conversation, executed this session):** print files
flow Typhon (slice) → direct Tailscale transfer → Salomon (print), not through Oroborus —
Oroborus was ruled out for the *active* pipeline (third-machine dependency, unconfirmed uptime,
unclear share auth) but adopted for *cold storage* of historical/low-value material, which is
a different use case with no reliability requirement.

**Inventory finding that overturned an initial classification:** a sub-agent's first pass
claimed `~/printer-files/vault-printer/` (1.5G, 85 files) was a stale duplicate of the vault's
own `printer/{originals,prints}` and could be dropped. Verified this directly with checksum
spot-checks before acting — it was **not** a duplicate of anything, anywhere on the system.
Revised the plan to archive it to Oroborus instead of deleting it. This is worth remembering:
don't trust a classification claim for a delete decision without independent verification,
even when the source did real investigation.

**Bug found and fixed during execution:** `tar --exclude` patterns are ignored if placed
*after* the file/directory argument on the command line (GNU tar 1.35) — they must come before.
One transfer (`Desktop/Review` → Typhon) used the wrong order and let a Camood file leak
through; caught immediately via a post-transfer `findstr` check, deleted from Typhon, and
redone with the excludes correctly positioned. All other transfers had excludes in the correct
position from the start and were clean on first pass.

**Transfers executed:**
- `~/printer-files/library/` (3.9G) → Typhon `C:\Forge\models\library` (3.87G landed, delta is
  the excluded Camood files) — via `tar czf - | ssh ... tar xzf -` (Typhon has no rsync)
- `~/Desktop/Review/` (655M) → Typhon `C:\Forge\models\review` (0.64G landed)
- `~/printer-files/archive/` (1.1G, genuine historical batches) → Oroborus
  `~/print-library-archive/printer-files-archive/` — via rsync (Oroborus has rsync)
- `~/printer-files/vault-printer/` (1.5G, see above) → Oroborus
  `~/print-library-archive/vault-printer/`
- Low-value tier (`printer-files/staging/`, `recovery/`, `calliope-safe-point-2026-06-02/`,
  scattered `Downloads/` Meshy AI/paracord exports) → Oroborus
  `~/print-library-archive/junk-tier/`

**Cleanup on Salomon** (via `gio trash`, not `rm`, per standing preference — verified transfer
integrity by size comparison before trashing anything):
- `printer-files/library`, `archive`, `vault-printer`, `staging`, `recovery`,
  `calliope-safe-point-2026-06-02` — trashed
- `Desktop/Review` — Camood file moved out first, rest of directory trashed, Camood file moved
  back into place afterward
- Migrated `Downloads/` files — trashed
- **Left untouched, out of scope:** `printer-files/{models,queue,creality-datadir,inventory,logs,scripts}`
  (~70M remaining) — these look like active tooling/config directories, not library content,
  and weren't part of what was discussed for migration.

**New checklist created:** `printer/library/UNCONFIRMED-PRINTS.md` — 17 pieces have design/repair
work logged but no confirmed successful-print record anywhere (COMMS, build-log, PRINT-LOG.md,
or their own piece report). Cross-referenced against each piece's own report; confirmed these
are genuinely under-logged (no "Print Status" section at all), not silently failed. One
exception: `applacrabus` has an explicit **ON HOLD** status — claw supports collapsed
mid-print 2026-06-04 — flagged separately from the "just needs confirmation" bucket since it
needs an actual rework decision. All of these pieces' files migrated to Typhon regardless, on
the assumption they're fine; the checklist just closes the loop on the written record.

---

## Technical Decisions

**Archive rather than delete "the rest" — Why:** explicit instruction ("do the best option
that will help us in the end") interpreted in favor of the safer default — Typhon is one day
into being a reliable machine, and irreversible deletion of unverified-value files isn't worth
the disk space saved when Oroborus has 404G free.

**Copy-then-verify-then-trash, never move-then-hope — Why:** every transfer was size-checked
(and for the vault-printer reclassification, checksum-checked) against the source before any
`gio trash` call. This caught the tar-exclude-order bug before it caused permanent data loss —
worth the extra round-trips.

**Left `printer-files/{models,queue,creality-datadir,...}` alone — Why:** these weren't
discussed explicitly in the planning conversation, and unlike `library`/`archive`/`vault-printer`
they look like active working directories for existing tooling (`creality-datadir` in
particular sounds like live slicer config). Migrating or archiving them without confirming
they're not in active use by `djinn-model-slice` or similar would risk breaking something
currently working.

---

## Files Created or Modified

```
djinn/printer/library/README.md                                      ← points to new Typhon/Oroborus locations
djinn/printer/library/UNCONFIRMED-PRINTS.md                          ← new — checklist for Javier
djinn/machines/TF-TTHQ.md                                             ← notes library now lives on Typhon
djinn/logs/reports/2026-07-01_print-library-migration.md             ← this report

On Salomon (not vault-tracked):
~/printer-files/{library,archive,vault-printer,staging,recovery,calliope-safe-point-2026-06-02}  ← trashed
~/Desktop/Review/*  (except Camood file)                             ← trashed
~/Downloads/{Meshy_AI_export_*.stl, 2131/}                           ← trashed

On Typhon (not vault-tracked):
C:\Forge\models\library\   ← new, 3.87G
C:\Forge\models\review\    ← new, 0.64G

On Oroborus (not vault-tracked):
~/print-library-archive/{printer-files-archive,vault-printer,junk-tier}/  ← new, ~2.7G total
```

---

## Tests & Validation

- Every transfer size-checked against source (`du -sh` / PowerShell `Get-ChildItem ... Measure-Object`)
  before proceeding to the next step or to cleanup.
- Camood exclusion verified with `findstr /i camood` against the full recursive listing on
  Typhon after each transfer — caught and fixed the one leak (`Desktop/Review` transfer).
- `vault-printer/` duplicate claim verified false via `md5sum` spot-checks against the vault,
  `printer-files/library/`, and `Desktop/Review/` — zero matches found across 8 sampled files.
- Post-cleanup `du -sh` on Salomon confirms `printer-files` dropped from 6.5G → 70M,
  `Desktop/Review` from 655M → 1.4M (just the Camood file).

---

## Known Issues / Caveats

- The confirmed-working set kept directly on Salomon is small (mario pipe, Forge coins, proxy
  recycler) — if `djinn-confirm-print` or other tooling expects a specific local path for these
  that wasn't part of the migrated directories, it should still be intact since nothing in
  `printer-files/{models,queue}` was touched, but this wasn't explicitly re-verified against
  the actual print-execution scripts.
- Oroborus's uptime/reliability is still unconfirmed for anything beyond "it responded to SSH
  during this session" — fine for cold storage (no active dependency), but don't assume it for
  anything time-sensitive.
- `UNCONFIRMED-PRINTS.md` is a point-in-time snapshot — if Javier confirms pieces going
  forward, that file should get checked off / updated, not left stale.

---

## What's Next

- [ ] Work through `UNCONFIRMED-PRINTS.md`, confirm or flag each piece — @Javier
- [ ] Decide on `applacrabus` rework, separate from the confirmation checklist — @Javier
- [ ] Build the actual Typhon→Salomon gcode handoff mechanism (direct Tailscale transfer,
      per the earlier architecture decision) — not done this session, only the library
      migration was — @Claude, next session
- [ ] Confirm `printer-files/{models,queue,creality-datadir}` are still fully intact and
      referenced correctly by existing print tooling — @Claude or @Javier, sanity check

---

*— Claude, 2026-07-01*
