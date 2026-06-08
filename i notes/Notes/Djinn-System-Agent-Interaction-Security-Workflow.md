---
subject: technology/ai/security-workflow
tags:
  - cs/ai/security
  - cs/ai/coding
  - security/guardrails
  - coding/agents
created: 2026-06-07
source: Perplexity export
---

# Djinn System: Agent Interaction & Security Workflow

## Summary
This note outlines the interaction between autonomous coding agents, coding-optimized models, and security guardrails within the Djinn system.

## Key Points
- **IDE Environment:** Agents execute and review code changes directly through Codium.
- **Guardrails:** Enforce strict PII redaction and block prompt-injection attempts before interacting with local coding models.

## Details
The workflow architecture of the Djinn system involves several key nodes:

### Workflow Architecture

```mermaid
graph TD
    %% Nodes
    subgraph Salomon [Salomon: Daily Ops 192.168.1.225]
        Agents[Autonomous Agents: OpenClaw, Claude Code, Hermes]
        IDE[Codium IDE]
        Agents <--> IDE
    end

    subgraph Typhon [Typhon: Storage & Sync 192.168.1.113]
        Vault[Vault: ChromaDB & Markdown]
    end

    subgraph Orin [Orin: Large Models 192.168.1.176]
        LocalModels[Coding-Optimized Models: Gemma 4, MiniMax M3]
    end

    subgraph Security External [Security Guardrails & External Agents]
        Marcus[Marcus: Code Audits & Synthesis]
        Firecrawl[Firecrawl: Secure Web Data]
        Guardrails[OpenRouter Guardrails: PII Redaction & Prompt Injection Blocking]
    end

    %% Connections
    Marcus -->|Audit Findings| Agents
    Firecrawl -->|Sanitized Web Data| Agents
    Agents -->|Data Sync| Vault
    Agents -->|Inference Requests| Guardrails
    Guardrails -->|Routed Requests| LocalModels
```

### Integration Details
- **IDE Environment:** Agents execute and review code changes directly through Codium, bypassing standard Visual Studio Code telemetry.
- **Guardrails:** Outbound traffic routing through OpenRouter enforces strict PII redaction and blocks prompt-injection attempts before interacting with the local coding models on Orin.

## References

## Related
- [[Comparison-Of-Open-Code-Models-For-Coding-And]] — similarity
- [[Faust-Step-10-Operator-Prompt]] — similarity
