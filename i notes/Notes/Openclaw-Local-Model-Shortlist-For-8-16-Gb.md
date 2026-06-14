---
subject: ai/development/faust/cli
tags:
  - cs/software
  - ai/models
  - personal/business
  - performance/memory
created: 2026-06-14
source: Perplexity export

# OpenClaw Local Model Shortlist for 8–16 GB RAM, USB-Portable Setup

## Summary
This note provides a shortlist of local AI models suitable for the OpenClaw project with 8 to 16 GB RAM and a USB-portable setup. The focus is on memory requirements, quantization, and performance metrics.

## Key Points
- **Models**: Qwen3-4B-2507, Qwen3.5-9B, Llama 3.1-8B, Gemma-3-4B
- **Memory Needs**: Fit within 6–10 GB RAM
- **Tool Calling**: Support for tool calling and vision

## Details
For a repeatable, portable OpenClaw benchmark this week, test the following models:
- **Qwen3-4B-2507** (4 billion parameters, Q4_K_M quantization)
- **Qwen3.5-9B** (9 billion parameters, Q4_K_M quantization)
- **Llama 3.1-8B** (8 billion parameters, Q4_K_M quantization)
- **Gemma-3-4B** (4 billion parameters, Q4_K_M quantization)

These models are designed to fit on a fast USB NVMe drive and support tool calling. The benchmark plan involves running the 5-dimensional PinchBench-inspired suite against a fixed 10-task set.

### Candidate Models — Memory, Quantization, and Fit

| Model | Parameters | Quant (rec.) | Disk Size | RAM Needed | Tool Calling | Vision | Best For | Source |
|
---

| --- | --- | --- | --- | --- | --- | --- | --- |
| Qwen3-4B-2507 | 4B | Q4_K_M | ~2.75 GB | 4–6 GB | ✅ | ❌ | Heartbeats, classification, ultra-portable | [microcenter](https://www.microcenter.com/site/mc-news/article/best-local-llms-8gb-16gb-32gb-memory-guide.aspx) |
| Qwen3.5-9B | 9B | Q4_K_M | ~5.5 GB | 8 GB | ✅ | ❌ | **Top 8 GB VRAM coding/agent score** | [localllm](https://localllm.in/blog/best-local-llms-8gb-vram-2025) |
| Llama 3.1-8B | 8B | Q4_K_M | ~4.7 GB | 8 GB | ✅ | ❌ | General-purpose, coding, writing | [kunalganglani](https://www.kunalganglani.com/blog/portable-llm-usb-stick) |
| Gemma-3-4B | 4B | Q4_K_M | ~3.0 GB | 6 GB | ✅ | ✅ | Fast responses, summarization, vision | [kunalganglani](https://www.kunalganglani.com/blog/portable-llm-usb-stick) |
| DeepSeek-R1-0528-Qwen3-8B | 8B | Q4_K_M | ~5 GB | 8 GB | ✅ | ❌ | Reasoning, brainstorming | [microcenter](https://www.microcenter.com/site/mc-news/article/best-local-llms-8gb-16gb-32gb-memory-guide.aspx) |
| Qwen2.5-Coder-14B | 14B | Q4_K_M | ~8 GB | 16 GB | ✅ | ❌ | Serious coding, 16 GB tier | [microcenter](https://www.microcenter.com/site/mc-news/article/best-local-llms-8gb-16gb-32gb-memory-guide.aspx) |
| Gemma-3-12B | 12B | Q4_K_M | ~10 GB | 16 GB | ✅ | ✅ | Chat + vision, 16 GB tier | [microcenter](https://www.microcenter.com/site/mc-news/article/best-local-llms-8gb-16gb-32gb-memory-guide.aspx) |
| Phi-4-Mini | 3.8B | Q4_K_M | ~2.3 GB | 4 GB | ✅ | ❌ | Surprising reasoning for size | [kunalganglani](https://www.kunalganglani.com/blog/portable-llm-usb-stick) |
| Mistral-7B | 7B | Q4_K_M | ~4.4 GB | 8 GB | ✅ | ❌ | Instruction-following, EU langs | [kunalganglani](https://www.kunalganglani.com/blog/portable-llm-usb-stick) |

### USB-Portable Hardware & Software Stack

| Component | Spec | Why |
| --- | --- | --- |
| **Drive** | Samsung T7 1 TB or SanDisk Extreme Pro (USB 3.2 Gen 2, ~1000 MB/s read) | Loads 5 GB model in <8 s; standard flash drives are 4× slower |
| **Format** | exFAT | Cross-platform, no 4 GB file limit |
| **Runtime** | Ollama (installed on each host) | Single `OLLAMA_MODELS` env var redirects model storage to USB |
| **Launcher** | Shell/bat script on USB that sets `OLLAMA_MODELS=/Volumes/Drive/ollama-models` and starts `ollama serve` | Plug-and-play on macOS/Windows/Linux |
| **Host RAM** | 16 GB preferred (8 GB minimum) | 8 GB works but swaps; 16 GB gives headroom for context + OS |

### Repeatable Benchmark Plan

#### Fixed Task Set (10 tasks, 3–5 steps each)

| # | Task | Tools Required | Success Criteria |
| --- | --- | --- | --- |
| 1 | **Email triage** – read 5 mails, flag urgent, draft replies | Email read, LLM classify, Email draft | All 5 classified correctly; drafts need ≤1 edit |
| 2 | **Calendar conflict resolution** – schedule 3 meetings across 2 time zones | Calendar read/write, timezone calc | Zero overlaps; correct local times |
| 3 | **Code refactor** – extract function, add type hints, run tests | File read/write, code exec, test runner | Tests pass; diff <20 lines |
| 4 | **Web research + summary** – find 3 sources, extract key stats, write 150-word brief | Search, browser, file write | All stats cited; no hallucinated numbers |
| 5 | **File reorganization** – move 20 files by type/date, create manifest | FS list/move, JSON write | Manifest matches final tree exactly |
| 6 | **Multi-step data pipeline** – CSV → clean → aggregate → plot → save PNG | Python exec, file I/O | Output PNG renders; aggregates match |

## References
- [microcenter](https://www.microcenter.com/site/mc-news/article/best-local-llms-8gb-16gb-32gb-memory-guide.aspx)
- [localllm](https://localllm.in/blog/best-local-llms-8gb-vram-2025)
- [kunalganglani](https://www.kunalganglani.com/blog/portable-llm-usb-stick)

## Related
- [[Comparison-Of-Open-Code-Models-For-Coding-And]] — similarity
