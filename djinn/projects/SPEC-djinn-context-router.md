---
title: "SPEC: djinn-context-router — Selective Vault Context Injection"
status: approved
priority: high
assigned_to: Claude
date: 2026-05-25
tags: [spec, architecture, context-engine, salomon, openclaw]
related: [[BUG-salomon-telegram-tool-overflow]] | [[build-log]] | [[decision-log]]
---

# SPEC: djinn-context-router

## The Problem It Solves

Salomon's workspace files inject **47,920 chars (~11,980 tokens)** into every message — 85% of
qwen2.5:7b's 16,384-token window before a single word of conversation. The model has ~2,320
tokens left to think, call tools, and respond. It can't.

The fix: replace `import *` with selective imports. Each message gets only the vault sections
it actually needs, like importing from specific modules in code.

---

## Architecture

```
Incoming message: "confirm 7"
        ↓
[OpenClaw before_prompt_build hook]  ← integration point, already exists
        ↓
[djinn-context-router]  (Python)
    ├── Fast path: known command → hardcoded tag set (no embedding needed)
    └── Vector path: open query → nomic-embed-text → ChromaDB search
        ↓
[Context assembler]
    → fetch chunks by tag + wikilink
    → trim to 3,000 token budget
    → format as clean markdown
        ↓
[prependContext injected into prompt]
        ↓
qwen2.5:7b: 3K tokens of relevant context + plenty of room to work
```

---

## The Tag / Wikilink Schema

Javier's proposal: wikilinks for subjects, tags for actions. Exact split:

### `[[Wikilinks]]` — Subjects (entities, tools, agents, specialties)

| Link | Refers to |
|------|-----------|
| `[[Calliope]]` | Ender-3 V3 Plus, the 3D printer |
| `[[print-queue]]` | print-queue.json job list |
| `[[djinn-confirm-print]]` | confirm/deny print tool |
| `[[djinn-model-slice]]` | PrusaSlicer wrapper |
| `[[djinn-print-quote]]` | commission pricing tool |
| `[[djinn-model-fetch]]` | model downloader |
| `[[djinn-design]]` | CAD/design orchestrator |
| `[[media-pipeline]]` | full Instagram media workflow |
| `[[djinn-media-ingest]]` | media ingestion agent |
| `[[djinn-media-reel]]` | video export agent |
| `[[djinn-media-publish-prep]]` | caption + publish agent |
| `[[Salomon]]` | local machine (192.168.1.225) |
| `[[Typhon]]` | remote node (192.168.50.113) |
| `[[javier]]` | user profile, preferences |
| `[[vault]]` | Obsidian vault structure |
| `[[lsat]]` | law school / LSAT study |

### `#tags` — Actions (what the user wants to do)

| Tag | Triggers on |
|-----|-------------|
| `#printer` | any 3D printing operation |
| `#confirm` | `confirm N`, `deny N` |
| `#slice` | `slice N` |
| `#quote` | `quote`, `price`, commission pricing |
| `#design` | `design`, CAD generation |
| `#fetch` | model URLs, .stl/.3mf links |
| `#media` | general Instagram/media |
| `#ingest` | `ingest`, `media <path>` |
| `#reel` | `reel`, video editing |
| `#caption` | `caption`, transcript |
| `#publish` | `publish`, posting package |
| `#thumbnail` | `thumbnail` |
| `#hashtag` | hashtag bank operations |
| `#memory` | recall, "what did we decide" |
| `#schedule` | daily plan, time blocks |
| `#law` | LSAT, case analysis |
| `#code` | coding help |
| `#status` | status checks, queue views |

---

## Fast-Path Routing Table

Rule-based matching for known commands — no embedding needed, runs in <5ms:

| Message pattern | Tags | Links | Sections fetched |
|----------------|------|-------|-----------------|
| `confirm N` / `deny N` | #confirm #printer | [[Calliope]] [[djinn-confirm-print]] | confirm tool usage, queue format |
| `slice N [args]` | #slice #printer | [[djinn-model-slice]] [[Calliope]] | slice CLI args, profiles |
| `quote ...` / `price ...` | #quote | [[djinn-print-quote]] | formula, CLI args, tiers |
| `design ...` | #design | [[djinn-design]] [[Calliope]] | design agent commands |
| `<URL>.3mf` / `<URL>.stl` | #fetch #printer | [[djinn-model-fetch]] | fetch command |
| `/3dqueue` | #status #printer | [[print-queue]] | queue JSON path |
| `media <path>` / `ingest` | #ingest #media | [[djinn-media-ingest]] [[media-pipeline]] | ingest command |
| `reel <id>` | #reel #media | [[djinn-media-reel]] | reel command args |
| `publish <id>` | #publish #media | [[djinn-media-publish-prep]] | publish command |
| `callie status` / `print status` | #status #printer | [[Calliope]] | status command |
| greeting / `hi` / short message | (none) | (none) | IDENTITY only (~300 tokens) |

Vector search handles everything else.

---

## Three Components to Build

### 1. `djinn-vault-indexer` (Python)

Scans the vault and workspace, chunks by section, embeds, stores in ChromaDB.

**Inputs:** vault path, workspace path
**Outputs:** ChromaDB collection at `~/.openclaw/context-engine/index/`

Chunking strategy:
- Split on H2 (`##`) and H3 (`###`) headings
- Each chunk = heading + content below it until next heading
- Max chunk size: 800 tokens (~3,200 chars)
- Metadata stored per chunk: `{file, heading, tags: [...], wikilinks: [...], chars}`

