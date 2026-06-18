---
title: Bug Report — Discord gateway "build TASK-NNN" routes to Ollama without QUEUE context
system: djinn-discord-gateway
severity: high
status: open (TASK-085 queued)
date: 2026-06-18
---

# Bug — Discord gateway "build TASK-NNN" routes to Ollama without QUEUE context

**System:** `djinn-discord-gateway` (Discord + Telegram gateways)
**Severity:** high (command produces completely wrong output, no indication of failure)
**Status:** open — TASK-085 queued for Salomon

## Root Cause

The gateway has no `build TASK-NNN` command handler. When Javier sent `build TASK-081 TASK-082` via Discord, the gateway fell through to the generic LLM fallback, passing the raw message to a local Ollama model with no system context about what TASK-081 and TASK-082 actually are.

The Ollama model hallucinated plausible-sounding but completely wrong task descriptions ("Refine Djinn's Knowledge Graph", "Develop a Strategic Framework") and signed them as "— Djinn", making them look like legitimate system responses.

## Symptom

```
User: build TASK-081 TASK-082
Bot:  TASK-081: Refine Djinn's Knowledge Graph
      Objective: Enhance Djinn's understanding of Javier's life...
      [hallucinated content signed as — Djinn]
```

No error. No indication the command didn't work. The output looks authoritative.

## Impact

Javier believed the tasks had been executed. They had not. Any "build TASK-NNN" command through the gateway produces silent wrong output until TASK-085 is fixed.

## Fix (TASK-085)

Add a QUEUE-aware `build` command handler to both Discord and Telegram gateways that:
1. Parses `build TASK-NNN [TASK-NNN ...]` from the message
2. Reads the spec block from `~/Obsidian/djinn/communications/QUEUE.md`
3. Passes the actual spec to `opencode` with a non-negotiable prompt
4. Returns opencode's output to the chat

Handler must be registered **before** the generic LLM fallback in the dispatch table.

## Rule Learned

Any command that could silently produce wrong output is worse than a command that fails loudly. Gateway fallback to LLM should never fire for structured commands — either handle it or return "Unknown command: build". The LLM fallback is a last resort, not a catch-all.

*— Claude, 2026-06-18*
