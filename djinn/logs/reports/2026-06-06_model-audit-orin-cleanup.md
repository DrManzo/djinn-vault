---
title: Session Report — Fleet-Wide Model Audit + Orin Cleanup
agent: Claude
date: 2026-06-06
tags: [djinn, report, model-audit, orin, salomon, fleet, routing]
related: [[build-log]] [[INFRASTRUCTURE.md]] [[ROUTING.md]] [[djinn-route]]
---

# Session Report — Fleet-Wide Model Audit + Orin Cleanup

**Date:** 2026-06-06
**Agent:** Claude
**Session type:** Infrastructure + Cleanup
**Trigger:** Javier requested fleet-wide model audit, automated routing, and Salomon cleanup after Salomon hit RAM crisis (qwen3.6 loaded, 550MB free).

---

## Summary

Conducted a complete fleet-wide model audit across Salomon, Typhon, and Orin. Built `djinn-route`, the automated task→model→machine routing script. Connected Orin (iMac, 192.168.1.176) to the Djinn fleet via SSH. Resolved Salomon RAM crisis by removing qwen3.6 (26GB, wrong machine). Identified and removed the only genuine redundancy: `phi4:14b` on Orin (GPU version on Salomon is faster; Orin's 40GB RAM is better reserved for llama3.3:70b + qwen2.5-coder:32b + qwen3.6).

---

## What Was Built or Changed

- **`~/.local/bin/djinn-route`** (Salomon) — NEW. Resolves task type → model → machine → OLLAMA_BASE_URL. 11 task types with Orin-unreachable fallback. Usage: `eval "$(djinn-route code-heavy)"` sets `$OLLAMA_BASE_URL` and `$DJINN_MODEL`. Also supports `--json`, `--model`, `--url`, `--list`.
- **`djinn/ROUTING.md`** — Full rewrite. Added Orin to fleet roster with task mappings, full routing table, djinn-route usage docs, updated escalation path.
- **`djinn/INFRASTRUCTURE.md`** — Added Orin section + network topology ASCII diagram. Updated Orin model list (phi4:14b removed).
- **`~/.ssh/config`** (Salomon) — Added `Host orin` entry for `javiermanzo@192.168.1.176`.
- **`~/.hermes/config.yaml`** (Salomon) — Fixed default model from `nemotron-3-super:cloud` → `qwen3.6:latest`.
- **`~/.hermes/profiles/assistant/config.yaml`** (Salomon) — Created (was empty, causing profile fallback).
- **`~/.hermes/config.yaml`** (Orin) — Updated default model and models list to all 4 current Orin models.
- **`~/.zprofile`** (Orin) — Added PATH export for SSH sessions (Ollama not in default SSH PATH).

---

## Technical Decisions

**phi4:14b removed from Orin** — phi4 is a notes/summary/captions model. Salomon has GPU (RTX 5060); Orin is CPU-only. Running phi4 on CPU is slower than Salomon, and the 9.1GB saved matters when llama3.3:70b (42GB) is Orin's primary purpose. No task in djinn-route routes phi4 to Orin.

**qwen3.6:latest removed from Salomon** — 26GB model on a 29GB RAM machine left 550MB free and 7.5GB swap. qwen3.6 belongs on Orin where it runs as the Hermes agent model. Salomon RAM restored to 14GB free after removal.

**nomic-embed-text kept on all 3 machines** — 274MB, trivial footprint, enables independent embedding on each node. Not redundant.

**Hermes on Orin tried and failed for the audit** — Attempted to use Hermes + qwen3.6 on Orin to do the audit autonomously. Session hit max tokens 3 times with 0 tool calls — model generated text from memory instead of running commands. Audit was executed directly by Claude instead.

---

## Fleet Model State (post-audit)

| Model | Salomon | Typhon | Orin |
|-------|---------|--------|------|
| qwen2.5:7b | ✅ GPU | ✅ | — |
| deepseek-r1:7b/8b | ✅ GPU | ✅ | — |
| qwen2.5-coder:7b | ✅ GPU | — | — |
| qwen2.5-coder:32b | — | — | ✅ CPU |
| phi4:14b | ✅ GPU | — | ~~✅~~ REMOVED |
| llama3.2-vision:11b | ✅ GPU | — | — |
| nomic-embed-text | ✅ | ✅ | ✅ |
| llama3.3:70b | — | — | ✅ CPU |
| qwen3.6:latest | ~~✅~~ REMOVED | — | ✅ CPU |
| mistral:7b | ✅ GPU | — | — |

---

## Files Created or Modified

```
~/.local/bin/djinn-route                             ← new: automated routing script
djinn/ROUTING.md                                     ← rewrite: full fleet routing table
djinn/INFRASTRUCTURE.md                              ← updated: Orin added, model list corrected
~/.ssh/config                                        ← updated: Host orin entry
~/.hermes/config.yaml (Salomon)                      ← fixed: model default
~/.hermes/profiles/assistant/config.yaml (Salomon)  ← created: was empty
~/.hermes/config.yaml (Orin)                         ← updated: model list
~/.zprofile (Orin)                                   ← updated: PATH for SSH
djinn/logs/reports/2026-06-06_model-audit-orin-cleanup.md  ← this report
```

---

## Tests & Validation

- `djinn-route code-heavy --json` → `{"machine":"orin","model":"qwen2.5-coder:32b","url":"http://192.168.1.176:11434"}`
- `ssh orin "ollama list"` → 4 models confirmed (qwen3.6, qwen2.5-coder:32b, llama3.3:70b, nomic-embed-text)
- Salomon RAM: 14GB free, 0 swap after qwen3.6 removal
- Typhon: qwen2.5:7b confirmed present (was missing, pulled)

---

## Known Issues

- Hermes on Orin hits max tokens without calling tools when given open-ended prompts. Use step-by-step forced-tool-use prompts or execute tasks directly. qwen3.6 on CPU generates verbose text responses from memory rather than reading files.
- AGENTS.md was corrupted mid-session by Hermes write_file tool (literal `\n` strings). Fixed via Python replace. Monitor Hermes file writes going forward.

---

## What's Next

- [ ] Wire `djinn/core/llm.py` into scripts that still have inline Ollama client instantiation — @Claude
- [ ] Evaluate whether Typhon needs deepseek-r1:8b or if :7b is sufficient — @Javier
- [ ] Test `djinn-route` integration in a real pipeline script (start with djinn-generate-3d or djinn-ctx-router) — @Claude

---

*— Claude, 2026-06-06*
