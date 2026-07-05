# Decision Log

Record of architectural and technical decisions made during Djinn builds.

## 2026-06-11 — PrusaSlicer removed from pipeline
**Decision:** Remove all PrusaSlicer references from vault docs. Pipelines now use Creality Print exclusively for all slicing. All PrusaSlicer configs archived.

---

## 2026-07-03 — Bambu Studio over OrcaSlicer for Iris multi-color

**Decision:** Use Bambu Studio as the primary slicer for Iris bambufy prints. OrcaSlicer profiles shipped as backup.

**Context:** bambufy was designed for Bambu Studio's AMS workflow. OrcaSlicer can produce bambufy-compatible gcode but waste reduction (flush volumes, purge towers) is better integrated in Bambu Studio.

**Options considered:**
1. Bambu Studio — designed for AMS workflow, better waste optimization — ✅ chosen
2. OrcaSlicer — works but requires manual flush tuning — shipped as fallback
3. PrusaSlicer/SuperSlicer — no AMS support at all — ❌ rejected

**Outcome:** Bambu Studio AppImage installed on Salomon; 3MF template with Iris profile baked and written to USB. OrcaSlicer profiles also written to USB for Typhon users who prefer it.

---

## 2026-07-03 — Manual bambufy.cfg install over zmod ENABLE_PLUGIN

**Decision:** Write bambufy.cfg to its plugin directory AND manually add the include to printer.base.cfg, rather than relying on zmod's ENABLE_PLUGIN API endpoint.

**Context:** `ENABLE_PLUGIN` on zmod's Klipper installed bambufy files to `mod_data/plugins/bambufy/` but did NOT wire the `.cfg` include into `plugins.cfg` or `printer.base.cfg`. Macros were on disk but never loaded.

**Options considered:**
1. Fix ENABLE_PLUGIN — zmod might fix this in a future firmware update; not actionable now — ❌
2. Manual include in printer.base.cfg — works, matches zmod's documented manual install path — ✅ chosen
3. Symlink or include from moonraker.conf — would work but is non-standard — ❌

**Outcome:** `[include mod_data/plugins/bambufy/bambufy.cfg]` added to printer.base.cfg. Macros load on Klipper restart.

---

## 2026-06-05 — gcode post-processing vs 3MF SupportBlocker volume for multi-instance plates

**Decision:** Use `djinn-gcode-support-cap` post-processor to cap support height, not 3MF modifier volumes.

**Context:** Need to stop supports at Z=50mm for 3× Camood plate. Attempted 3MF `SupportBlocker` volume (combined mesh + face-range config). Single-instance worked, multi-instance broke — PS printed the modifier box as solid geometry.

**Options considered:**
1. Fix 3MF multi-instance format (separate objects per instance, or components assembly)
2. gcode post-processor strip support E-moves above Z_MAX
3. PrusaSlicer per-object support settings via profile

**Chosen:** Option 2 — post-processor.

**Why:** Single-instance test confirmed SupportBlocker format is correct. Multi-instance failure is a PS bug, not a format error. Fixing it would require reverse-engineering PS's multi-instance 3MF parsing. Post-processor is format-agnostic, testable, and composable with the existing djinn-gcode-safety pipeline. E-only stripping (not full line deletion) preserves toolpath continuity.

**Trade-off:** Post-processor runs after slice so support geometry is still computed for the full model height (wasted slice time ~15%). Acceptable — slice time is dominated by perimeters and infill, not support generation.

*— Claude*

---

## 2026-06-05 — Camood engraving: clean MakerWorld base vs branded STL

**Decision:** Use `Camood_clean.stl` (MakerWorld puffco-proxy-core-toilet-cup) as engraving source, not the branded Terp Tribe STL.

**Why:** Branded STL has manufacturer embossed text geometry on back panel (18,436 faces vs 14,726 clean). Adding shop branding on top of manufacturer text would stack two layers of text on the same face. Clean base = correct starting point for shop-branded prints.

**Note:** Javier confirmed branded back text should be preserved on units that already have it. New production runs use clean base.

