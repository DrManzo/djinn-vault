---
title: "PLAN: djinn-context-router — Phase Build Plan"
status: active
date: 2026-05-25
tags: [plan, context-engine, salomon, openclaw]
related: [[SPEC-djinn-context-router]] | [[BUG-salomon-telegram-tool-overflow]]
---

# Build Plan: djinn-context-router

## Context
Salomon's workspace files consume 85% of qwen2.5:7b's 16,384-token window before any message.
Only ~2,320 tokens left. Fix: selective context injection — each message gets only what it needs.

## System Check (2026-05-25)
| Component | State |
|-----------|-------|
| Python venv `djinn-orchestrator` (3.11) | ✅ Ready |
| `nomic-embed-text` via Ollama | ✅ Live, 768-dim |
| `chromadb` | ❌ Not installed (install in venv) |
| `active-memory` plugin (OpenClaw built-in) | ✅ Disabled — injects via before_prompt_build |
| `memory-wiki` plugin (OpenClaw built-in) | ✅ Disabled — Obsidian bridge mode available |
| Context overhead | ❌ 85% / ~14,064 tokens before any message |

## Phase 0 — Try built-in stack first (2h)
**Goal:** memory-wiki + active-memory may already solve this without custom code.
1. Enable memory-wiki in unsafe-local mode → workspace files
2. Enable active-memory with memory-wiki backend
3. Test: greeting + /3dqueue + confirm N
4. Check systemPromptChars in journal — target <4,000
**Decision:** works → skip to Phase 4 | fails → Phase 1

## Phase 1 — Indexer + vector store (2-3h) [if Phase 0 fails]
1. pip install chromadb into djinn-orchestrator venv
2. Write djinn-vault-indexer (H2/H3 chunking, tag/wikilink extraction, nomic-embed-text, ChromaDB)
3. Index workspace + key vault files
4. Smoke test retrieval

## Phase 2 — Router (1-2h) [if Phase 0 fails]
1. Write djinn-context-router with fast path (regex, <10ms) + vector path (<500ms)
2. Fast path covers all Salomon commands
3. Output: markdown context block under token budget

## Phase 3 — Hook integration (1-2h) [if Phase 0 fails]
1. Minimal OpenClaw plugin hooking before_prompt_build
2. Calls djinn-context-router, returns prependContext
3. Remove TOOLS.md, USER.md, MEMORY.md from static injection
4. Keep static: AGENTS.md (trimmed), SOUL.md, IDENTITY.md, HEARTBEAT.md

## Phase 4 — Tag the vault (ongoing)
- Add #tags to TOOLS.md sections
- Add [[wikilinks]] to MEMORY.md entries
- Run djinn-vault-indexer --file after changes

## Tag / Wikilink Schema
**[[Wikilinks]]** — subjects: [[Calliope]], [[print-queue]], [[djinn-confirm-print]],
[[djinn-model-slice]], [[djinn-print-quote]], [[djinn-design]], [[media-pipeline]],
[[Salomon]], [[Typhon]], [[javier]], [[vault]], [[lsat]]

**#tags** — actions: #printer, #confirm, #slice, #quote, #design, #fetch, #media,
#ingest, #reel, #caption, #publish, #thumbnail, #hashtag, #memory, #schedule, #law, #code, #status

## Fast-Path Routing (Phase 2)
| Pattern | Tags | Links |
|---------|------|-------|
| confirm/deny N | #confirm #printer | [[Calliope]] [[djinn-confirm-print]] |
| slice N | #slice #printer | [[djinn-model-slice]] [[Calliope]] |
| quote/price | #quote | [[djinn-print-quote]] |
| design | #design | [[djinn-design]] |
| .3mf/.stl URL | #fetch #printer | [[djinn-model-fetch]] |
| /3dqueue | #status #printer | [[print-queue]] |
| media/ingest | #ingest #media | [[djinn-media-ingest]] |
| greeting/hi | (none) | IDENTITY only |

— Claude, 2026-05-25
