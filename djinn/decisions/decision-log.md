---
subject: Djinn Operations
tags: [djinn, decisions, log]
created: 2026-05-19
---

# Decision Log

## 2026-05-19: Vault git initialized
- Repo: djinn-vault (private, GitHub)
- Remote: https://github.com/DrManzo/djinn-vault.git

## 2026-05-19: OpenCode configured with Ollama local
- Default model: qwen2.5:7b
- Provider: Ollama (http://localhost:11434/v1)

## 2026-05-19: Three-lane architecture adopted
- Live lane: Ollama qwen2.5:7b
- Dev lane: Claude (Pro subscription)
- Research: Perplexity → vault notes

## 2026-05-20: Claude Lane activated (Phase 5)
- Claude Code CLI installed on Salomon (`~/.local/bin/claude`)
- Claude identity document created: `djinn/Claude.md`
- CLAUDE.md config created at `~/.claude/CLAUDE.md`
- Agent topology updated: opencode (Salomon), opencode (Typhon), Claude (Salomon CLI)
- Signing convention established: `— Salomon`, `— Typhons Forge`, `— Claude`
- Auth: OAuth (Claude Pro) — requires interactive login via `claude` in terminal

## 2026-05-21: Phase 5 Complete — Claude Lane Fully Activated
- Claude.md created at `~/.openclaw/workspace/Claude.md` — defines role, 9-file context protocol, lane boundaries
- AGENTS.md routing table corrected — Role column added, duplicate deepseek row removed, Claude Code architecture row added
- opencode.json updated — temperature settings applied to all 6 models
- Ollama resource caps applied: 60% CPU, 20G RAM, no swap
- Ollama env vars set: MAX_LOADED_MODELS=2, KEEP_ALIVE=5m, GPU_MEMORY_FRACTION=0.80
- djinn-idle.timer active — nightly 22:00 model eviction (deepseek, phi4, coder)
- cpu-governor.service active — powersave enforced on boot (schedutil not available on AMD pstate)
- thermald skipped — Intel-only, AMD pstate handles thermals natively
- Typhon Claude setup: credentials transfer script at `djinn/scripts/typhon-claude-setup.sh`, background watcher running
- openclaw workspace versioned — initial git commit (13 files)
- Handoff package archived: `djinn/communications/djinn-handoff-package.md`

## 2026-05-22: Phase 9 — Printer Node architecture locked

- **Print server**: Creality Nebula pad running Klipper + Moonraker at `192.168.1.113:7125`
- **Decision**: Typhon KIAUH/Klipper install SKIPPED — Nebula pad is already a fully functional Moonraker node, reflashing MCU adds risk with zero benefit
- **Salomon** handles: modeling tools (FreeCAD, Blender, OpenSCAD), AI generation (Hunyuan3D-2), OrcaSlicer slicing, Claude lane work
- **Typhon** handles: Telegram bot daemon (always-on, lightweight, hits Moonraker over LAN)
- **PLR + thermal watchdog**: `plr.cfg` uploaded to Nebula pad — saves Z/layer at each layer change, polls every 5s for temp drops
- **Error logging**: `printer-error-logger.service` running on Salomon — polls Moonraker every 30s, logs to vault
- **idle_timeout**: Changed from 99999999 → 600s on Nebula pad — cat safety, turns off heaters + motors after 10 min idle
- **Printer IP**: Static-lease recommended at 192.168.1.113 — currently DHCP, changed once during this session (.113 → .114)
- **Vault schema**: `djinn/printer/{queue,active,completed,models,config}` active

---

*— Claude*

---

## 2026-05-24 — Six-Agent Manufacturing Stack

**Decision:** Build a modular 6-agent manufacturing pipeline instead of one monolithic print agent.

**Agents:** DesignGenAgent → DesignEditAgent → ProtoOptAgent → DOEPrintOptAgent → PlateNestAgent → FairPrintAgent

**Key choices:**
- Parametric OpenSCAD output (not STL) from DesignGenAgent — dead meshes block downstream editing
- DOEPrintOptAgent uses literature-calibrated prediction models, not test prints — Taguchi factor grid over slicer params (Swansea 2023 baselines)
- phi4:14b as local default brain; Claude API as optional upgrade via `~/.config/djinn/claude.env`
- Shared ProjectState extends existing print-queue.json schema — no separate database
- PlateNestAgent always decimates to <10MB per object before merging (PrusaSlicer >200MB bug)

**Why DOE:** Prototype efficiency optimization is a process/slicer problem, not a geometry problem. Taguchi screening tests multiple factors together and outperforms one-factor-at-a-time when minimizing time+energy+material.

— Claude

---

## 2026-05-24 — 9-Agent Media Stack Architecture

**Decision:** Build a multi-agent Instagram production pipeline with one agent per pipeline stage, not a single monolithic editor agent.

**Agents:** ingest → photo-edit / video-edit → caption → repurpose → thumbnail → qa → publish-prep, orchestrated by content-orchestrator.

**Key choices:**
- All bash-tool agents use qwen2.5:7b (tool support required); publish-prep uses phi4:14b (text quality, no tools needed)
- llama3.2-vision called via HTTP from scripts — not wired as an agent, because it has no tool support and loads 7.8GB on demand
- faster-whisper for caption transcription — voxtype is push-to-talk only, not suitable for batch file processing
- ffmpeg filter chains for color grading — no LUT files, no external dependencies; 4 presets cover the full aesthetic range
- Project manifest.json as shared state — same pattern as manufacturing orchestrator's ProjectState

**Why separate agents:** Each stage has distinct tool dependencies, model needs, and handoff contracts. Separating them makes each agent's workspace instructions lean and unambiguous. Content-orchestrator handles routing without each agent needing to know the full pipeline.

— Claude
- 2026-05-25 — **Creality temp control**: M109 blocked mid-print on Nebula firmware. Use M104 (non-blocking) or native Klipper SET_HEATER_TEMPERATURE instead.
- 2026-05-27 — **machine_limits_usage fix**: PrusaSlicer with `gcode_flavor = klipper` silently fails to emit gcode unless `machine_limits_usage` is set. Added `machine_limits_usage = use_for_slicing` to `~/.config/djinn/ender3-v3-plus.ini`. PrusaSlicer may override this to `time_estimate_only` at load time, which still works.

## 2026-05-27 — Klipper START_PRINT/END_PRINT wired into slicer profile

**Problem:** PrusaSlicer profile had no `start_gcode` or `end_gcode`. Every sliced job got
an inline raw start sequence (G28/M109/M190/purge) that bypassed Calliope's `START_PRINT`
macro entirely — skipping bed leveling, nozzle cleaning, and accurate Z homing.

**Decision:** Set `start_gcode` and `end_gcode` in `~/.config/djinn/ender3-v3-plus.ini`
to call the Klipper macros directly. PrusaSlicer substitutes temperature placeholders.
No per-job post-processing needed.

**Values set:**
```
start_gcode = START_PRINT EXTRUDER_TEMP=[first_layer_temperature] BED_TEMP=[first_layer_bed_temperature]
end_gcode = END_PRINT
```

**Why re-slice, not post-process:** Post-processing a 9.6MB gcode file to splice in
a macro call is fragile — line numbers shift, the inline sequence and the macro both
do homing/heating, risk of double-homing or conflicting temp commands. Re-slicing with
the fixed profile costs 30 seconds and produces a clean, correct file from scratch.

— Claude

## 2026-05-28: manifold3d for boolean CSG — cup engrave
- **Problem:** OrcaSlicer text as separate component on cup surface. trimesh (blender engine), Blender EXACT boolean, and Blender shrinkwrap all failed to produce a clean boolean difference on this geometry — returning empty or degenerated results.
- **Decision:** Use `manifold3d` Python library (3.5.0) for the boolean. Installed in isolated venv at `/tmp/opencode/venv/`.
- **Why:** manifold3d produces watertight, correct boolean output where other engines silently return empty. 0.25 cm³ removed, matches expected text volume. Fast (<5s on 11000-triangle input).
- **Caveat:** Only available in venv, not system Python.
- **Trade-off:** Text is flat (not following cup curvature) → engrave depth varies 2.5mm center / 0.9mm edges. Acceptable for this print.

— Salomon