Files to index (priority order):
1. `~/.openclaw/workspace/AGENTS.md` — command routing, lane boundaries
2. `~/.openclaw/workspace/TOOLS.md` — tool reference, script paths
3. `~/.openclaw/workspace/USER.md` — Javier's profile
4. `~/.openclaw/workspace/MEMORY.md` — long-term memory entries
5. `~/Obsidian/djinn/printer/` — printer config, queue format
6. `~/Obsidian/djinn/media/` — media pipeline config
7. Key vault notes as needed

Run: `djinn-vault-indexer --all` (full rebuild) or `djinn-vault-indexer --file <path>` (incremental)

### 2. `djinn-context-router` (Python)

Called per message. Returns a markdown context block under a token budget.

```
djinn-context-router "<message>" [--budget 3000]
```

Logic:
1. Try fast path: regex match against routing table → get tag set
2. If no match: embed message via `nomic-embed-text` → ChromaDB top-5 search
3. Fetch matched chunks from index
4. Deduplicate, rank by relevance score
5. Assemble under budget (default 3,000 tokens)
6. Output: markdown string for injection

Target latency: <200ms fast path, <500ms vector path

### 3. Hook integration

**Integration point:** OpenClaw `before_prompt_build` hook

Two options for wiring (investigate at build time, pick whichever works):

**Option A — Shell hook in workspace**
OpenClaw supports workspace hooks via a `hooks/` directory. Create:
`~/.openclaw/workspace/hooks/before_prompt_build.sh`
```bash
#!/bin/bash
MESSAGE="$1"
djinn-context-router "$MESSAGE" --budget 3000
```

**Option B — Enable `active-memory` plugin**
OpenClaw has a bundled `active-memory` plugin (currently disabled) that already hooks
`before_prompt_build` and injects memory context. May be configurable to use our ChromaDB
index. Investigate before building from scratch.

Check: `~/.nvm/versions/node/.../openclaw/dist/extensions/active-memory/openclaw.plugin.json`
for config schema before deciding.

---

## What Changes in the Workspace

### Removed from static injection (moved to dynamic retrieval):
- `TOOLS.md` — 8,021 chars → fetched on demand when a tool command is detected
- `USER.md` — 9,509 chars → fetched when user context is relevant
- `MEMORY.md` — 11,587 chars → fetched when memory lookup is needed

### Stays static (always injected, small enough):
- `IDENTITY.md` — 1,231 chars — who Djinn is, always relevant
- `SOUL.md` — 3,451 chars — behavioral rules, always relevant
- `AGENTS.md` — stays but trimmed to routing rules only (~3,000 chars target)
- `HEARTBEAT.md` — 1,728 chars — machine status, keep for now

**Target after change:**
- Static injection: ~9,400 chars (~2,350 tokens) vs. 47,920 chars today
- Dynamic context: ~3,000 tokens per message (relevant sections only)
- Total overhead: ~5,350 tokens = **33% of window** vs. 85% today
- Salomon's working space: **~11,000 tokens** vs. 2,320 today

---

## Build Phases

### Phase 1 — Foundation (2–3 hours)
- [ ] `pip install chromadb` on Salomon
- [ ] Write `djinn-vault-indexer`
- [ ] Index workspace + key vault files
- [ ] Test retrieval: `djinn-context-router "confirm 7"` → returns Calliope + confirm sections

### Phase 2 — Router (1–2 hours)
- [ ] Write `djinn-context-router` with fast path + vector fallback
- [ ] Validate routing table against all known Salomon commands
- [ ] Benchmark latency

### Phase 3 — Hook integration (1–2 hours)
- [ ] Investigate `active-memory` plugin — use if configurable, build shell hook if not
- [ ] Wire `before_prompt_build`
- [ ] Remove TOOLS.md, USER.md, MEMORY.md from static workspace injection
- [ ] Test end-to-end on Discord: greeting + `/3dqueue` + `confirm N`
- [ ] Monitor: `journalctl | grep systemPromptChars` — target <4,000

### Phase 4 — Tag the vault (ongoing, low priority)
- [ ] Add `#tags` and `[[wikilinks]]` to key TOOLS.md sections
- [ ] Add to MEMORY.md entries for better recall
- [ ] Improves vector search precision over time

---

## What Does NOT Change
- Salomon's `systemPromptOverride` — command routing stays exactly as-is
- All existing scripts (`djinn-confirm-print`, `djinn-model-slice`, etc.)
- Vault structure — tags are additive, nothing gets deleted
- Discord/Telegram channels — transparent to Salomon

---

## Dependencies
- Python 3.x — already installed
- `chromadb` — needs `pip install chromadb` (~50MB)
- `nomic-embed-text:latest` — already running in Ollama
- `requests` — already installed (Ollama API calls)

No LangGraph needed. The graph traversal is handled by ChromaDB similarity search +
the wikilink/tag schema. LangGraph can be added later for more complex multi-hop retrieval.

---

## Decision Log Entry
**Decision:** Build djinn-context-router as a pre-prompt injection layer using ChromaDB +
nomic-embed-text, wired via OpenClaw's `before_prompt_build` hook. Use Obsidian wikilinks
as subject identifiers and #tags as action classifiers.

**Why:** qwen2.5:7b's 16K context window cannot hold all workspace files statically. The
selective import approach mirrors how code imports work — only load what the current call needs.

**Rejected:** Increasing context window to 32K (higher RAM, doesn't fix root bloat problem),
slimming files manually (maintenance burden, loses historical depth), disabling injection
entirely (loses contextual grounding).

— Claude, 2026-05-25
