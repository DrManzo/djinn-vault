---
title: Session Report — Discord Print Flow Fix
agent: Claude
date: 2026-06-09
tags: [djinn, report, printing, discord, watcher]
related: [[build-log]] [[decision-log]]
---

# Session Report — Discord Print Flow Fix

**Date:** 2026-06-09
**Agent:** Claude
**Session type:** Debug + Build
**Trigger:** Javier reported three problems: job numbers all over the place, duplicate jobs per file drop, and customer-facing Discord messages asking to "slice N supports=..." which is internal mechanics.

---

## Summary

Fixed three bugs in the Discord → 3D print intake pipeline. The customer-facing flow now goes: drop file → get A/B/C + color prompt → reply "A black" → system auto-slices and queues, customer gets clean "Got it!" message. Created `djinn-model-slice` using PrusaSlicer (OrcaSlicer/CrealityPrint CLI were both broken for headless use).

---

## What Was Built or Changed

- **watcher.py** — Removed `slice N supports=... infill=... brim=...` prompt from customer-facing Discord. Added `_trigger_slice()` which calls `djinn-model-slice` automatically after profile/color confirmed. Added `_tg_alert()` fallback that pings Javier on Telegram if the slice script is unavailable. Job status now advances `needs_settings → confirmed` on reply.
- **djinn-model-fetch** — Added dedup: `add_to_queue()` now checks for existing jobs with same sha256 in pending/confirmed status and returns the existing job_id instead of creating a duplicate.
- **djinn-model-slice (new)** — PrusaSlicer-based headless slicer. Takes job_id from queue, slices with profile-specific settings (standard/production/proto), updates job to `pending`, alerts Javier on Telegram with time/weight.
- **ender3-v3-plus.ini (new)** — PrusaSlicer flat config for Calliope (Ender-3 V3 Plus): correct bed size, nozzle, speeds, temps, PLA density 1.24 g/cm³.
- **print-queue.json** — Archived 9 stale/test jobs (IDs 8-15). Only job 9 (currently printing Camood_TTHQ) kept active. `next_id` reset to 10.

---

## Technical Decisions

**PrusaSlicer over OrcaSlicer/CrealityPrint for headless CLI** — Both flatpak slicers returned `run 2559: process not compatible with printer` on every profile combination tried (user presets, merged presets, no compatible_printers constraint). PrusaSlicer (`/usr/bin/prusa-slicer`) accepts a flat INI config and slices correctly. Tested and producing valid gcode with correct time/weight estimates.

**OrcaSlicer user presets created anyway** — Created `user/default/machine/`, `process/`, `filament/` presets with `"from": "user"` and merged inheritance chains. These don't fix the CLI issue but may help if OrcaSlicer GUI usage is needed later.

**Queue archive instead of delete** — Old jobs moved to `q["archived"]` key rather than deleted. Keeps history accessible for debugging.

**Auto-slice with defaults, no customer input** — After A/B/C + color, slicing fires automatically with sensible defaults (supports from mesh analysis, infill=15%, brim=no). Customer doesn't see any slicer mechanics.

---

## Files Created or Modified

```
~/Obsidian/djinn/printer/discord/watcher.py         ← removed slice prompt, added _trigger_slice + _tg_alert
~/.local/bin/djinn-model-fetch                      ← dedup by sha256 in add_to_queue()
~/.local/bin/djinn-model-slice                      ← NEW: PrusaSlicer-based headless slicer
~/.config/djinn/slicer-profiles/ender3-v3-plus.ini  ← NEW: PrusaSlicer flat config for Calliope
~/.local/share/djinn/print-queue.json               ← queue cleaned, 9 old jobs archived
```

---

## Tests & Validation

- Created synthetic confirmed job, ran `djinn-model-slice 10 supports=no infill=15 brim=no`
- Output: `Sliced OK — 8h 47m 33s, 109.55g` ✓
- Gcode written to `~/.local/share/forge/gcode/cup_engraved_final_job10.gcode` (23MB) ✓
- Print time extracted from `; estimated printing time` comment ✓
- Filament weight extracted via cm³ × 1.24 fallback (PrusaSlicer needs filament_density in config; fixed) ✓
- Watcher restarted clean after watcher.py edit ✓

---

## Known Issues / Caveats

- OrcaSlicer/CrealityPrint CLI slicing still broken — `run 2559: process not compatible with printer`. Root cause unclear (likely profile inheritance not resolved in non-GUI mode). PrusaSlicer is the working fallback.
- `djinn-confirm-print` expects `status == "pending"` — slice script correctly sets this. The Telegram prompt tells Javier to run `djinn-confirm-print N`.
- PrusaSlicer gcode flavor `klipper` — should work with Calliope's Klipper firmware. Not tested on printer yet; verify first print.
- Duplicate detection uses sha256 — files with same content but different URLs are deduped. Intentional for retry scenarios.

---

## What's Next

- [ ] Approve vault push via GATEWAY — @Javier
- [ ] Test full flow end-to-end: drop new file → A black → verify auto-slice fires → `djinn-confirm-print N` — @Javier
- [ ] Verify PrusaSlicer gcode is Klipper-compatible on first print — @Javier
- [ ] Investigate OrcaSlicer headless fix (profile inheritance in CLI mode) — @Claude (optional, PrusaSlicer works)
- [ ] Add `filament_density` to override config when material is PETG/ABS — @Claude

---

*— Claude, 2026-06-09*
