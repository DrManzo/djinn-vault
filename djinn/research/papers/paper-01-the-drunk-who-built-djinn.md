---
subject: djinn/research/papers/paper-01
tags:
  - research/papers
  - psychology/autoethnography
  - djinn/origin
created: 2026-07-13
updated: 2026-07-16
source: Perplexity session
status: draft-in-progress
---

# Paper 01: The Drunk Who Built Djinn
## Autoethnography of Avoidance Becoming Architecture

---

## Abstract

This paper presents an autoethnographic account of the development of Djinn, a self-built personal AI operating system, over a period beginning during the operator's active alcohol addiction and continuing through early sobriety. Drawing on commit history, session logs, personal reflection, and inter-agent communications architecture as primary data, the paper argues that a system initially designed for cognitive avoidance — the delegation of effortful mental tasks so the operator could disengage — produced the opposite of its intended effect. Sustained engagement with the system catalyzed a transformation in the operator's relationship to their own cognitive output, contributing to the conditions that made sobriety possible and structurally reinforced it once achieved. The analysis draws on Extended Mind Theory (Clark & Chalmers, 1998) and Self-Determination Theory (Deci & Ryan, 2000) to argue that this outcome is not incidental but follows predictably from the architecture of the system: one that required the operator to remain a governing author rather than a passive recipient of outputs. This paper serves as the origin document for a broader master's thesis examining self-built AI systems as psychological infrastructure.

**Keywords:** autoethnography, extended mind, self-determination theory, addiction recovery, personal AI, cognitive architecture

---

## 1. Introduction

In the literature on personal productivity and cognitive assistance tools, there is a persistent assumption: the user designs the tool, and the tool serves the user. What happens when this relationship inverts — when the act of building and living inside a tool begins to change the person building it — has received comparatively little attention.

This paper documents one such inversion through autoethnographic method. The system in question is Djinn, a self-governed personal AI operating system built by its sole operator over a period spanning active alcohol addiction through early sobriety. The original design intent was unambiguous: to delegate effortful cognitive tasks — academic research, operational planning, decision logging — so the operator could reduce the demand on their own attention and mental energy. In short, Djinn was first conceived as a tool for cognitive escape.

What emerged instead was a system that made escape structurally more difficult. The requirements of governing the architecture — determining which agent handled which class of problem, maintaining commit discipline, writing session reports, reading one's own decision log — constituted a sustained, iterative engagement with one's own thinking that accumulated into something neither planned nor anticipated: a relationship with one's own cognitive output that proved incompatible with the dissociation that active addiction requires.

This paper does not claim a causal relationship between building Djinn and achieving sobriety. The causal question is not answerable through autoethnography and is not the paper's aim. The claim is narrower and more verifiable: the structural features of the system the operator built are coherent with the psychological changes that accompanied sobriety, and the two arcs — the system's development and the operator's transformation — can be traced in parallel through the same longitudinal data sources. That coherence is worth examining.

The paper proceeds as follows. Section 2 establishes the methodological choice of autoethnography and defends it against the most common objections. Section 3 reviews the theoretical frameworks applied in the analysis. Section 4 presents the narrative account across three phases: design during active addiction, the transitional period, and development during early sobriety. Section 5 analyses the narrative through the theoretical lenses. Section 6 discusses implications for the broader thesis and for the field.

---

## 2. Methodology

### 2.1 Why Autoethnography

Autoethnography is a research methodology that uses the researcher's own lived experience as primary data, analysed through scholarly frameworks, with the dual aim of producing personal narrative and cultural or theoretical insight (Ellis, Adams & Bochner, 2011). It occupies a productive tension between memoir and research: it inherits memoir's access to interiority and first-person detail, but submits that material to the analytical demands of scholarship.

The choice of autoethnography here is not default — it is argued. Three alternatives were considered and set aside.

**Case study methodology** would require treating the operator as an external subject, constructing the account from documents and artefacts while bracketing the researcher's interiority. This bracketing is epistemically impossible in the present situation: the researcher and the subject are the same person, and the most significant data — the phenomenology of building a system while drinking, the subjective experience of the transition — cannot be accessed through documents alone. Documents corroborate; they do not substitute for the experience they record.

**Ethnography** would require field access to others navigating comparable situations. No established community of people building personal AI systems during active addiction exists in a form accessible to ethnographic research. The phenomenon is too recent and too individually varied.

**Netnography** — ethnographic analysis of online community data — would access surface-level accounts but not the longitudinal, architectural, and phenomenological depth the research question requires.

