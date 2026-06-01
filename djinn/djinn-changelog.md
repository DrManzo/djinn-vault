# Djinn Changelog

_Tracks all modifications, additions, and decisions made to Djinn across workspace files, configuration, and infrastructure._

---

## 2026-05-20 — Model Overhaul + Notes Command + Script Production Workflow

### Models Changed (Revision 2 — Tool Support Fix)
- **Correction:** Llama 3.2 Vision 11B doesn't support tool calling — OpenClaw needs tools for agent ops
- **Pulled:** `qwen2.5:7b` (general instruct, tool-capable) — new default primary model
- **New routing:**
  - `qwen2.5:7b` = default daily driver (tools OK, fits VRAM, fast)
  - `llama3.2-vision:11b` = vision specialist only (no tools, on-demand)
  - `phi4:14b` = notes specialist (no tools, on-demand)
  - deepseek-r1:7b = deep reasoning (keep)
  - qwen2.5-coder:7b = code (keep)
  - nomic-embed-text = embeddings (keep)
- **Config fix:** `supportsTools` set correctly per model (qwen2.5:7b=yes, vision=no, phi4=no)
- OpenClaw gateway restarted, confirmed running with `ollama/qwen2.5:7b`
- TUI sessions killed, cache files cleared

---

### Models Changed
- **Pulled:** `llama3.2-vision:11b-instruct-q4_K_M` (7.8 GB) — new daily driver, replaces qwen3.6 + llama3.1:8b
- **Pulled:** `phi4:14b` (9.1 GB) — notes specialist for APA/structured output
- **Retired:** `qwen3.6:latest` (23 GB) — replaced by 11B Vision at 1/3 the size
- **Retired:** `llama3.1:8b` (4.9 GB) — 11B Vision covers everything it did better
- **Kept:** deepseek-r1:7b (deep reasoning), qwen2.5-coder:7b (code), nomic-embed-text (embeddings)
- **Freed disk:** ~28 GB

### Files Created
- **`workflows/notes-command.md`** — 10-step notes pipeline. Trigger: "Djinn, note:" in Telegram. Steps: extract → detect subject → generate title → summarize → grammar fix → tags → APA refs → format markdown → link related notes → save to `i\ notes/Notes/`. Routed to phi4:14b.
- **`workflows/script-production.md`** — 8-step LBlack pipeline with automatic vault search. Step 0: auto-search all vault areas (djinn/, scripts/, references/, i notes/, inbox/). Steps 1-8: Prompt → Draft → Grammar Check (script-check) → Links → Resources (web search) → Research → Review → Final. Each stage saves to corresponding `~/Obsidian/scripts/0N-name/` folder.
- **`~/Obsidian/i\ notes/Notes/`** — output directory for processed notes

### Files Modified
- **`AGENTS.md`**
  - New model routing table: 11B Vision (daily driver) + Phi-4 14B (notes) + DeepSeek-R1 (reasoning) + Qwen2.5-Coder (code) + nomic-embed (embeddings)
  - Added Notes Command section (trigger pattern + workflow reference + phi4 routing)
  - Added Script Production section (trigger + vault search rules + 8-stage pipeline reference)
  - Updated vault directory listing with `i\ notes/Notes/`
- **`TOOLS.md`**
  - Updated model listing with new 5-model setup and descriptions
  - Changed STT from "whisper.cpp (local)" to "voxtype at target/release/voxtype"
  - Added `i\ notes/Notes/` to vault paths

### Key Decisions
- Llama 3.2 Vision 11B as single daily driver (vision + text, fits 8GB VRAM at Q4_K_M)
- Phi-4 14B as on-demand notes specialist (slightly exceeds VRAM, acceptable for async processing)
- Script production vault search is automatic — no ask, just search and use as context
- Notes command is text-only now; voxtype can be wired for voice later
- Workspace state reset to force fresh bootstrap on next session

---

## 2026-05-19 (Part 3) — Timeshift Save Point

### Infrastructure Changes
- **Timeshift snapshot created** — `sudo timeshift --create --comments "Djinn schedule + research workflow system"`
- System state preserved before further changes

---

## 2026-05-19 (Part 2) — Schedule + Research Workflow + 8 AM Cron

### Files Created
- **`~/.openclaw/workspace/SCHEDULE.md`** — Master daily schedule: 7:30 AM (wake) to 1:00 AM (sleep), with AA meeting 9-10 PM on Discord. Blocks: morning ritual, deep work x3, physical, projects, dinner, AA meeting, post-meeting journal, decompress.
- **`~/.openclaw/workspace/workflows/research.md`** — 3-topic research workflow. When triggered: web search 3 sources per topic, create paired notes in `~/Obsidian/i\ notes/Topics/` and `~/Obsidian/i\ notes/Resources/` with Obsidian wiki-links between them.

