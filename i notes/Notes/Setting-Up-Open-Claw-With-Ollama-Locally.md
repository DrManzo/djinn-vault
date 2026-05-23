---
subject: technology/software-development
tags:
  - ai/models/performance-analysis-ollama-openclaw
created: 2026-05-23
source: Perplexity export

# Setting Up Open Claw with Ollama Locally

## Summary
This note provides a step-by-step guide on setting up an open claw using Ollama and OpenClaw locally, focusing on the installation and configuration of both tools.

## Key Points
- Install Node 24 or Node 22.16+ for OpenClaw.
- Use Ollama as the local LLM server running at `localhost:11434`.
- Run `openclaw onboard --install-daemon` to set up and install OpenClaw with a daemon.
- Verify installation using commands like `openclaw --version`, `openclaw doctor`, and `openclaw gateway status`.

## Details
To set up an open claw using Ollama and OpenClaw locally, follow these steps:

1. **Install Node.js**: Ensure you have Node 24 or a compatible version (Node 22.16+) installed on your system.
2. **Start Ollama**: Run Ollama to start the local LLM server at `localhost:11434`. The API becomes available once Ollama is running, and no authentication is required for local access.
3. **Pull a Model in Ollama**: Use commands like `ollama pull qwen2.5-coder:14b` to download the desired model.
4. **Install OpenClaw**:
   - Option 1 (Recommended): Run `curl -fsSL https://openclaw.ai/install.sh | bash` or `npm install -g openclaw@latest`.
   - Option 2 (Source-based): Clone the repository, run `pnpm install`, and then `pnpm ui:build` followed by `pnpm build` before running `pnpm openclaw onboard --install-daemon`.

5. **Onboard OpenClaw**:
   - Use `openclaw onboard --install-daemon` to configure OpenClaw with the local model.
   - Alternatively, set the model in `~/.openclaw/openclaw.json` after onboarding.

6. **Verify Installation**: Run commands like `openclaw --version`, `openclaw doctor`, and `openclaw gateway status` to ensure everything is working correctly.

7. **Local Architecture**:
   - Ollama runs the model service on `localhost:11434`.
   - OpenClaw runs the gateway/assistant as a daemon.
   - Prompts, skills, and workspace files are stored in `~/.openclaw/workspace`.

8. **Security Considerations**: Tools run on the host for the main session by default; review security settings before opening channels or remote access.

## References
- [Ollama Docs](https://docs.ollama.com/)
- [OpenClaw GitHub Repository](https://github.com/openclaw/openclaw)
- [GitHub Install Documentation](https://github.com/theNetworkChuck/openclaw-setup)

## Related
- [[AI-Assistant-Setup]] — Detailed setup for AI assistants.
- [[Node-JS-Installation-Guide]] — Guide to installing Node.js on different systems.
- [[LLM-Model-Selection]] — Information on selecting and using LLM models.

TAG RULES:
- topic MUST be one of: psychology, law, business, cs, personal, creative
- path: topic/context/relevant/commonality/specific-tag
- 2-4 tags per note, use hyphens not spaces
- You may create new nodes at context level and below
- Existing vault tags for reference: ai/development/fedora/workstation, ai/models/performance-analysis, betrayal/trust, bio.libretexts.org/Bookshelves/Introductory_and_General_Biology/General_Biology_, bio/neuroscience/executive-functions, bio/neuroscience/memories, biology/cell-biology/mitosis, biology/conception, biology/neuroscience/brain-pathways, biology/neuroscience/cerebellum, biology/neuroscience/motor-control, biology/neuroscience/symptoms, business/career-strategies, business/human-resources, business/leadership/critical-thinking, business/llc-formation/california/software-development-company, business/management-methods, business/management-methods/faust-cli-step-10/cli-polish, business/management-methods/faust-cli-step-10/control-loop, business/management-methods/faust/cli/core/adapters, business/management-methods/faust/cli/persistent-context, business/management-methods/faust/cli/review-and-advice, business/marketing-revenue-models, business/marketing-revenue-models/toy-industry, business/passive-income-strategies/neuro-architecture-assets, business/passive-income-strategies/power-user-bluebeam-market, business/project-management, business/project-management/data-models/faust/core/models, business/project-management/modules/roles/faust/cli/adapters, business/project-management/modules/roles/faust/cli/core/adapters, business/project-management/tasks/results/faust/chat, business/strategic-planning, business/technology/integration, business/technology/software-architecture, business/technology/software-development, career/career-factors/growth-opportunities, career/career-factors/income-stability, career/career-factors/job-security, career/career-factors/personality-fit