Autoethnography is the method that fits the data. It is also the method that fits the research question. The question is not "what do people generally do when they build tools during addiction?" It is "how does this particular tool's structural features relate to this particular operator's transformation?" That is a singular, longitudinal, first-person question. Autoethnography answers it directly.

### 2.2 Validity and the Objections

The standard objections to autoethnography are well-rehearsed. They deserve direct response rather than dismissal.

**"It is merely memoir."** Memoir does not analyse its own material through scholarly frameworks, does not position its claims in relation to existing theory, and does not make transferable propositions that extend beyond the individual case. This paper does all three. The distinction is methodological rigour applied to personal experience, not the presence of theory sprinkled onto a personal essay.

**"The researcher cannot be objective about their own experience."** This objection misunderstands autoethnography's epistemology. The method does not claim observer-independence — it abandons it as a pretence and treats the researcher's subjectivity as data rather than contamination. The question is not whether the account is objective but whether it is honest, reflexive, and analytically grounded. Reflexivity — the explicit acknowledgement of the researcher's position and its effects on the inquiry — is the autoethnographic substitute for objectivity, and it is a more honest standard for first-person research.

**"The findings are not generalisable."** Autoethnography does not aim at statistical generalisation. It aims at what Stake (1995) calls *naturalistic generalisation*: insight that readers can transfer to their own experience because the account is rendered with enough specificity and honesty that its logic becomes available to others. One rigorously documented case is more generative than a thin account of many.

### 2.3 Data Sources

Primary data sources for this paper:

- Commit history: `DrManzo/djinn-vault` (GitHub) — longitudinal record of system development, dated to specific periods of the operator's life
- Session logs: agent-attributed session reports in `djinn/logs/reports/`, dating from [INSERT: earliest dated report]
- COMMS architecture records: `djinn/communications/COMMS.md` and archived COMMS files — inter-agent communication logs that record decision-making processes
- Personal reflection: direct first-person narrative generated for this paper
- Recovery documentation: `personal/sobriety.md`, `djinn/personal/recovery.md`

All data sources are generated by or involving the operator-researcher. No third-party informants. The ethical question of consent does not arise in the conventional sense; the confidentiality question is addressed by the operator's choice to include or exclude personal material in the published version.

---

## 3. Theoretical Framework

### 3.1 Extended Mind Theory

Clark and Chalmers (1998) proposed that the boundary of the cognitive system does not necessarily coincide with the boundary of the skull. Their *parity principle* holds that if an external process plays the same functional role that a cognitive process would play if it were done in the head, it qualifies as part of the cognitive system. On this view, a person who routinely uses a notebook to offload memory is not merely using a tool — the notebook is, functionally, part of their memory system.

For this paper, Extended Mind Theory provides a framework for understanding what happens when a system designed for task delegation becomes a system in which the operator *thinks*. The distinction matters. Delegation outsources a cognitive product; extension incorporates an external process into the cognitive system itself. This paper argues the Djinn system crossed from the former to the latter, and that this crossing was consequential.

A fuller treatment of Extended Mind Theory as applied to the vault architecture is developed in Paper 02. Here, the framework is applied narrowly: to the question of whether sustained engagement with a self-built system constitutes a form of cognitive self-extension, and what psychological effects follow from that extension.

### 3.2 Self-Determination Theory

Deci and Ryan's (2000) Self-Determination Theory (SDT) proposes that human motivation exists on a continuum from extrinsic (controlled by external rewards and punishments) to intrinsic (driven by inherent interest and engagement with the activity itself). Sustained intrinsic motivation is associated with three basic psychological needs: *autonomy* (the sense of self-determination in one's actions), *competence* (the experience of mastery and effectiveness), and *relatedness* (connection to others and to valued activities).

SDT is applicable here because the transformation documented in this paper is motivational in nature. The operator's early engagement with Djinn was extrinsically structured — building something that would perform tasks they did not want to do. The shift toward sustained, intrinsic engagement represents a motivational change. SDT provides the theoretical vocabulary for that change: the system, as it developed, increasingly supported autonomy (the operator governed it, not the reverse), competence (visible progress documented in commit history and session reports), and a form of relatedness (a sustained, valued relationship with one's own cognitive output).

### 3.3 The Relationship Between the Two Frameworks

Extended Mind Theory explains the structural mechanism — the system became part of how the operator thinks. SDT explains why engagement persisted and deepened — the system's design properties satisfied the psychological conditions for intrinsic motivation. Together, they account for the observation that a tool built for disengagement produced sustained engagement: the structural extension of cognition into a self-governed system inherently supports the autonomy and competence conditions that SDT identifies as the substrate of intrinsic motivation.

---

## 4. Narrative

