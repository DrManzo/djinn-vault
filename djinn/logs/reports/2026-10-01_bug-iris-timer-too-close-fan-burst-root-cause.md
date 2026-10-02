---
title: Bug — Iris "Timer too close" root cause: overhang-fan M106 bursts saturate Klippy
agent: Claude
date: 2026-10-01
tags: [djinn, bug, iris, klipper, gcode, fan]
related: [[2026-08-16_bug-iris-mcu-timer-too-close-shutdown]] | [[build-log]]
---

# Bug — Iris "Timer too close": overhang-fan M106 bursts saturate Klippy

**System:** Iris (AD5X / zmod / bambufy) + Bambu Studio Iris presets · **Severity:** high · **Status:** fixed (mitigation tool) — closes the 2026-08-16 open bug

## Summary

Both 8/16 shutdowns of `Proxy_Tornado_Recycler.gcode` were caused by the gcode itself: Bambu Studio's overhang fan (`overhang_fan_threshold = 10%`) flipped the part fan between S229.5 (overhang) and S102 (base) on nearly every perimeter segment of the organic geometry. Peak burst: **896 M106 in 5s (~179/s)** — the worst in the file. On Iris every M106 runs two zmod macros (`M106` → `SET_FAN_SPEED`) on a 2-core host. Klippy CPU went 17–21% → 84% → 103% in the last 5s, the 2s stats cadence stretched to 2.4s, then both MCUs shut down with "Timer too close".

## Evidence

- Both attempts died at the same file position: filament_used 9410 / 9454 mm (Moonraker history) → gcode lines 265,274–267,576, layer 100/1097.
- Those lines sit 30–60s (estimated) after the file's single densest fan burst (window starting line 259,840). Same spot, two separate attempts → deterministic, gcode-driven.
- Host memory flat (384 MB avail), MCU srtt flat (1 ms), load avg low — the stall was Klippy's own single-threaded CPU, not memory/network/USB.
- Control: `puffco-710` completed 5h12m on 8/26; its worst burst was 91/s (half the Tornado's).
- Ruled out: G2/G3 arcs (Tornado is 0.3% arcs; puffco-710, which survived, is 44%).
- The 7/20 Kraken_pipe_PLA_3h42m stops (3× at ~14 min) were webhooks emergency_stops, not Timer too close — but that file has the fleet's worst burst (249/s at ~11 min est). Not proven related.

## Fix

`forge/tools/djinn-gcode-fancap` (installed `~/.local/bin/`) extended:
- `--min-interval SEC` — at most one part-fan change per SEC of estimated print time. While held back, the highest requested speed wins (overhang cooling preserved); settles to the last requested speed one interval later. A fan can't physically track >1 change/s, so no cooling is lost.
- `--no-cap` — skip the Calliope S128 cap (Iris has no EMI issue).
- Recomputes zmod's `; MD5:` header (md5 of everything after line 1) when present — zmod deletes files on mismatch. Missing header = warning only (upload adds it).
- `--check-only` now reports the worst 5s burst; exits 1 when it's >2/s.

Verified on the crashed Tornado file: 180,769 → 9,395 fan commands, worst burst 896 → 5 per 5s, all 1,731,189 non-fan lines byte-identical, MD5 valid. Calliope cap-only mode unchanged.

Applied in place (`.bak` kept) to the 7 at-risk files in `~/Desktop/Review/Iris/`; `white block cup` was already fine.

## Not done (Javier's call)

- Iris filament presets (`FLASHFORGE PETG/PLA Basic @Iris`) still have `overhang_fan_threshold = 10%`. Raising to ~50% would cut bursts at the source but changes cooling behaviour — print-quality decision.
- 43 files already on Iris weren't scanned/modified.
- No automatic enforcement: Iris files go from Bambu Studio directly, so `djinn-gcode-fancap --no-cap --min-interval 1.0` must be run before upload.

## Unsafe Shutdown Count (52 → 56) — not a fault

Each increment matches exactly one power-on (8/24, 8/26, 9/4, 10/1). Moonraker counts any power-off at the switch as unsafe. Fix is habit: run zmod's `SHUTDOWN` macro before switching off. Also: Iris has no RTC, clock resets to 2026-01-01 each boot.

## Rule / Lesson

Klipper on weak hosts can't absorb slicer fan-toggle storms; per-second fan command rate is a printer-safety property of the gcode, not just a quality one. Any Iris gcode must pass `djinn-gcode-fancap --check-only --no-cap --min-interval 1.0` before printing.

*— Claude*
