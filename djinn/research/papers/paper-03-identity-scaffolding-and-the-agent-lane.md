---
subject: djinn/research/papers/paper-03
tags:
  - research/papers
  - psychology/identity
  - djinn/agents
  - faust/architecture
created: 2026-07-13
source: Perplexity session
---

# Paper 03: Identity Scaffolding and the Agent Lane
## How Personalized AI Roles Reflect and Stabilize the Operator's Self-Concept

---

## Research Question

When a person assigns distinct roles, names, authorities, and behavioral boundaries to AI agents within a personally governed system, what does the structure of those assignments reveal about identity, self-concept, and psychological self-regulation?

---

## Lived Experience / Primary Data

Both Djinn and Faust CLI use named, role-differentiated agents rather than a single monolithic AI. In Djinn, Marcus handles multi-source web synthesis and deep research; Salomon handles tool execution and integrations; Claude handles correlation architecture and pipeline design. In Faust, roles are formalized into a compiled LangGraph state machine: assistant, reasoner, coder, test_proposer, memory_writer, memory_answer, tool_call.

Critically, these are not arbitrary technical labels. The operator governs them explicitly — determining which agent handles which class of problem, which require human approval, and which operate autonomously. The system reflects a deliberate architecture of trust, delegation, and self-extension.

Key data points:
- Marcus in Djinn: described as "perfect for OSINT research" and "multi-source web synthesis" — a research mind the operator trusts for synthesis
- Faust's memory system: deterministic recall for personal facts (name, location, preferences) without LLM inference — the operator's identity stored as explicit contracts, not fuzzy embeddings
- Approval gates in both systems: the operator never surrenders final authority; all consequential actions require explicit confirmation

Primary data sources: Djinn OSINT workspace documentation, Faust_CLI README (design principles section), personal reflection, architectural commit history.

---

## Theoretical Lens

**Narrative Identity Theory** (McAdams, 1993) — identity as a self-authored story that provides unity and purpose across time. Argued here that the agent architecture is a form of externalized narrative structure.

**Self-Concept Clarity** (Campbell et al., 1996) — the extent to which self-beliefs are clearly and consistently defined. The explicit role contracts in the agent system mirror and potentially reinforce self-concept clarity in the operator.

**Micro-Sociology / Symbolic Interactionism** (Goffman, 1959; Mead, 1934) — identity as constructed through social roles and interaction. The agent lanes constitute a micro-social environment in which the operator occupies a consistent role (the operator-authority) while assigning stable roles to non-human interactants.

Key argument: The design of named, role-bounded, operator-governed AI agents is not incidentally psychological — it is structurally isomorphic to the way humans maintain identity through consistent role assignment, narrative coherence, and bounded trust. The system the operator built externally mirrors what healthy self-regulation looks like internally.

---

## Thesis Use

This paper is the bridge between the technical and the clinical. It makes the argument that the psychological health outcomes visible in the operator's development — self-regulation, clear identity, sustained autonomy — are not separate from the system they built but are partially constituted by it. This paper, combined with Papers 01 and 02, forms the core of a masters thesis on self-built AI as psychological infrastructure.

---

## Status

`draft-skeleton` — bones only. Expand with Goffman role theory applied to agent-lane structure and McAdams narrative identity framework in next pass.
