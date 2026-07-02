---
title: Session Report — djinn-gcode-sync (Typhon→Salomon gcode handoff)
agent: Claude
date: 2026-07-01
tags: [djinn, report, printer, typhon, gcode-sync]
related: [[machines/TF-TTHQ]] | [[SYSTEM-STATE]] | [[2026-07-01_print-library-migration]]
---

# Session Report — djinn-gcode-sync (Typhon→Salomon gcode handoff)

**Date:** 2026-07-01
**Agent:** Claude
**Session type:** Build
**Trigger:** Following the print library migration, Javier asked to build the actual live
pipeline: getting gcode sliced on Typhon back to Salomon so `djinn-confirm-print` and
`djinn-penelope` can use it, per the earlier architecture decision (direct Tailscale transfer,
Oroborus excluded from the live pipeline).

---

## Summary

Built `djinn-gcode-sync`, a Salomon-side script that pulls new gcode from Typhon's
`C:\Forge\gcode\{calliope,penelope}` over Tailscale SSH every 5 minutes, auto-queues Calliope
jobs into the existing `print-queue.json`/`djinn-confirm-print` pipeline, and lands Penelope
files locally for manual `djinn-penelope upload`. Tested end-to-end with a real file
(SSH listing, scp pull, gcode metadata parsing, queue insertion, idempotency) before wiring it
into a systemd timer. Never uploads or starts a print — Calliope jobs still require the normal
`djinn-confirm-print` auth gate; Penelope files require a manual upload command.

---

## What Was Built or Changed

**`~/.local/bin/djinn-gcode-sync`** (Python, matches `djinn-model-slice`'s style/venv):
- Lists `.gcode` files in Typhon's `C:\Forge\gcode\calliope\` and `...\penelope\` via
  `ssh ... dir /b`.
- Diffs against a local state file (`~/.config/djinn/forge-sync-state.json`) to avoid
  re-pulling/re-queuing the same file twice.
- Pulls new files via `scp` to `~/.local/share/forge/gcode/` (Calliope — same `GCODE_DIR`
  `djinn-model-slice` already uses) or `~/.local/share/forge/gcode/penelope/` (Penelope).
- For Calliope: extracts `estimated printing time` / `total filament used [g]` from the gcode
  comments (same parsing logic and comment format `djinn-model-slice` already uses — Orca's
  output is Slic3r-family, so this works for Typhon-sliced files too) and appends a new
  `pending` job to `print-queue.json` with a fresh `id` from `next_id`. Prints the
  `djinn-confirm-print <id>` command to run next.
- For Penelope: just lands the file and prints the `djinn-penelope upload <path>` command —
  no queue system exists for Penelope, it's driven directly.

**Systemd timer:** `djinn-gcode-sync.timer` / `.service`, 5-min interval, `network-online.target`
dependency, matches the existing `comms-processor`/`forge-sync` pattern. Enabled and running.

---

## Technical Decisions

**Named it `djinn-gcode-sync`, not `djinn-forge-sync` — Why:** a systemd unit called
`forge-sync` already exists (GDrive sync for `~/forge`, the typhons-cyber-forge repo clone) —
different thing entirely. Picked a name with zero ambiguity at the `systemctl --user
list-timers` level rather than relying on the `djinn-` prefix alone to disambiguate.

**Pull-based (Salomon polls Typhon), not push-based — Why:** matches the existing
`comms-processor`/`vault-sync` pattern already used throughout Djinn (a Salomon-side timer
checking a state source), and keeps Typhon's role passive/simple — it doesn't need to know
anything about Salomon's queue format or auth, it just writes gcode to a folder like normal.

**No printer target field added to the job schema — Why:** the existing `print-queue.json`
schema and `djinn-confirm-print` are Calliope-only already (hardcoded Moonraker URL, no
`printer` field anywhere in current jobs). Extending the schema to be printer-aware was out of
scope for wiring up the handoff — Penelope's separate `djinn-penelope` CLI already exists and
doesn't need queue integration to work, so the simplest correct thing was to route Penelope
files around the queue entirely rather than bolt an incomplete multi-printer field onto a
single-printer schema.

**Kept the safety gate intact — Why:** per standing print-authorization rules, nothing in this
tool starts a print or uploads to a live printer automatically. Calliope jobs land as
`pending`, same state `djinn-model-slice` produces locally — `djinn-confirm-print`'s password
prompt is still the only path to an actual upload+print. Penelope files aren't even uploaded to
OctoPrint automatically, just staged locally.

---

## Files Created or Modified

```
~/.local/bin/djinn-gcode-sync                              ← new script
~/.config/systemd/user/djinn-gcode-sync.timer               ← new, 5-min timer
~/.config/systemd/user/djinn-gcode-sync.service             ← new, oneshot
djinn/SYSTEM-STATE.md                                        ← added to Active Services — Salomon table
djinn/logs/reports/2026-07-01_print-library-migration.md    ← marked the gcode-handoff TODO done
djinn/logs/reports/2026-07-01_djinn-gcode-sync.md           ← this report
```

---

## Tests & Validation

- Dry run against empty Typhon gcode dirs — correctly reported nothing new.
- Created a real test gcode file on Typhon (`test_sync_job.gcode`, with realistic
  `estimated printing time` / `total filament used [g]` comment lines) and confirmed:
  - `--dry-run` detected it without pulling.
  - Real run pulled it via scp, queued it as a new job with correctly parsed `1h 30m 0s` /
    `12.5g`, and printed the right `djinn-confirm-print` follow-up command.
  - Re-running afterward correctly reported "nothing new" (idempotency via state file).
- Found and fixed a real bug during testing: `scp` over Windows OpenSSH silently fails
  ("No such file or directory") when the remote path uses backslashes, even though the file
  exists and `ssh ... dir` (which does use backslashes) lists it fine. Fixed by converting to
  forward slashes specifically for the `scp` remote path.
- Triggered the systemd service manually (`systemctl --user start djinn-gcode-sync.service`)
  and confirmed clean execution via `journalctl`.
- Cleaned up all test artifacts (test gcode file on Typhon, test queue entry, test state file)
  before finishing.

---

## Known Issues / Caveats

- Only tested against Calliope's directory in depth; Penelope's path uses the same code path
  but wasn't tested with a real file this session (no test file created there) — logic is
  identical, low risk, but not empirically confirmed the same way Calliope's was.
- If Typhon is unreachable (network down, machine off), the timer will just log "nothing new"
  or fail silently on the SSH call — no alerting is wired up for "sync has been failing for N
  cycles." Worth adding if this becomes load-bearing.
- Filament-gram estimate for `cm3`-only gcode comments uses a rough PLA-density fallback
  (1.24 g/cm³) — inherited as-is from `djinn-model-slice`'s existing logic, not something this
  session touched or improved.

---

## What's Next

- [ ] Slice something real on Typhon (OrcaSlicer or Creality Print) and confirm a genuine
      end-to-end job lands correctly, not just the synthetic test file — @Javier/@Claude
- [ ] Consider alerting if the sync timer goes several cycles without reaching Typhon — @Claude,
      only if this becomes a real pain point
- [ ] Test the Penelope path with a real file — @Claude, next session

---

*— Claude, 2026-07-01*