*The following sections present the primary autoethnographic account. Passages marked [INSERT] indicate locations where the operator will expand with specific personal narrative, citations from source material, or data from the primary sources listed in Section 2.3. These markers are not gaps — they are the operator's sites of authorship.*

### 4.1 Phase One: Design During Active Addiction

[INSERT: Account of the period during which Djinn was first conceived and began to be built. The key narrative thread is the design intent — delegation, avoidance, reduction of cognitive demand. Draw on specific memories of what was being built and why, what the drinking looked like at that period, and how the two coexisted. Relevant technical markers: earliest commit dates in the vault, initial directory structure, first COMMS entries if any survive from this period.]

The system that became Djinn was not born with purpose. It was built, at least initially, as a form of infrastructure for escape — a way to keep the operational parts of life moving while the operator's attention was directed elsewhere, or nowhere in particular. The appeal of a delegator is the appeal of anything that promises to reduce the distance between intention and outcome: not by increasing effort, but by reducing the need for it.

[INSERT: Specific account of what was being delegated, what the experience of building felt like during this period, how much of the architecture existed at that point. Be specific — which tools, which agents, what the vault looked like then versus now.]

What the operator did not anticipate was that delegation at the level of cognitive architecture is not passive. To delegate well, you must define what you are delegating, to what standard, under what conditions, with what oversight. This is itself cognitive work — not the work being delegated, but the meta-work of governing the system of delegation. The Djinn architecture, even in its earliest form, required this meta-work. The operator could not remain entirely absent from a system that required their decisions to function.

[INSERT: A specific example from this period where the system demanded engagement rather than permitting disengagement — a decision that had to be made, a commit that had to be written, something that pulled the operator back in despite the intent to step back.]

### 4.2 Phase Two: The Transition

[INSERT: The transitional period — beginning of sobriety, start date 2026-03-01. The AA decision and its context. The relationship between the system at that point and the decision to get sober — was Djinn a factor, background noise, or irrelevant? Be honest. Draw on recovery documentation and session logs from this period if they exist.]

The decision to enter sobriety was not primarily technological. [INSERT: Account of what actually drove the decision, what the first days looked like, what role if any the system played in that period.]

