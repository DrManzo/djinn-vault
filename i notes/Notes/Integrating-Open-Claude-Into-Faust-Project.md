---
subject: business/management-methods/faust-cli-step-12/operator-prompt
tags:
  - cs/software-engineering
  - ai/models/integration
  - business/collaboration-strategies
created: 2026-05-23
source: Perplexity export
---

# Integrating Open Claude into Faust Project

## Summary
The note discusses integrating Open Claude as a co-worker in the Faust project, with the author considering using it more as a consultant rather than a primary workhorse. The roles of each AI tool are defined to avoid chaos and enhance efficiency.

## Key Points
- **Claude (Primary Builder / Co-worker):**
  - Day-to-day coding help.
  - Narrative explanations, system design, step-by-step planning.
  - Use "projects" for persistent context.
  
- **Perplexity ("Marcus") (Consultant / Research and Verification):**
  - High-precision research.
  - Sanity-checking Claude’s plans.
  - Helping with design trade-offs, roadmap, process.

- **Future: OpenClaw / Perplexity Computer:**
  - Orchestrate multiple sub-agents for multi-step tasks.
  - Best used once Faust's architecture and interfaces are stable.

## Details
The workflow involves defining the feature spec, architecture choices, and constraints with Claude. The output is then reviewed by Perplexity to ensure it aligns with external best practices. This setup ensures that Claude handles the "doing" while Perplexity provides critical review and advice.

### Example Workflow on a Faust Feature:
1. **Define Spec and Constraints:**
   - You and the author define the feature spec, architecture choices, and constraints.
2. **Generate Code with Claude:**
   - Claude drafts the code, config, and tests for that feature.
3. **Review Output with Perplexity:**
   - The output is brought back to Perplexity for critique against external best practices.
4. **Tighten Interfaces and Security Assumptions:**
   - Suggest better abstractions or patterns.

### Practical Tips:
- **Maintain a Single Source of Truth:**
  - Keep one "master spec" in the project repository.
  - Load this into Claude’s project and into the current space to ensure both parties are aligned.
  
- **Decide When to Use Each Tool:**
  - Use Claude for active coding, debugging, or long narrative design discussions.
  - Use Perplexity when unsure about Claude's suggestions, needing research on frameworks, security, distributed systems, or law/ethics implications.

### Recommendation:
For the next phase of Faust, bring Claude in as a co-worker and continue using Perplexity for design partnership at the start of each feature and as a reviewer afterward.

## References
- [itchronicles.substack](https://itchronicles.substack.com/p/the-ai-orchestra-how-to-use-chatgpt)
- [youtube.com/watch?v=URBFTwuSRVI](https://www.youtube.com/watch?v=URBFTwuSRVI)
- [dev.to/vtempest/using-claude-perplexity-v0-chatgpt-etc-to-make-tech-apps-and-write-content-4odo](https://dev.to/vtempest/using-claude-perplexity-v0-chatgpt-etc-to-make-tech-apps-and-write-content-4odo)
- [youtube.com/watch?v=GfFsguzaHpI](https://www.youtube.com/watch?v=GfFsguzaHpI)

## Related
- [[Faust-Open-Claude-Consideration]] — similarity 0.82
- [[Faust-Cli-Core-Adapters]] — similarity 0.75