### Files Modified
- **`~/.openclaw/workspace/AGENTS.md`**
  - Added `SCHEDULE.md` to Session Startup read list
  - Rewrote Daily Plan section:
    - 8 AM cron prompt via Telegram: "What's today's focus? Need me to research anything?"
    - Reads carry-forward from previous day's PLAN.md
    - Generates PLAN.md from Javier's reply mapped into SCHEDULE.md blocks
    - Offers research workflow if Javier indicates interest
  - End-of-Session expanded: now scans **last message** for loose ends/tasks, writes to PLAN.md carry-forward
  - Added `i\ notes/` paths to Obsidian Vault Integration section
  - Added Research Workflow subsection referencing workflows/research.md
- **`~/.openclaw/workspace/TOOLS.md`**
  - Added `i notes` paths to Obsidian Vault section
  - Added SCHEDULE.md reference

### Cron Jobs Created
- **Morning prompt** (`25a700db-47b3-46b9-b9b0-c6054c99adfc`) — daily at 8:00 AM PT, sends Telegram to Javier asking for today's focus + research needs, generates PLAN.md from reply

### Key Decisions
- 8 AM prompt is the single daily planning touchpoint — one message, everything flows from it
- Research workflow uses direct file writes (no external CLI needed) — Djinn has web search + file access
- `notesmd-cli` identified as potential future addition for structured vault operations

---

## 2026-05-19 (Part 1) — Daily Plan System + Discord Fix

### Files Created
- **`~/.openclaw/workspace/PLAN.md`** — Daily plan template. Generated fresh each day on first contact. Sections: Top 3 Priorities, Active Projects Status, Blockers, Schedule, Notes, End-of-Session.
- **`~/.openclaw/workspace/memory/2026-05-19.md`** — First session log. Live documentation of conversation, actions, decisions, and state changes.
- **`~/Documents/djinn-changelog.md`** — This file. Canonical record of all Djinn modifications going forward.

### Files Modified
- **`~/.openclaw/workspace/AGENTS.md`**
  - Added `PLAN.md` to Session Startup read list
  - Added **Daily Plan** section: auto-generate plan on first message of new day, write session log during conversation, end-of-session detection (15min idle or explicit signal)
  - Added **End-of-Session** subsection to Memory: scan session log, update PLAN.md end-of-session section, distill to MEMORY.md
- **`~/.openclaw/workspace/HEARTBEAT.md`**
  - Added "Daily plan" to Things to Check list
  - Added **Daily Plan Check** section: first heartbeat of new day generates plan, stale plan flagging, missed end-of-session recovery
  - Updated heartbeat-state.json schema to include `plan` field
- **`~/.openclaw/workspace/MEMORY.md`**
  - Added 2026-05-19 session entry
  - Updated Active Context with current state (Discord live, plan system live, changelog live)

### Configuration Changes
- **`~/.openclaw/openclaw.json`** — Discord guild config added:
  ```json
  "groupPolicy": "allowlist",
  "guilds": {
    "1504308482575433788": {
      "requireMention": false,
      "users": ["341840772582211587"]
    }
  }
  ```

### Infrastructure Changes
- Discord Message Content Intent enabled in Discord Developer Portal
- Bot re-invited to Djinn OC guild with updated scopes
- Stale OpenClaw sessions wiped, cache cleared, gateway restarted via systemd

### Key Decisions
- Daily plan system: plain markdown (no schemas, no infrastructure) for easy modification
- Session end detection: 15min idle timeout + explicit /end / goodnight
- PLAN.md = forward-looking, memory/YYYY-MM-DD.md = backward-looking
- Scheduling agent deferred to next build cycle
- Obsidian vault sync deferred
- Changelog at ~/Documents/djinn-changelog.md (not in workspace, to avoid clutter)

---

## 2026-05-18 — Djinn Birth

### Files Created
- `~/.openclaw/workspace/IDENTITY.md` — Djinn identity
- `~/.openclaw/workspace/SOUL.md` — behavior rules and boundaries
- `~/.openclaw/workspace/USER.md` — Javier profile
- `~/.openclaw/workspace/TOOLS.md` — environment documentation
- `~/.openclaw/workspace/AGENTS.md` — workspace instructions and memory rules
- `~/.openclaw/workspace/HEARTBEAT.md` — periodic checks
- `~/.openclaw/workspace/MEMORY.md` — long-term memory
- `~/Obsidian/` vault with script production pipeline and djinn subdirectories
- Docker setup for Djinn container
- Forge workspace: lblack, voice-app, djinn-core projects

### Key Decisions
- Djinn is a conciliary, not an assistant
- Local-first, privacy-respecting
- Direct communication, no softening
