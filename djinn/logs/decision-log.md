
## 2026-05-28: Typhon's Studio — Stream Agent Architecture

- **WHIP not a hard blocker for go-live**: Pre-flight warns on no active browser stream but doesn't block — OBS can start and the browser client can reconnect. Only OBS connectivity and stream key are hard blockers.
- **stream_keys.json chmod 600**: Stream keys are disk-persisted (survive restarts) but never in config.py, never in git. File created on first save, locked to owner-read-only.
- **Instagram uses RTMPS URL**: `rtmps://live-api-s.facebook.com:443/rtmp/` — OBS rtmp_custom supports rtmps:// natively, no separate handling needed.
- **go-live routes lighting lock**: StreamAgent.go_live() and end_live() call lighting_agent.lock()/unlock() directly — consistent with manual OBS stream/record routes.
- **PRIMARY_MODEL downgraded**: `phi4:14b` → `qwen2.5:7b` for copilot — phi4 was causing reliability issues; qwen2.5:7b is faster and more consistent for short suggestions.

*— Claude*

## 2026-05-28: Guardian Agent Decisions
- **Poll + broadcast on change** — Guardian polls systemctl every 30s but only WebSocket-broadcasts on state transitions, keeping traffic low. On-demand health_check() always broadcasts.
- **120s restart cooldown** — Prevents restart storms if a service is flapping. Manual API restarts bypass cooldown intentionally.
- **typhons-studio restartable: False** — Backend cannot restart itself; systemd `Restart=on-failure` handles that case.
- **Thread pool for systemctl** — All `is-active` and `restart` calls run in `run_in_executor()` to keep asyncio unblocked during I/O-bound subprocess calls.

*— Claude*

## 2026-05-28: Reporting + Bug Logging Decisions
- **bugs.md as flat index** — single file, one row per bug, machine-readable, links to full reports. Future agents can scan it in seconds to see the failure history of any system.
- **djinn-bugreport as CLI** — any agent can call it from any context (interactive session, automated script, comms-processor). No friction = more likely to actually be used.
- **djinn-session-end for enforcement** — Telegram notification when a session ends without a report. Javier gets notified, which creates accountability without requiring him to audit every session manually.
- **Rule/Lesson field in bug reports** — the point of bug reporting isn't just documentation, it's pattern extraction. One sentence that prevents the class of bug in future is the actual deliverable.
- **Vue 3 rule added to docs** — never prefix a `setup()` return property with `_` or `$`; Vue silently excludes them from the template proxy with no warning in production builds.

*— Claude*

### 2026-05-30 — Direct REST over openclaw for Discord sends (Claude)
Replaced openclaw subprocess calls in djinn-model-fetch, djinn-model-slice, watcher.py with direct Discord REST API. openclaw lives in nvm bin dir not in systemd PATH. Direct REST is simpler and already proven by djinn-discord-watch.

### 2026-05-30 — Feedback keyed by file SHA256 (Claude)
Post-print feedback stored per model by SHA256 hash, not filename or URL. Same physical model reprinted from any source accumulates the same history. Makes the feedback loop source-agnostic.

### 2026-05-30 — Priority overrides layer height unless user specifies (Claude)
priority= adjusts layer height as a default. If user passes layer=N explicitly, that wins. Keeps priority as a suggestion, not a constraint.

### 2026-05-30 — No LLM for style parsing in djinn-model-engrave (Claude)
Keyword parser over LLM. Djinn is near-zero-cost — LLM adds latency and cost for a task simple enough for rules. Apply this to all future tool design: deterministic first, LLM only when genuinely needed.

### 2026-05-30 — Per-component boolean for text meshes (Claude)
OpenSCAD text produces non-manifold merged meshes on complex letters (a, e, o, b). Splitting by connected component and booleing each stroke separately is robust — one failed component warns but doesn't crash the job.

### 2026-05-30 — X-mirror for bottom-face brand mark (Claude)
A makers mark on the bottom face reads backwards when the print is flipped. X-mirror in model space is the correct fix — `shapely_scale(xfact=-1.0)`. No winding fix needed afterward: shapely handles orientation correctly on extrusion.

### 2026-05-30 — No winding fix after shapely X-mirror (Claude)
`cutter.faces[:, ::-1]` after shapely X-mirror + extrusion inverts normals inward. Manifold3d boolean difference then adds material instead of subtracting (negative volume). Shapely mirror already produces correct extrude winding — winding reversal is redundant and harmful.