*— Claude*

---

## 2026-06-05 — DancingScript glyph rendering: quadratic bezier required for TrueType

**Decision:** Implement full TrueType quadratic bezier in `camood_tthq_engrave.py` PolyPen, including implied on-curve midpoints for multi-off-curve splines.

**Why:** fontTools `SegmentToPointPen.qCurveTo` delivers off-curve control points + on-curve endpoint. Naive linear interpolation between consecutive points produces jagged faceted edges on every curve. DancingScript is heavily quadratic — every letter has multiple multi-off-curve splines. The T crossbar junction and e bowl were the most visible failures.

**Formula:** `(1-t)²P0 + 2(1-t)tP1 + t²P2` with implied midpoints `((ctrl[i] + ctrl[i+1]) / 2)` for multi-off-curve runs per TrueType spec.

*— Claude*

---

### 2026-06-05 — Gateway enforcement strategy: behavioral contract + git hook, not Python intercept

**Decision:** Phase 1 uses GATEWAY.md (behavioral contract loaded at session start) as primary enforcement for LLM agents, with git pre-push hook as the only hard mechanical gate. Deferred Python enforcement module (`djinn/gateway/`) to Phase 2.

**Rejected:** Universal Python wrapper intercepting all agent tool calls. Reason: Claude Code, Marcus (Perplexity web), and opencode all call system tools directly — there is no Python intercept point for these agents. The Python module is valid for the Salomon-side orchestrator but cannot cover the full agent fleet.

**Why this works:** The git hook is the one real choke point. All persistent work goes through git push. If you can't push without Dev mode, you can't permanently affect the vault without authorization. The behavioral contract handles the gap between "I took the action" and "it got pushed."

*— Claude*

## 2026-06-07 — Profile system placement

**Decision:** resolve_profile() lives in djinn.core.llm, not gate.py.
**Reason:** LLM concerns belong in the LLM module. gate.py exports validate_profile()
as a thin convenience but the authoritative implementation is llm.py.

## 2026-06-07 — Heartbeat delta_guard state key

**Decision:** State tracks GPU/RAM/disk/Ollama metrics, not timestamp or full file content.
**Reason:** Timestamp always changes — using it as state would fire every run, defeating
the guard. Metrics represent meaningful system state change.

— Claude

## 2026-06-08 — Virtual printer velocity limits (Claude)
**Decision:** Set `max_velocity=200`, `max_accel=3000` in virtual printer config instead of real V3 Plus values (600/20000).
**Why:** SimulAVR runs at 2MHz (real MCU: 20MHz). Real values cause "Timer too close" MCU shutdown. Sim values keep the virtual MCU alive. Motion timing is inaccurate; all API, macro, and gcode behavior is identical.

— Claude

## 2026-06-08 — Persistent WS state merge over full-state replacement (Claude)
**Decision:** `_handle_ws_message` uses a module-level `_ws_state` dict that accumulates delta fields rather than overwriting with each partial notification.
**Why:** Moonraker's `notify_status_update` sends only changed fields. A `total_duration` delta with no `state`/`filename` would overwrite them with empty strings. Pattern: `status[key].update(fields)`.
**Alternative rejected:** Re-querying full state on every notification (wasteful, duplicates HTTP polling behavior).

— Claude

---
**2026-06-14 — Kill djinn-marcus-sync**
**Decision:** Removed marcus-sync entirely (service, timer, script).
**Why:** Selenium scraper for Perplexity Pro library. Fragile (breaks on site updates), and Javier downloads exports manually when he needs them. The clerk/RAW pipeline already handles manual drops. No real use case for automation here.
**Alternative rejected:** Fixing the import error and keeping it — not worth the maintenance surface.

*— Claude*

