---
subject: ai/integration/gateway-rules
tags:
  - ai/development/cli
  - djinn/security/rules
  - djinn/gateway/enforcement
created: 2026-06-05
source: Perplexity export

# Phase 1 Deliverables — Djinn Gateway Rules Implementation

## Summary
This note outlines the implementation plan for Phase 1 of the Djinn Gateway rules, focusing on creating a canonical rules document and implementing a Git pre-push hook. The goal is to enforce security policies more effectively while maintaining operational efficiency.

## Key Points
- Canonical rules document (`djinn/GATEWAY.md`)
- Mode file configuration (`~/.config/djinn/session.json`)
- Dev mode CLI tool (`djinn-gateway --dev-session`)
- Git pre-push hook for automated pipeline protection

## Details
Phase 1 aims to address the three main concerns identified in the spec:
1. **Agent Enforcement**: The current enforcement layer only works for Python agents, not Bash or other native tools.
2. **Pipeline Blocking**: Tier 3 blocking wait can freeze pipelines if the agent is unable to communicate with the user.
3. **Scattered Rules**: Existing rules are scattered across multiple files and not consistently followed by all agents.

The implementation plan includes:
- Creating a canonical `GATEWAY.md` document that defines action tiers and rules.
- Introducing a mode file (`session.json`) for different operational modes (Standard/Dev/Restricted).
- Developing a CLI tool to activate Dev mode with an expiry period.
- Implementing a Git pre-push hook to mechanically block pushes outside of Dev mode.

The most valuable single piece is the Git pre-push hook, which ensures that any push attempt is blocked if not in Dev mode. This mechanical enforcement complements the behavioral enforcement (reading `GATEWAY.md`) and provides an audit trail for actions taken by agents.

## References
- [djinn/GATEWAY.md](https://github.com/DrManzo/djinn-vault/blob/main/djinn/GATEWAY.md)
- [session.json schema](https://github.com/DrManzo/djinn-vault/blob/main/djinn/session.json)
- [djinn-gateway CLI](https://github.com/DrManzo/djinn-vault/blob/main/scripts/djinn-gateway)

## Related
- [[djinn/GATEWAY.md]] — Canonical rules document
- [[session.json]] — Mode file schema
- [[djinn-gateway]] — Dev mode CLI tool

---

subject: ai/integration/gateway-rules-phase-2
tags:
  - ai/development/cli
  - djinn/security/rules
  - djinn/gateway/enforcement
created: 2026-06-05
source: Perplexity export

# Phase 2 Deliverables — Djinn Gateway Rules Implementation

## Summary
Phase 2 of the Djinn Gateway rules implementation will focus on creating a proper Python enforcer to handle more complex scenarios and provide a comprehensive audit log.

## Key Points
- `djinn/gateway/` module for Salomon-side orchestrator tools
- Checkpoint flow with Telegram notify + Marcus relay
- Audit log to `djinn/logs/gateway/`

## Details
Phase 2 aims to build on the foundation laid in Phase 1 by implementing a more robust Python enforcer. The plan includes:
- Developing a `gateway` module for orchestrator tools.
- Implementing a checkpoint flow that notifies via Telegram and relays through Marcus.
- Creating an audit log to track all actions taken by agents.

The git hook from Phase 1 will remain as the most valuable piece, providing mechanical enforcement of rules. The Python enforcer will enhance behavioral enforcement and provide detailed logs for auditing purposes.

## References
- [Phase 1 spec](https://github.com/DrManzo/djinn-vault/blob/main/docs/gateway-phase-1.md)

## Related
- [[djinn/GATEWAY.md]] — Canonical rules document
- [[session.json]] — Mode file schema
- [[djinn-gateway]] — Dev mode CLI tool

---

subject: ai/integration/gateway-rules-deliverables
tags:
  - ai/development/cli
  - djinn/security/rules
  - djinn/gateway/enforcement
created: 2026-06-05
source: Perplexity export

# Phase 1 Deliverables — Djinn Gateway Rules Implementation

## Summary
This note outlines the specific deliverables for Phase 1 of the Djinn Gateway rules implementation, including the canonical `GATEWAY.md` document and the Git pre-push hook.

## Key Points
- Canonical `GATEWAY.md` document
- Mode file configuration (`~/.config/djinn/session.json`)
- Dev mode CLI tool (`djinn-gateway --dev-session`)
- Git pre-push hook for automated pipeline protection

## Details
The Phase 1 deliverables are as follows:
- **Canonical Rules Document**: `GATEWAY.md` defines the action tiers and rules.
- **Mode File Configuration**: `session.json` allows different operational modes (Standard/Dev/Restricted).
- **Dev Mode CLI Tool**: `djinn-gateway --dev-session` activates Dev mode with an expiry period.
- **Git Pre-push Hook**: Ensures that any push attempt is blocked if not in Dev mode.

The Git pre-push hook is the most valuable single piece, providing mechanical enforcement of rules. The other components ensure consistent and comprehensive rule adherence across all agents.

## References
- [djinn/GATEWAY.md](https://github.com/DrManzo/djinn-vault/blob/main/djinn/GATEWAY.md)
- [session.json schema](https://github.com/DrManzo/djinn-vault/blob/main/djinn/session.json)
- [djinn-gateway CLI](https://github.com/DrManzo/djinn-vault/blob/main/scripts/djinn-gateway)

## Related
- [[djinn/GATEWAY.md]] — Canonical rules document
- [[session.json]] — Mode file schema
- [[djinn-gateway]] — Dev mode CLI tool