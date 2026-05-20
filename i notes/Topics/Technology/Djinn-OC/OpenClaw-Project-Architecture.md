---
subject: Technology/AI-Agent-Architecture
tags: [technology, ai-tools, openclaw, ollama, langgraph, agent-design, fedora, homebrew]
created: 2026-05-19
source: Perplexity
---

# OpenClaw Project Architecture

## Summary
Complete architectural blueprint for building a local-first personal AI assistant using OpenClaw, Ollama, and OpenCode on Fedora. Covers installation procedures, multi-agent supervisor patterns, sandboxing strategies, monitoring stacks, and the DjinnOC portable project structure designed for a triple-track student in psychology, computer science, and law.

## Key Points
- OpenClaw is built on LangGraph state machines; workflows are LangGraph by architecture, not an add-on
- Installation requires Node 24 or Node 22.16+, installed via npm or the official install script
- Ollama serves as the local model server at localhost:11434 with no authentication required for local access
- Homebrew installs on Fedora via the official installer script at /home/linuxbrew/.linuxbrew
- Fedora 44 uses dnf5 with lowercase group names (development-tools instead of Development Tools)
- Recommended architecture uses DeepSeek as supervisor agent and Qwen 2.5 Coder as coding specialist
- Three trust zones are required: main assistant (medium risk), coder worker (high risk), ephemeral sandbox (highest risk)
- OpenClaw main session runs tools on host by default; non-main sessions should use Docker sandbox mode
- Self-improvement loop follows inspect-propose-test-approve-apply pattern with mandatory approval gates
- LangGraph provides durable execution, state checkpoints, and human-in-the-loop control for the supervisor pattern
- Monitoring requires four layers: agent behavior (Canary.bot), token/cost tracking (OpenTelemetry), system resources (htop, nvidia-smi, Cockpit), and request/response logs (LangFuse)
- DjinnOC portable structure contains openclaw config, MCP servers, pipelines, vault, reports, sandbox, and scripts directories
- Voice-to-notes pipeline uses Whisper for local transcription into Zettelkasten-formatted Obsidian notes
- Report generation uses python-docx for APA 7th edition .docx output saved to Google Drive
- Google Calendar and Drive MCP servers require OAuth 2.0 credentials from Google Cloud Console
- 32GB RAM supports two 7B-14B models simultaneously with Q4 quantization; GPU VRAM is the limiting factor
- Self-improvement works for code-level changes but cannot replicate frontier model capabilities at this hardware scale
- Claude Pro/Max subscriptions do not provide unlimited API access for external tool integration

## Details
The DjinnOC system is designed as a sandboxed personal assistant with bounded self-maintenance. The supervisor pattern routes tasks between DeepSeek (reasoning, planning, routing) and Qwen 2.5 Coder (code generation, patching, refactoring). All generated code executes in ephemeral Docker containers, with patches written to a staging directory rather than live code.

The portable folder structure at ~/DjinnOC serves as the source-of-truth project, containing OpenClaw configuration overlays, custom LangGraph workflows, Docker sandbox policies, MCP server clones, and automation pipelines for voice transcription, APA report generation, and Obsidian Zettelkasten organization.

Homebrew installation on Fedora requires installing development tools first (sudo dnf group install development-tools), running the official installer, and adding brew to PATH via ~/.bashrc. The installer places Homebrew at /home/linuxbrew/.linuxbrew and uses sudo only during installation.

Ollama can serve multiple clients simultaneously (OpenClaw, coding tools, voice) from a single instance, but RAM and context contention become the primary bottleneck when multiple models stay loaded concurrently.

The monitoring stack enables visibility into tool calls, token consumption, latency per step, estimated cost per session, and hardware resource pressure. Minimum viable setup includes Ollama debug logging, Canary.bot integration, and side-by-side htop/nvidia-smi monitoring.

## References
- OpenClaw. (2026). OpenClaw documentation and installation guide. https://github.com/openclaw/openclaw
- Ollama. (2026). Ollama documentation and model library. https://docs.ollama.com
- LangChain. (2026). LangGraph multi-agent patterns. https://docs.langchain.com/oss/python/langgraph/overview
- Fedora Magazine. (2026). Homebrew on Fedora Linux. https://fedoramagazine.org

## Related
- [[Fedora IDE Setup Guide]]
- [[AI Coding Model Comparison]]
- [[AI Interaction Guidelines]]
- [[Technology-and-AI-Hub]]
- [[AI-Coding-Model-Comparison]]
- [[Faust-Project-Setup-Architecture]]
- [[HERMES Model Framework]]