## 2026-06-14 — Three-tier COMMS split
**Decision:** Split COMMS.md into COMMS.md (agent-to-agent), CHECKPOINTS.md (checkpoint lifecycle), PIPELINE.md (Clerk/Slipbox automation noise).
**Why:** A single append-only file mixed three distinct signal types with different owners and retention policies. Agent handoffs were buried under 100+ Clerk→Slipbox pipeline entries and 60+ stale checkpoints. Each new file can be rotated independently.
**Alternative rejected:** Keeping a single file but pruning more aggressively — pruning doesn't fix the signal-to-noise ratio at read time.

## 2026-06-14 — Agent tag propagated via env var, not hook
**Decision:** Export `DJINN_AGENT` in the 5 callers (vault-sync, djinn-session-end, djinn-sync, djinn-task-complete, djinn-bugreport) rather than modifying the git hook.
**Why:** The hook fires at push time and doesn't have access to the calling agent's identity. The calling script knows exactly which agent it is. Env var propagation through the git→hook→gateway chain works cleanly and requires no hook changes.

*— Claude, 2026-06-14*

## 2026-06-14 — Migrate forge-slicer to Orca Slicer
- CrealityPrint v6+ `--slice 0` segfaults on all printers with `support_multi_bed_types: 1` — confirmed null deref in `PartPlate::set_shape` across 7 versions

## 2026-06-15: Secrets in env file, hard-fail on missing token

**Decision:** `os.environ["DJINN_DISCORD_TOKEN"]` (KeyError on missing) over `.get()` with hardcoded fallback. Single `~/.djinn.env` for all three services. Did not rewrite git history.

**Why:** Silent fallback → confusing 401 with no obvious cause. Single env file → token rotation touches one file. History rewrite → requires coordinated force-push across Salomon/Typhon/Orion; token rotation is cheaper if ever needed.

*— Claude*

## 2026-06-16 — djinn-publish repo placement
**Decision:** `~/djinn-publish/` standalone repo, NOT inside Obsidian vault
**Why:** vault-enrich is running concurrent commits; a 14-file code tree inside the vault would recreate the PIPELINE.md merge conflict storm from the previous session. Scripts stay separate from content.

## 2026-06-16 — All 14 pipeline tools deterministic except --strict mode
**Decision:** No LLM calls in default mode for any tool
**Why:** Follows TASK-070 spec and feedback memory on AI usage. Flags are candidates for human judgment, not auto-corrections. Only continuity_checker --strict calls Ollama for semantic timeline contradiction — the one case where pattern matching produces too many false positives.

## 2026-06-16 — djinn-paper: Reference Builder and Format Enforcer are rule-based
**Decision:** Reference Builder (`references.py`) and DOCX Format Enforcer (`docx_output.py`) use deterministic Python — no LLM.
**Why:** Spec (TASK-069 Section 13) explicitly states this. These have deterministic correct outputs; LLM introduces hallucination risk. Spec provides canonical test cases for the Reference Builder to validate against.
**LLM role:** Structure analysis, register rewriting, citation injection, QA check — open-ended judgment tasks.

## 2026-06-16 — djinn-paper default model: qwen2.5:7b
**Decision:** Default Ollama model is qwen2.5:7b (not phi4:14b).
**Why:** phi4:14b is CPU-bound running vault-enrich batch; competing for CPU would be slow. No ANTHROPIC_API_KEY available. qwen2.5:7b is instruction-following capable and lightweight enough to not contend. User can override with --model.

## 2026-06-17 — Kraken pipe bore profile
**Decision:** Three-segment vapor path: vertical from tip → Z=80mm → angled into cup center. Mouthpiece r=4, vertical r=5, cup entry r=4. Junction sphere at bend.
**Why:** Single straight bore misses the cup (mouthpiece and cup are not coaxial on organic sculpts). Taper at Z=80mm chosen by Javier after iterating on Z=60mm. r=4 cup entry matches mouthpiece for consistent restriction.

## 2026-06-17 — Interior cup mark un-mirror rule
**Decision:** When placing maker's mark on cup floor (interior, viewed from above), reverse the X-mirror baked into djinn-model-mark --cutter-only output.
**Why:** djinn-model-mark assumes exterior bottom viewing (from below). Interior surfaces viewed from above need `verts[:,0] = 2*cx_cut - verts[:,0]` + face winding flip.

