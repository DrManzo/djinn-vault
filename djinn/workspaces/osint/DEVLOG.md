# DEVLOG — OSINT / Intelligence Department

This file is an append-only operation history maintained by the OSINT Scribe agent.
Each entry records what was done, which agents were involved, which files were changed, and what commit was suggested.

---

## 2026-06-18T11:38:00Z — Initial department setup

- **Agents:** Marcus (Perplexity), SCRIBE
- **Files changed:**
  - `djinn/workspaces/osint/OSINT-MANUAL.md` (created)
  - `djinn/workspaces/osint/TEAM.md` (created)
  - `djinn/workspaces/osint/DEVLOG.md` (created)
  - `djinn/workspaces/osint/targets/README.md` (created)
  - `djinn/workspaces/osint/targets/_template.md` (created)
  - `djinn/workspaces/osint/reports/README.md` (created)
  - `djinn/workspaces/osint/reports/_template.md` (created)
  - `djinn/workspaces/osint/feeds/README.md` (created)
  - `djinn/workspaces/osint/feeds/feed-registry.md` (created)
  - `djinn/workspaces/osint/tools/README.md` (created)
  - `djinn/workspaces/osint/agents/RECON.md` (created)
  - `djinn/workspaces/osint/agents/SOCIAL.md` (created)
  - `djinn/workspaces/osint/agents/NETPROBE.md` (created)
  - `djinn/workspaces/osint/agents/ARCHIVE.md` (created)
  - `djinn/workspaces/osint/agents/TREND.md` (created)
  - `djinn/workspaces/osint/agents/CORRELATOR.md` (created)
  - `djinn/workspaces/osint/agents/SCRIBE.md` (created)
- **Summary:** Bootstrapped the OSINT Intelligence Department workspace. Added full department manual with Gateway tier policy, routing rules, and operation protocol. Created TEAM.md with 7 specialist agents: RECON, SOCIAL, NETPROBE, ARCHIVE, TREND, CORRELATOR, and SCRIBE. All agents include identity, responsibilities, tool assignments, and escalation rules. Gateway Tier 3/4 enforcement for PII and active enumeration documented throughout. Full directory scaffold committed: targets/, reports/, feeds/, tools/, agents/.
- **Suggested commit:** `feat(osint): bootstrap OSINT workspace with full department scaffold`

---

## 2026-07-12T23:45:00Z — First live operation: Javier self-audit

- **Agents:** RECON, NETPROBE, SCRIBE (Claude)
- **Files changed:**
  - `djinn/workspaces/osint/targets/2026-07-12_javier-self-audit.md` (created)
  - `djinn/workspaces/osint/reports/2026-07-12_javier-self-audit.md` (created)
- **Summary:** First real operation run through this workspace since bootstrap on 2026-06-18 — everything before this was scaffolding. Tier 1 passive self-audit of the `DrManzo` GitHub identity, prompted by finding a live-but-dead OctoPrint API key hardcoded in public `djinn-vault` earlier this session. RECON: general web search doesn't index the account/repo yet (not real protection — GitHub's own search finds it instantly); profile page itself leaks no PII. NETPROBE: GitHub code search (6 secret-pattern queries) across all 10 public repos under the account found no live secrets beyond the already-fixed one, and confirmed the other 9 repos are clean. Two real findings: (1) a second real email, `djinnstudio@gmail.com`, is exposed via git commit author metadata — not visible on the profile, but trivially found via `git log`; (2) the already-redacted Penelope key is still physically present 5 commits deep in git history (filter-repo purge, TASK-103, is still pending). Confidence: High. Nothing above Tier 1/2 — no third-party PII collected.
- **Suggested commit:** `osint(javier-self-audit): first live op — GitHub footprint audit finds commit-metadata email exposure`

---

## 2026-07-13T00:05:00Z — Javier self-audit escalated to Tier 2

- **Agents:** SOCIAL, SCRIBE (Claude)
- **Files changed:**
  - `djinn/workspaces/osint/targets/2026-07-12_javier-self-audit.md` (updated — Tier 2 added, SOCIAL findings)
  - `djinn/workspaces/osint/reports/2026-07-12_javier-self-audit.md` (updated — Tier 2 findings)
