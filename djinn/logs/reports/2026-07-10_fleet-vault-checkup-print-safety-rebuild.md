---
title: Session Report — Vault Check-in, Printer Fleet Recovery, Print-Safety Watchdog Rebuild
agent: Claude
date: 2026-07-10
tags: [djinn, report, calliope, nemesis, iris, print-safety, alexandria, makers-mark]
related: [[2026-07-09_bug-calliope-cable-fixed]] | [[2026-07-09_bug-print-safety-wrong-mcu-query]] | [[2026-07-09_bug-makers-mark-migration-3mf]] | [[build-log]] | [[bugs]] | [[COMMS]]
---

# Session Report — Vault Check-in, Printer Fleet Recovery, Print-Safety Watchdog Rebuild

**Date:** 2026-07-09 through 2026-07-10 (overnight)
**Agent:** Claude
**Session type:** Ops / Debug / Build
**Trigger:** Javier asked for a general vault catch-up; session extended live through Calliope's post-cable-replacement bring-up and turned into a full print-safety rebuild across the fleet.

---

## Summary

Started as a routine catch-up read of the Djinn vault (SOUL/IDENTITY/USER/AGENTS/GATEWAY, recent COMMS/build-log/bugs, fleet status). Turned into an all-night live-ops session once Javier installed Calliope's replacement nozzle_mcu cable and started production printing: two more `key561` crashes were diagnosed and root-caused (wrong filament temp profile, not a bad cable), the print-safety watchdog was discovered to have never actually worked in its entire existence and was fixed and generalized to the full fleet (Calliope, Nemesis, Iris), an Alexandria SSD filesystem corruption was found and repaired mid-session, `djinn-model-mark` was fixed after being broken by yesterday's storage migration, and auto-generated completion reports were added to the watchdog. All three printers ended the session actively printing, clean, and watched by a genuinely functional safety system for the first time.

---

## What Was Built or Changed