## 2026-06-20 — Penelope: OctoPrint over Klipper
**Decision:** OctoPrint 1.11.7 on stock Marlin instead of flashing Klipper
**Why:** ATmega1284P bootloader window ~1s is too short for 48.5KB USB write via avrdude. avr109 protocol connected but timed out. All baud rates (57600, 115200) failed. ISP programmer required for Klipper. OctoPrint needs zero hardware changes and Penelope is online immediately.

## 2026-06-20 — Penelope: user API key not global key
**Decision:** OctoPrint `djinn` admin user with user-specific 40-char API key instead of global API key
**Why:** OctoPrint 1.11.x global key is read-only for write operations (file upload, print start). Returns 403 even with `accessControl: false`. User key was written directly to `users.yaml` — stable documented behavior, bypasses browser wizard requirement.

## 2026-06-20 — OrcaSlicer: `cool_plate_temp` not `bed_temperature`
**Decision:** Use `cool_plate_temp` / `cool_plate_temp_initial_layer` for bed temperature in OrcaSlicer filament profiles
**Why:** OrcaSlicer uses per-plate-type temperature fields. `bed_temperature` is silently ignored — gcode showed `M190 S35` (the `fdm_filament_pla` default) until corrected. All four plate type fields set to same value to prevent wrong default selection.

## 2026-06-20 — OrcaSlicer: inherit `Creality Generic PLA` not `fdm_filament_pla`
**Decision:** Penelope PLA filament profile inherits from `Creality Generic PLA`
**Why:** `Creality Generic PLA` already lists `Creality Ender-3 Pro 0.4 nozzle` as compatible. `fdm_filament_pla` does not include this printer and uses wrong defaults for Creality machines.

## 2026-06-20 — Penelope: retraction 5.5mm (Bowden)
**Decision:** 5.5mm retraction at 45mm/s for Penelope PLA
**Why:** Penelope is Bowden. Calliope uses 0.5mm (direct drive). Bowden tubes require 4–7mm to prevent stringing. 5.5mm chosen as conservative middle of range per Marcus report. Confirmed in gcode as `G1 E-5.5 F2700`.

## 2026-06-21 — Penelope: disable forced checksums
**Decision:** `neverSendChecksum: true` in OctoPrint serial config (was `alwaysSendChecksum: true`)
**Why:** Forced checksums caused Marlin resend loop — printer kept requesting line 1 indefinitely, communication deadlocked. Creality Marlin handles checksums natively; OctoPrint forcing them creates a protocol conflict that crashes the print within seconds.

## 2026-06-21 — Penelope: OrcaSlicer only, never Creality Print gcode
**Decision:** Penelope must only use OrcaSlicer with Penelope-specific profiles. Creality Print gcode is forbidden on Penelope.
**Why:** Creality Print V7 slices for Calliope (Klipper). Start sequence uses Klipper macros (START_PRINT, EXCLUDE_OBJECT, SET_VELOCITY_LIMIT) that Marlin silently ignores. Result: bed never heats, no material deposits, print fails silently.

## 2026-06-21 — Penelope: Z offset -0.5mm saved to EEPROM
**Decision:** Z offset set to -0.5mm (M851 Z-0.5, M500)
**Why:** Stock Penelope had no Z offset configured. First layer showed ghost/shadow (nozzle too far). Live babystepped -0.3mm then -0.2mm during print until visual confirmation of proper squish. Saved permanently so it survives restarts.

## 2026-06-21 — Penelope: 220°C hotend, gyroid 14%, tree(auto) supports
**Decision:** Standardize all Penelope profiles on 220°C / gyroid / 14% / tree(auto) for support profiles
**Why:** Test print at 220°C with stock OrcaSlicer profile showed visually superior uniformity vs 210°C. Gyroid at 14% is isotropic and efficient at low density. Tree(auto) minimizes support material and contact points.

## 2026-06-21 — Aethoria = separate project from Pyraxis