- **Summary:** Operator confirmed `djinnstudio@gmail.com` (Tier 1 finding) is their own address, then provided their real name directly and requested Tier 2. Auto-approved per the workspace's own Gateway policy (Tier 2 = operator-aware, not confirm-gated). SOCIAL cross-referenced the real name against the DrManzo/Djinn/Forge persona — no public link found, which is the good result for this kind of audit. Real name is common enough that name-only search returns dozens of unrelated people; deliberately did not chase those down (misattribution risk, not a finding). Gravatar checked for both known emails — clean, no avatar registered on either. Also surfaced that SOCIAL's documented tools (`djinn-bore-core`, `djinn-social-analyst`) don't actually do handle enumeration — `djinn-bore-core` is a 3D-print geometry tool, `djinn-social-analyst` needs missing config — so this pass used plain web search instead. Per the workspace's own PII non-negotiable ("no names in plaintext vault files"), the operator's real name was used as a search input but deliberately never written into either the target file or report — this repo is public, and writing it would create the exact real-name↔persona link the audit confirmed doesn't currently exist.
- **Suggested commit:** `osint(javier-self-audit): escalate to Tier 2 — no real-name/persona link found, SOCIAL tool stack drift noted`

---

## 2026-07-13T00:15:00Z — Javier self-audit: operator-supplied Pinterest handle checked

- **Agents:** SOCIAL, SCRIBE (Claude)
- **Files changed:**
  - `djinn/workspaces/osint/targets/2026-07-12_javier-self-audit.md` (updated — Pinterest finding)
  - `djinn/workspaces/osint/reports/2026-07-12_javier-self-audit.md` (updated — Pinterest finding)
- **Summary:** Operator supplied a specific Pinterest handle (`boxingking1`) to check directly. Fetched the page: `<title>` and meta description tags are fully public and search-indexed, directly attributing the account to the operator's real name — more discoverable by real-name search than `djinn-vault` currently is. Content is unrelated personal hobby boards (hairstyle/facial-hair history, general art references); no mention of Djinn, Forge, or the maker/cybersecurity persona anywhere, and the handle isn't reused on other platforms in a way that bridges either (checked X/Twitter, Roblox, YouTube — all unrelated third parties using similar handles). Net finding unchanged: real name and DrManzo/Djinn persona remain unlinked. Process note: initially drafted a line quoting the Pinterest page's exact title text (which contains the real name) directly into this public repo before catching it — corrected before commit to describe the finding without reproducing the name string, consistent with the PII Notice already in place. Worth remembering for any future pass: quoting evidence verbatim is not automatically safe just because the source itself is already public.
- **Suggested commit:** `osint(javier-self-audit): check operator-supplied Pinterest handle — real-name-indexed, no persona crossover`

---

## 2026-07-13T00:25:00Z — Javier self-audit: two LinkedIn profiles confirmed

- **Agents:** SOCIAL, SCRIBE (Claude)
- **Files changed:**
  - `djinn/workspaces/osint/targets/2026-07-12_javier-self-audit.md` (updated — LinkedIn finding)
  - `djinn/workspaces/osint/reports/2026-07-12_javier-self-audit.md` (updated — LinkedIn finding)
- **Summary:** Operator confirmed ownership of both LinkedIn profiles surfaced during Tier 2 name search. LinkedIn blocks unauthenticated access outright (HTTP 999 on curl and WebFetch alike) — no content beyond pre-indexed search-snippet headlines was retrievable (university-student era; home-improvement-company employment). Neither connects to the Djinn/Forge persona. Same PII handling as the Pinterest finding: profile IDs described but not reproduced as literal name-bearing URLs in this public repo, consistent with the earlier near-miss lesson. Overall self-audit conclusion holds across every identifier checked this operation (GitHub, Pinterest, 2x LinkedIn): real identity and DrManzo/Djinn persona remain unlinked.
- **Suggested commit:** `osint(javier-self-audit): confirm 2 LinkedIn profiles — LinkedIn blocks scraping, no persona crossover`