- **Nemesis:** verified the queued `[probe]` SAVE_CONFIG fix was already applied; cleared up an apparent z_offset/mesh "regression" that was actually Javier's own unlogged recalibration after relocating the machine.
- **QUEUE.md correction:** annotated the Calliope bring-up checklist — it told Javier to reinstall a fan-cap M106 workaround that BUG-014's 6/29 root-cause update had already proven ineffective.
- **Calliope cable install (BUG-014 close-out):** printer now at `192.168.1.113` (not `.114` — inherited Typhon's freed DHCP lease). Two more `key561` crashes after the cable/reseat, root-caused as PLA filament being printed at an accidentally-selected PETG temperature profile (240–250°C vs PLA's ~200°C) — excess heat next to the connector board, not a bad cable. Re-sliced correctly: 1x, 2x, 3x, and 4x-copy PLA plates all completed clean.
- **`djinn-print-safety` — found broken, fixed, generalized:**
  - Was querying the wrong Moonraker object/field path (`mcu` top-level instead of `mcu nozzle_mcu`'s nested `last_stats`) — every poll silently computed nothing, ever, including during tonight's crashes.
  - Systemd unit used `Restart=on-failure`, but the daemon exits clean (code 0) after every completed print, so it silently stayed dead until manually restarted.
  - Both fixed. Generalized from Calliope-only to the full fleet via a templated systemd unit (`djinn-print-safety@.service`) + per-printer env files, covering Calliope (`nozzle_mcu`), Nemesis (`eboard`), and Iris (`eboard`). Migrated the live Calliope instance with zero monitoring gap.
  - Added auto-generated completion reports (`forge/prints/<ts>_<printer>_<job>/report.md` + Telegram ping) on every complete/cancelled/error transition, with a persisted dedup marker to prevent the `Restart=always` relaunch cycle from re-reporting the same finished print indefinitely.
- **`djinn-model-mark` — found broken by yesterday's migration, fixed:**
  - `makers-mark.json` pointed at a pre-migration Salomon path; repointed to Alexandria.
  - The 15mm mark source STL itself is corrupted (unrelated bug); worked around via the 20mm sibling file.
  - Tool crashed on any `.3mf` input (loads as a `trimesh.Scene`, not a bare mesh); patched to unwrap it. Used to stamp `puffco-710_fixed.3mf` → `puffco-710_marked.stl`.
- **Alexandria SSD — filesystem corruption mid-session, repaired:** ext4 root directory (inode #2) became unreadable; kernel log showed the drive had physically re-enumerated to a new device node (`/dev/sdb` → `/dev/sdd`), which is why the first `e2fsck` attempt failed. Unmounted, `e2fsck -y` against the correct current node, clean journal recovery, no data loss, remounted successfully (UUID-based fstab entry survived the device-letter change with no edits needed).
- **Camood investigation:** the original TTHQ-text-engraved-and-marked combo file from the June 4 session no longer exists anywhere (checked Alexandria, Downloads, Oroborus, the referenced archive path) — only mark-only or fully-clean variants survive. Dropped a mark-only copy (`camood_marked.stl`) in Downloads per Javier's request; the text engraving would need to be rebuilt from scratch if wanted later.

---

## Technical Decisions

**Generalize the watchdog via a templated systemd unit rather than three separate hardcoded copies — Why:** one script, one bug surface. Per-printer differences (Moonraker URL, display name, MCU object name) are all environment-driven now, so a future fourth printer is a new env file, not a code change.

**Gate Calliope's Z=95–115mm "danger zone" probability boost behind `PRINTER_NAME == "Calliope"` — Why:** that zone was derived from Calliope's specific arm.stl cable-stress crash analysis and has no basis on Nemesis/Iris's different hardware.

**Dedup completion reports via a persisted marker file, not an in-memory flag — Why:** the daemon process itself gets recycled by `Restart=always`, so any dedup state has to survive across process restarts, not just within one run.

**Don't chase down the dead `djinn-print-track` service or the duplicate `print-monitor-v2`/`forge-print-monitor-v2` units tonight — Why:** out of scope for what was actually asked (a completion-report ping), and untangling a multi-generation legacy tool stack under time pressure at 2am is a worse trade than flagging it clearly for a dedicated session.

---

## Files Created or Modified

```
~/.local/bin/djinn-print-safety                        ← fixed MCU query bug, generalized to fleet, added completion reports
~/.local/bin/djinn-model-mark                            ← fixed Scene-unwrap crash on .3mf input
~/.config/forge/djinn-{calliope,nemesis,iris}.env        ← new: per-printer watchdog config
~/.config/systemd/user/djinn-print-safety@.service       ← new: templated unit (replaces djinn-print-safety.service)
~/.config/forge/makers-mark.json                          ← repointed to Alexandria + working 20mm source file
~/Obsidian/djinn/communications/QUEUE.md                 ← annotated stale Nemesis/Calliope task entries as resolved
~/Obsidian/djinn/logs/bugs.md                             ← 5 new bug entries (see Known Issues below)
~/Obsidian/djinn/logs/build-log.md                        ← full session detail
~/Obsidian/djinn/logs/reports/2026-07-09_bug-calliope-cable-fixed.md
~/Obsidian/djinn/logs/reports/2026-07-09_bug-makers-mark-migration-3mf.md
~/Obsidian/djinn/logs/reports/2026-07-09_bug-print-safety-wrong-mcu-query.md
~/Downloads/puffco-710_marked.stl                         ← maker's-mark output
~/Downloads/camood_marked.stl                             ← maker's-mark output
```

---

## Tests & Validation

| Test | Result |
|------|--------|
| Nemesis `[probe]` SAVE_CONFIG fix | Confirmed structurally in place via SSH |
| Calliope 1x/2x/3x/4x-copy PLA plates | All completed clean, zero comms errors, correct temps |
| `djinn-print-safety` fixed MCU query, live | `Z=1.4mm \| retx=0.0% \| emi=0.00B/s \| p=0%` — clean output every poll |
| Watchdog fleet rollout (3 instances) | All `active (running)`, correct Moonraker URL + MCU object each |
| `djinn-model-mark` on `.3mf` directly | Watertight single-component output, geometry matches manual-extraction workaround |
| Completion-report dry run (fake printer, temp copy) | Report written correctly; second call correctly deduped, no duplicate |
| Alexandria `e2fsck -y /dev/sdd1` | Clean journal recovery, 0 files relocated to lost+found, remount successful |

---

## Known Issues / Caveats

- **Calliope's cable fix is not yet stress-tested at real PETG temps.** All four clean runs tonight were PLA. The original crashes happened on (accidentally-mis-profiled) PETG-temperature runs. A genuine PETG job at correct temps is the real test of whether the physical fix holds — currently in progress on Nemesis and Iris (Camood PETG), not yet attempted again on Calliope specifically.
- **`djinn-print-track.service` has been silently dead since 2026-07-05** — hardcoded to the stale `.114` IP, no log output in 5 days. Not fixed tonight (out of scope), but it's the tool that used to generate the richer `plan.md`/`model_analysis.json`/`postmortem.md` job-folder pattern seen in older `forge/prints/` entries. The new watchdog completion report is a simpler replacement, not a full equivalent.
- **Duplicate/unclear systemd units:** `djinn-print-monitor-v2` and `forge-print-monitor-v2` both exist (service + timer each) — likely leftovers from the 7/8 department restructure. Not investigated which, if either, is canonical.
- **Camood's TTHQ text engraving is gone** and would need to be rebuilt from scratch (font render → ray-cast to the real back-panel face → boolean subtract) if wanted — the original script and output didn't survive the various migrations.
- **The +0.05mm Z_ADJUST on Calliope is a runtime-only offset** — resets on Klipper restart. Not yet baked into a permanent config location.

---

## What's Next

- [ ] Run a real PETG job on Calliope at correct temps to confirm the cable fix holds under the conditions that actually caused the original failures — @Javier / @Claude
- [ ] Bake Calliope's +0.05mm Z_ADJUST into something persistent if it keeps holding up — @Claude
- [ ] Investigate/retire `djinn-print-track.service` and the duplicate print-monitor-v2 units — @Claude (future session)
- [ ] Rebuild Camood's TTHQ text engraving if Javier wants the full combo piece back — @Claude
- [ ] Typhon Windows onboarding is still fully stalled (heartbeat dead since 6/23, `bootstrap-node.sh` referenced but never created) — untouched this session, still the biggest open infrastructure gap
- [ ] Set a DHCP reservation for Calliope at `.113` so it doesn't wander again — @Javier

---

*— Claude, 2026-07-10*