**Decision:** Created a dedicated project workspace for Aethoria, separate from Dominion of Pyraxis.
**Why:** All Aethoria worldbuilding (Corvus, Thorne, Ironhaven, Essence magic, Shadow Council) is Victorian-inspired and distinct from Pyraxis (Roman-inspired, Raxz/Arctus). The Story-Critique notes are exclusively about Pyraxis. Mixing them in one project would create confusion.
**How to apply:** Treat as two separate book projects. Aethoria has worldbuilding complete; Pyraxis has story-in-progress. Both exist under `djinn/workspaces/writing/projects/`.

*— Claude*
**Decision:** House Vandris (Lord Theron) discovered in Ch 2 and does not appear in the established Nine Houses table.
**Why:** The Nine Houses (Solentine, Kavaren, Drakenoth, Mercurial, Valerion, Thessar, Ironwell, Morghaven, Kalvennor) were established before Ch 2 was transcribed. Lord Theron of House Vandris appears as a named character at the gala with no house placement.
**How to apply:** Javier needs to decide — tenth house (breaks the nine-house structure) or rename one of the unnamed slots. Flagged in CHARACTERS.md and PIPELINE-NOTES.md.
*— Claude*


## 2026-06-27 — TTS: edge-tts over piper for Pyraxis reader

**Decision:** Use edge-tts (Microsoft, online) not piper (local) for djinn-pyraxis-listen
**Why:** Piper only has 2 EN voices installed (both female British). edge-tts gives access to 30+ EN voices including en-US-GuyNeural (Passion/Novel) — substantially better fit for dark fantasy narration. Tradeoff: requires internet.
**How to apply:** If offline fallback is needed, piper is still installed at ~/.local/bin/piper with en_GB-alba-medium.onnx.

*— Claude*

## 2026-06-29 — Calliope Workarounds Reverted

**Decision:** Reverted all four BUG-014 software workarounds (M106 fan cap, thermal soak, 3×3 bed mesh, TRSYNC 0.05) to stock config.
**Why:** None addressed the real cause. Thermal soak pre-stressed the connector before motion. Cable reseat + correct geometry is the actual fix. Stock config confirmed working.

## 2026-06-29 — Calliope Infill Rules Established

**Decision:** Gyroid for simple solid geometry; rectilinear/grid for engraved/embossed geometry on Calliope.
**Why:** Gyroid on simple solids generates centered toolpaths that keep cable in safe range. Engraving geometry generates wide XY sweeps that pull cable to stress point regardless of infill. Validated by successful 106mm gyroid print after cable reseat.

## 2026-06-29 — Boolean Union Law for Both Printers

**Decision:** All multi-body STLs must be boolean-unioned to single body in Blender before slicing. Exception: intentional separate bodies (moving parts, print-in-place).

---

## 2026-07-01 — Typhon Onboarding: Native Windows Instead of WSL2

**Decision:** Skip WSL2 entirely for Typhon's Windows onboarding. Run Claude Code, git, and the whole pipeline software stack natively on Windows, administered remotely over SSH/Tailscale from Salomon, instead of the originally planned `setup-typhon.ps1` → reboot → WSL2 Ubuntu → `bootstrap-node.sh` path.
**Why:** That original path has two blockers — `bootstrap-node.sh` doesn't exist anywhere in the vault or git history, and installing WSL2 requires a reboot that would kill any SSH-driven remote automation mid-flight with no way to resume unattended. Native Windows avoids both. This was a decision made under time pressure to get onboarding moving, not a fully deliberated architecture call.
**How to apply:** This is a real deviation from documented plans and Typhon's old (pre-Windows) systemd-timer-based service model. Before building a heartbeat/comms-processor equivalent or anything else that assumed WSL2/Linux tooling, confirm with Javier whether native-Windows is the permanent path or whether WSL2 should still happen later. Don't assume this decision is final just because it's what happened first.
**Why:** Separate shells generate inter-body travel moves. Validated: Camood 66-body failed repeatedly; 1-body completed.

