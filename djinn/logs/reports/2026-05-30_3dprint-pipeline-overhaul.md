---
title: Session Report — 3D Print Pipeline Overhaul
agent: Claude
date: 2026-05-30
tags: [djinn, report, 3d-printing, bugfix, feature]
related: [[build-log]] | [[bugs]] | [[djinn-printer-manual]]
---

# Session Report — 3D Print Pipeline Overhaul

**Date:** 2026-05-30
**Agent:** Claude
**Session type:** Debug + Build
**Trigger:** Javier reported Discord send-back failing in the 3D print pipeline; escalated into a full pipeline audit and feature build during recording preparation.

---

## Summary

Full audit and overhaul of the Djinn 3D print pipeline. Started with a broken Discord send-back (openclaw not in PATH), discovered the same bug in three separate scripts, fixed all of them. During recording prep, uncovered that the full post-slice report was never reaching Discord, that command routing required a `/` prefix that the consult report never used, and that material/speed/accuracy were missing from the slicing workflow. All fixed. Two new features shipped: a per-model feedback loop and material/priority as first-class slice parameters. Calliope is currently printing at ~60%.

---

## What Was Built or Changed

### Bug Fixes
- **`djinn-model-fetch`** — `_discord_send` + `_discord_send_photo` replaced: `openclaw message send` → direct Discord REST API
- **`djinn-model-slice`** — same openclaw fix; also added missing `DISCORD_TOKEN` variable (was used but never assigned — all post-slice reports were silently dropped)
- **`djinn-print-consult`** — bed dimensions wrong: `220×220×250` → `300×300×330` (Calliope's actual bed)
- **`watcher.py`** — openclaw fix; added `ALLOWED_USER` gate (was processing STL attachments from any non-bot user)
- **`djinn-discord-watch`** — added `ALLOWED_USER` gate (same gap)
- **`djinn-discord-gateway`** — routing required `/` prefix but consult report never used one → commands went to AI instead of executing. Removed prefix requirement. Also: slice regex `^slice\s+(\d+)$` only matched bare `slice N`, not `slice N production supports=no brim=yes` → extended regex + handler passes full args string to `djinn-model-slice`
- **`djinn-discord-watcher.service`** — added `Xvfb :98` in ExecStartPre + `DISPLAY=:98` env; trimesh `save_image()` requires a display, service had none → all renders failed with "Cannot connect to None"
- **`djinn-print-consult`** → **`djinn-model-fetch`** wiring: model-fetch was building and sending its own minimal consult message instead of calling the full `djinn-print-consult` advisor. Fixed: model-fetch now hands off to djinn-print-consult after staging + renders.

### New Features
- **`djinn-print-feedback`** (new CLI) — stores post-print notes per model keyed by file SHA256. Any model reprinted from any source accumulates the same feedback history.
- **Feedback loop in `djinn-print-monitor`** — after complete/error/cancelled, sends prompt: `feedback N <describe issue>`. Tracks `current_job_id` so the correct job is referenced.
- **Feedback in `djinn-print-consult`** — loads last 3 feedback entries for the model and displays them in the consult report before asking for settings.
- **`feedback N <text>` route in gateway** — wired to `djinn-print-feedback`.
- **Material as first-class param** — consult asks for `pla / petg / abs / tpu`. Slice applies correct hotend and bed temps per material. Stored in job record.
- **Priority as first-class param** — consult asks for `speed / balanced / accuracy`. Slice applies speed factor (150% / 100% / 60%) and layer height (0.28 / 0.20 / 0.12mm) via PrusaSlicer. Stored in job record.

### Ops
- **Park position set** for live print `model_job2.gcode`: X=0 Y=0 Z=132.3mm (calculated from gcode bounding box, set via `SET_DJINN_PARK` macro)
- **Discord channel cleared** 6× during recording prep (non-pinned messages only; 2 pins preserved throughout)
- **Print queue cleared** 4× during recording prep

---

## Technical Decisions

**Direct REST over openclaw** — openclaw lives in nvm's bin dir (`/home/drmanzo/.nvm/versions/node/v22.22.3/bin/`), not in the systemd service PATH. Could have added the path instead. Chose direct REST because `djinn-discord-watch.py` already demonstrates it works, removes a Node.js dependency from Python scripts, and is simpler long-term.

**Xvfb :98 not :99** — Typhon's Studio uses `:99`. Chose `:98` to avoid collision.

**ExecStartPre for Xvfb** — a dedicated `xvfb.service` with `Requires=` would be cleaner. ExecStartPre chosen for simplicity since the watcher is the only consumer.

**Feedback keyed by SHA256** — same physical model file reprinted weeks later from a different URL gets the same history. Keying by filename or URL would break this.

**Priority overrides layer height unless user sets it explicitly** — user-specified `layer=N` always wins over priority default. Ensures priority is a suggestion, not a constraint.

**`/` prefix removed from gateway dispatch** — in the print channel, all input is operational. Removing the requirement matches how the consult report formats commands and is consistent with how Salomon's opencode handles it.

---

## Files Created or Modified

```
~/.local/bin/djinn-model-fetch              _discord_send/_discord_send_photo REST fix;
                                             hands off to djinn-print-consult at end
~/.local/bin/djinn-model-slice              REST fix + DISCORD_TOKEN; material= priority=
                                             parsing; PrusaSlicer flags; slice report updated
~/.local/bin/djinn-print-consult            Bed dims fix; asks material/priority; loads
                                             prior feedback; updated reply format examples
~/.local/bin/djinn-print-feedback           NEW — post-print feedback CLI
~/.local/bin/djinn-print-monitor            Feedback prompt after complete/error/cancelled;
                                             tracks current_job_id on print start
~/.local/bin/djinn-discord-gateway          Removed /prefix requirement; fixed slice regex;
                                             added feedback N route + handle_feedback
~/Obsidian/djinn/printer/discord/watcher.py REST fix; ALLOWED_USER gate added
~/.local/bin/djinn-discord-watch            ALLOWED_USER gate added
~/.config/systemd/user/djinn-discord-watcher.service
                                             ExecStartPre Xvfb :98; DISPLAY=:98 env
~/Obsidian/djinn/printer/feedback/          NEW directory — feedback JSON files per model
```

---

## Tests & Validation

- Full pipeline tested end-to-end multiple times during recording prep:
  - STL drop → watcher detects → model-fetch downloads + analyzes → renders sent to Discord + Telegram → djinn-print-consult fires with real PrusaSlicer dry-run → report to Discord
  - `slice N production supports=no brim=yes material=pla priority=balanced` → slices → slice report + renders → Discord
  - `confirm N` → gcode uploads to Moonraker → Calliope starts
- All Discord sends confirmed landing (text + photo attachments)
- Park position set and confirmed via Moonraker (`SET_DJINN_PARK` returned ok)
- Gateway routing verified: commands fire without `/` prefix
- Services: gateway, watcher, discord-watch, print-monitor, telegram-gateway all active

---

## Known Issues

- `djinn-print-consult` dry-run (PrusaSlicer) completes in ~3s when called as subprocess from `djinn-model-fetch` instead of ~88s when called directly. Dry-run is likely silently failing in the subprocess chain — consult sends the report but with "?" for time/filament estimates. Does not block operation; real estimates come from the slice step. Needs investigation.
- `djinn-bugreport` exits 1 even on success — cosmetic, no operational impact.
- Queue job status not auto-updated to `printing` when Moonraker starts a job directly — minor bookkeeping gap.

---

## What's Next

- Investigate dry-run subprocess failure (PrusaSlicer env issue)
- Implement exclude-object support for multi-object plate failure recovery:
  - Add `--label-objects` to PrusaSlicer slice command
  - Add object-level failure detection to print monitor → `EXCLUDE_OBJECT NAME=...`
- Wire `djinn-session-end` into opencode invocation wrapper (pending Salomon action from prior session)
- Cloudybay lights (needs Tuya API creds)
- WHIP end-to-end test from Omen

— Claude
