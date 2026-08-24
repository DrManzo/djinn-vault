---
title: Recovered missing forge STL library from Typhon — Alexandria's library/ and review/ trees were empty
date: 2026-08-24
system: printer-files / Alexandria storage / Typhon
severity: high
status: fixed
---

# Missing forge STL library recovered from Typhon

## Symptom
While tracking down the Puffco Proxy Tornadocycler STL (Javier asked what happened to it — see [[2026-08-16_bug-iris-mcu-timer-too-close-shutdown]] for the print incident that surfaced it), found that `library/` didn't exist at all under Alexandria's `printer-files/` tree, and `~/printer-files/library/` on Salomon was empty too — only `log-archive/` and `recovery/` were present locally. Javier's read on this was that files had been deleted from the forge; the actual cause was storage drift, not deletion by any agent this session.

## Investigation
- Exhaustively searched Alexandria (`vault-snapshots/current/`, `printer-files/`, and the `oroborus-*-rescue` archives) for the Tornadocycler STL under all three of its known historical paths/names — zero binary hits, only markdown records referencing it.
- SSH'd into Typhon (`typhon@100.69.41.74`, Tailscale — the LAN IP `192.168.1.113` now belongs to Calliope, which inherited it) and found the real library intact at `C:\Forge\models\library\` — 148 files across `originals/` (logos, phone-stands, proxy-parts, proxy-tornado-recycler, puffco, spooletarium, typhons-forge-coin) and `penelope/` (kitten, koi, mario-pipe, proxy-stand) — plus a `C:\Forge\models\review\` tree (35 files: Oni Collection, Demon Slayer, Catrina, Totoro, Pokemon Gengar, cherry blossom cups, the paracord jig, melted-candle pillars, holster/filament-guide review pieces).
- `C:\Forge\models\utility\` (10 job-output STLs) was also present on Typhon but already exists on Alexandria in a *more* complete form (includes `.scad` sources Typhon's copy doesn't have) — left untouched, no merge needed.
- `C:\Forge\tools\OrcaSlicer\` accounted for 255 of the 455 total `.stl` files on Typhon — confirmed these are OrcaSlicer's own bundled build-plate/bed models (Voron, SecKit, BIQU, Anker, Dremel, etc.), not forge project files. Excluded from the pull.
- `C:\Forge\queue\` (4 files) matched what Alexandria's `printer-files/queue/` already has — transient job artifacts, not library content, skipped.

## Root cause
Not established with certainty — no deletion event, agent action, or commit touches these paths anywhere in `bugs.md`/`build-log.md` history. Most likely explanation: the `library/` and `review/` trees simply never made it across during the mid-July Library→Alexandria migration (the same window that produced the already-logged Backpack Boyz and Camood TTHQ "lost-file" bugs) — this looks like the same migration gap, just not caught until now because nothing needed those specific files in the intervening five weeks.

## Fix
- Pulled all 455 `.stl` files from `C:\Forge` on Typhon as a single `tar` archive (per [[feedback_typhon_file_transfers]] — glob/`scp -r` silently truncates against Typhon's Windows OpenSSH) — 1577.96MB, byte-verified after transfer.
- Extracted to a staging directory, filtered out `tools/` (slicer software, not ours) and `queue/`/`utility/` (already current on Alexandria), and copied `library/` (1.1GB) and `review/` (493MB) into `/run/media/drmanzo/alexandria/printer-files/` — purely additive (`cp -n`, no existing files touched or overwritten).
- Symlinked `~/printer-files/library` and `~/printer-files/review` → the Alexandria copies, so any doc or tool that references the `~/printer-files/library/...` path directly (several piece notes do) resolves correctly again without duplicating 1.6GB onto Salomon's local disk.
- Verified: `~/printer-files/library/originals/proxy-tornado-recycler/Proxy_Tornado_Recycler.stl` now resolves.

## Note
Nothing was deleted from Typhon — this was a pull/copy only. Typhon's `C:\Forge` remains the live source; Alexandria and Salomon now have a current mirror of `library/` and `review/` again.

— Claude
