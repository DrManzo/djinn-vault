---
subject: djinn/research/request-pa-layer-redesign
tags:
  - research/comprehensive-guide
created: 2026-06-15

# DJINN RESEARCH REQUEST — PA Layer Redesign

## Summary
Claude requested a detailed report on the current state of the DJINN vault and tools, focusing on the PA layer redesign.

## Key Points
- Access to GitHub and full control over all repos in the DJINN vault.
- Need to generate a comprehensive report on the PA layer redesign.
- Research should be conducted in the `research` folder within the DJINN vault.

## Details
The research involves analyzing existing projects, identifying areas for improvement, and documenting findings. The goal is to provide a detailed analysis that can inform future development efforts.

## References

## Related
- [[DJINN-RESEARCH-REQUEST-PALAYER-REDISIGN]] — Detailed report on the PA layer redesign.
- [[djinn-research-request-pa-layer-redesign]] — Original request from Claude.

---

subject: djinn/research/manual-writing
tags:
  - research/documentation
created: 2026-06-15

# MANUAL WRITING — 4 SYSTEMS CHANGED OR BUILT

## Summary
Claude requested user-facing documentation for four systems that were built or changed in the 2026-06-15 session.

## Key Points
- Documenting `djinn-bughunter`, `djinn-webcam-monitor`, `djinn-job-add`, and `forge-slicer`.
- Target audience: Javier, with a direct and technical tone.
- Documentation should follow the style of `DJINN-CLI-MANUAL.md`.

## Details
Each system requires detailed documentation covering its functionality, usage, findings, and state files.

### 1. djinn-bughunter — Proactive Vulnerability Scanner

- **What it scans**: Bandit static analysis, pip-audit CVE scan, secrets regex, journald/tmp error triage.
- **How to run**: `djinn-bughunter --bandit`, `--audit`, `--secrets`, `--errlogs`, `--dry-run`.
- **Findings location**: `djinn/logs/bugs.md`.
- **Deduplication**: State file at `~/.local/share/djinn/bughunter-state.json` with SHA1 hash per finding.
- **Timer**: Fires every hour via `djinn-bughunter.timer`.
- **Scope**: Bandit hits djinn-* Python scripts, pip-audit hits all installed packages, secrets scan hits all of `~/.local/bin`.

### 2. djinn-webcam-monitor — Print Failure Detection + Social Reel Pipeline

- **Camera**: AKASO Brave 4 at `/dev/video2`, Moonraker at `192.168.1.114:7125`.
- **Existing behavior**: Frame diff failure detection, 45-min scheduled 5-min clips, parks printer + alerts on failure.
- **New features**: Milestone clip system (at 1%, 25%, 50%, 75%, 100% of print progress).
- **Milestone clips location**: `~/Videos/print-monitor/jobs/<timestamp>_<jobname>/milestone_XXXpct.mp4`.
- **Post-print behavior**: FFmpeg concatenates all milestone clips into `social_reel.mp4` in the same job dir. Saves `job_meta.json` with filename, start_ts, milestones_hit, reel path.
- **Notifications**: Telegram + Discord message with reel filename and prompt to add cleanup shots to `~/djin`.
- **State file**: `~/.local/share/djinn/webcam-state.json` includes progress, milestones_hit, milestone_clip fields.
- **Service**: `djinn-webcam-monitor.service` (enabled, running).

### 3. djinn-job-add — Print Job Queue Entry + Auto-slice

- **Usage**: `djinn-job-add <model.stl> [--profile proto|production|quality] [--material pla|petg|abs] [--cono] [--qty N] [--notes "..."]`.
- **Default profile**: Production, default material: PLA.
- **New feature**: `--no-slice` flag queues the job without triggering slicing (use when you want to review settings).
- **Without --no-slice**: Calls `djinn-model-slice <job_id> profile=X material=Y supports=Z inline`.
- **Queue file location**: `~/.local/share/djinn/print-queue.json`.
- **Full pipeline**: `djinn-job-add model.stl → auto-slices → gcode in ~/.local/share/forge/gcode/ → upload`.

### 4. forge-slicer + slice.sh — Orca Slicer Migration

- **CLI slicing interface**: `slice.sh <abs_stl_path> <profile: proto|production|quality> <material: pla|petg|abs> [supportsal|tree]`.
- **Returns JSON to stdout**: `{"success": true/false, "gcode_path": "...", "error": "..."}` — or null fields on failure.
- **Orca binary**: `/opt/orca-slicer/AppRun` (AppImage extracted to `/opt/orca-slicer/`).
- **Symlink**: `/usr/local/bin/orca-slicer`.
- **Machine profile**: Built-in Orca Creality Ender-3 V3 Plus 0.4 nozzle profile.
- **Process profiles**: `~/Obsidian/djinn/printer/forge-slicer/profiles/process/` — Calliope-Proto.json, Calliope-Production.json, Calliope-Quality.json.
- **Output**: `~/Videos/print-monitor/ → plate_1.gcode` (Orca always uses this filename — slice.sh renames it to include STL stem).
- **Note**: Orca's JSON output (`result.json`) has triangle_count but print_time_s and filament_g are null — e comments instead.
- **Docker/CrealityPrint pipeline**: Dockerfile and entrypoint.py still in the `forge-slicer` dir.

## References
- [Perplexity](https://www.perplexity.ai/search/b6ad1fa0-34ed-449a-8cdb-816864e4b47a)

## Related
- [[djinn-bughunter-manual]] — Documentation for `djinn-bughunter`.
- [[djinn-webcam-monitor-manual]] — Documentation for `djinn-webcam-monitor`.
- [[djinn-job-add-manual]] — Documentation for `djinn-job-add`.
- [[forge-slicer-manual]] — Documentation for `forge-slicer`.