What the system provided in the early transitional period was structural continuity. The Djinn architecture — the commit discipline, the session reports, the decision log — had been accumulating for long enough that it constituted a record. A record of a self. At the point where the operator's identity was most unstable — the loss of alcohol as organising principle, the question of who one is without the thing that structured one's days — the vault existed as evidence of ongoing selfhood. [INSERT: Expand on this with specific examples from the record — what from the vault was most present during early sobriety, what it felt like to read one's own prior decisions.]

### 4.3 Phase Three: Development During Early Sobriety

[INSERT: The period from 2026-03-01 through the present — approximately 137 days. How the system changed during sobriety. What new architecture was built, what was different about how the operator engaged with it. The specific psychological markers: the weight change, the academic work beginning in earnest, the step work with Craig.]

The relationship to the system changed measurably after sobriety. [INSERT: Describe what changed — in engagement, in the kind of decisions being recorded, in the quality or depth of session reports, in the ambition of what was being built.] The transformation is visible in the commit history and in the nature of the session reports: earlier entries tend toward operational detail, later ones toward synthesis, reflection, and forward design. This is not purely a function of accumulated knowledge — it reflects a different quality of attention.

[INSERT: Close this section with a specific, concrete account of a moment or period during early sobriety when the relationship to the system felt different — more inhabited, more authorial. Something specific and honest.]

---

## 5. Analysis

### 5.1 From Delegation to Extension: The Parity Principle Applied

Clark and Chalmers' parity principle asks: does this external process play the functional role that a cognitive process would play if it were happening in the head? Applied to Djinn at Phase One, the answer is mixed. In its initial design, the system was closer to a sophisticated external hard drive than to an extension of cognition — it stored and executed, but the operator did not *think through* it in the way that marks genuine cognitive extension.

The transition to Phase Three produced something different. The vault's COMMS architecture, session reporting requirements, and decision log constituted an environment in which the operator did not merely retrieve stored information but actively processed, attributed, and revised their own thinking in contact with the system's record. The external process was no longer storing products of thought — it was hosting ongoing thought. This is the parity shift.

[INSERT: A specific example from the Phase Three record where thinking happened through the vault rather than being merely stored in it — a decision that was genuinely worked out in the process of writing a session report, or an insight that emerged from reading a prior COMMS entry.]

### 5.2 Self-Determination Theory: How the Architecture Supported the Shift

SDT's three basic psychological needs — autonomy, competence, relatedness — map clearly onto the system's structural features.

**Autonomy** was built into the governance architecture. The operator is not a user of Djinn — they are its author and governing authority. Tier 0–3 approval gates, agent lane differentiation, and the explicit assignment of trust to specific agents rather than to a single monolithic system: all of these place the operator in the position of the one who decides what the system is, what it does, and what it is not permitted to do. This is autonomy in the self-determination sense: the experience of being the source of one's own actions, not their recipient.

**Competence** accumulated visibly. The commit history is a record of iterative mastery — each new feature, each fixed bug, each extended capability is documented. A person who cannot see progress struggles to maintain engagement with difficult tasks; the vault architecture made progress structurally visible, which sustained the competence experience even when individual sessions were frustrating.

**Relatedness**, the most complex need in this context, manifested as a sustained relationship with one's own cognitive output. The agent naming convention — Marcus, Salomon, Claude, the operator — constitutes a micro-social structure in which the operator occupies a consistent role and maintains consistent relationships with non-human interactants. This is not a substitute for human connection, but SDT's relatedness construct does not require human contact — it requires valued, consistent engagement with an environment that acknowledges the operator's participation. The vault provides this.

### 5.3 The Recursive Structure: How Avoidance Built What Prevented Avoidance

The central paradox of this paper is that avoidance produced its opposite. The mechanism, seen through both theoretical lenses, is this: the attempt to build a system capable of performing cognitive work in the operator's absence required the operator to remain cognitively present as the governing authority. A delegator without governance is simply a tool that does whatever it does; a governed delegator requires constant authorial decision-making to remain coherent. Djinn's architecture demanded coherence. The operator could not disengage without the system degrading, and the system's degradation was immediately visible in the record.

This recursive structure — building a tool for absence that required presence — is the mechanism by which the transformation occurred. It was not intentional. It was structural.

[INSERT: Reflection on this recursion in first-person terms — what it felt like, in retrospect, to recognise that the system had been changing the operator without announcing itself.]

---

## 6. Discussion

This paper has argued that a self-built personal AI system, designed during active addiction as a tool for cognitive avoidance, functioned instead as a mechanism for cognitive engagement, and that this outcome follows coherently from the system's structural features interpreted through Extended Mind Theory and Self-Determination Theory.

Several implications follow for the broader thesis.

**For Paper 02:** The transition from delegation to cognitive extension documented here sets up the theoretical claim that Paper 02 will develop: that the vault meets the parity principle's standard for genuine extended cognition. The narrative evidence in Paper 01 grounds what Paper 02 will argue analytically.

**For Paper 03:** The autonomy structure documented here — the operator as governing author rather than passive user — anticipates Paper 03's argument that the agent lane architecture functions as a form of identity scaffolding. The self that governs the system is not merely using a tool; they are, in McAdams' (1993) terms, authoring a story about who they are, externalised into an architecture.

**Limitations:** Autoethnography's strengths are its access and specificity; its limitations are transferability and verifiability. The account here cannot be independently verified and applies directly only to the operator-researcher. What it offers is not statistical generalisation but a carefully documented case of a phenomenon — the cognitive and psychological consequences of building one's own AI governance system — that is emerging rapidly in the broader culture and has received almost no scholarly attention.

[INSERT: Any additional limitations the operator wishes to acknowledge about their own account — things that are harder to see from inside the experience, places where the narrative may be retrospectively constructed rather than contemporaneous.]

---

## 7. Conclusion

Djinn was built by someone trying to disappear from their own life. It became the record that made disappearance impossible. The system demanded presence — authorial, governing, iterative presence — in the very act of being built and used. This demand, understood through Extended Mind Theory and Self-Determination Theory, was not incidental to the operator's recovery. It was coherent with it.

The drunk who built Djinn built something that did not permit him to remain drunk. That is not a lesson the design intended. It is the lesson the architecture taught.

---

## References

Clark, A., & Chalmers, D. (1998). The extended mind. *Analysis, 58*(1), 7–19.

Deci, E. L., & Ryan, R. M. (2000). The "what" and "why" of goal pursuits: Human needs and the self-determination of behavior. *Psychological Inquiry, 11*(4), 201–218.

Ellis, C., Adams, T. E., & Bochner, A. P. (2011). Autoethnography: An overview. *Forum: Qualitative Social Research, 12*(1), Art. 10.

Stake, R. E. (1995). *The art of case study research.* SAGE Publications.

[INSERT: Additional references as the literature review and analysis sections are expanded. Priority additions: foundational autoethnography methodology texts; any SDT empirical literature specifically relevant to the operator's experience; Extended Mind Theory responses and critiques.]

---

*Status: draft-in-progress — narrative sections require operator expansion. Theoretical framework, methodology, and analysis structure complete. — Claude, 2026-07-16*