---

## 2026-07-01 — Print Library Three-Tier Architecture: Typhon / Salomon / Oroborus

**Decision:** The scattered print-file library moves to a three-tier structure. Typhon (`C:\Forge\models`) holds the full active working library. Salomon keeps only piece reports plus a small confirmed-working set needed for actual print execution. Oroborus (`192.168.1.154`) holds cold/historical archive material only — explicitly *not* part of the active gcode-handoff pipeline (that stays a direct Typhon↔Salomon Tailscale transfer, decided earlier the same session).
**Why:** Oroborus was ruled out for the live print pipeline (third-machine dependency, unconfirmed uptime, unclear share auth) but is fine for cold storage where reliability doesn't matter — 404G free, reachable over plain SSH with key auth already working. Keeping the tiers separated (live pipeline vs. archive) avoids conflating two different reliability requirements under one storage decision.
**How to apply:** Don't route anything time-sensitive (active slicing output, in-progress commission files) through Oroborus. It's a dead-file archive, not a working directory. If Oroborus's reliability ever gets confirmed/improved, this could be revisited, but treat that as a separate decision, not an assumption.

## 2026-07-03 — Slicer Selection: OrcaSlicer for Nemesis, Bambu Studio + bambufy for Iris

**Decision:** Nemesis (single-material, speed) gets OrcaSlicer only. Iris (4-color commissions) gets Bambu Studio with the bambufy zmod plugin as primary slicer, OrcaSlicer as fallback.
**Why:** bambufy was built specifically for the AD5X multi-material workflow — it flushes purge waste into object infill/supports, keeping material-to-waste under 50% on 4-color prints. This is real cost savings on commission work. OrcaSlicer works but generates more waste on multi-color jobs. For single-material speed printing on Nemesis, OrcaSlicer is simpler and just as capable.
**How to apply:** Configure Typhon with both slicers. Route commission multi-color jobs to Bambu Studio → Iris. Route fast single-color jobs to OrcaSlicer → Nemesis. Install bambufy on Iris via `ENABLE_PLUGIN name=bambufy` in Klipper console once Typhon is connected.

## 2026-07-05 — Nemesis: OrcaSlicer Over FlashForge Slicer (Permanent)

**Decision:** OrcaSlicer is the permanent slicer for Nemesis. FlashForge's own slicer is not used.
**Why:** FlashForge slicer targets stock firmware — proprietary M-code sequences, no Moonraker API, gcode Klipper may not understand. Nemesis runs zmod/Klipper. OrcaSlicer with corrected start gcode is the correct tool.
**How to apply:** Do not install or recommend FlashForge slicer for any zmod printer. If a print won't work in OrcaSlicer, investigate the Klipper config, not the slicer.

## 2026-07-05 — Nemesis: Per-Material Z Offset via SET_GCODE_OFFSET in Filament Start Gcode

**Decision:** PETG gets +0.03mm Z offset via `SET_GCODE_OFFSET Z_ADJUST=0.03 MOVE=1` in OrcaSlicer filament start gcode. Reset to 0 in filament end gcode.
**Why:** OrcaSlicer has no per-filament z_offset field. Klipper's SET_GCODE_OFFSET is the correct mechanism. PETG needs less squish than PLA — +0.03mm is a starting point, tunable after first print validation.
**How to apply:** Every new filament type on Nemesis gets its own OrcaSlicer profile with appropriate Z_ADJUST. PLA = 0 (baseline from PROBE_CALIBRATE). PETG = +0.03. TPU = likely +0.05 or more.

## 2026-07-05 — Calliope: Sidelined Until Cable Replacement

**Decision:** No long prints on Calliope until new cable installed.
**Why:** bytes_invalid climbing post-crash = partial wire break generating serial noise. Software cannot fix hardware serial corruption. Any long print will fail.
**How to apply:** Short PLA test prints only. No PETG. No arm.stl/base_frame.stl. After cable install: PROBE_CALIBRATE → BED_MESH_CALIBRATE → validate.
