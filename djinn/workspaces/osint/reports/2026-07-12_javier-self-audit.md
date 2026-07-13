# Intelligence Report: Javier / DrManzo Self-Audit

**Report ID:** OSINT-RPT-2026-07-12-javier-self-audit
**Target:** [[2026-07-12_javier-self-audit]]
**Date:** 2026-07-12
**Assembled by:** SCRIBE (Claude)
**Reviewed by:** Javier (DrManzo)
**Status:** Final

---

## Executive Summary

First real operation run through the OSINT workspace since it was bootstrapped — a Tier 1 passive self-audit of Javier's public `DrManzo` GitHub identity, prompted by finding a live-but-dead API key hardcoded in the public `djinn-vault` repo earlier this session. Found one new piece of real exposure (a second real email, `djinnstudio@gmail.com`, leaked via git commit metadata — not visible on the GitHub profile itself), confirmed the already-fixed Penelope key is still physically present in git history, and confirmed the other 9 public repos on the account are clean of secret-pattern hits. Confidence: High. No action is urgent — everything found is low-severity — but two items are worth folding into the already-queued git-history purge (TASK-103).

---

## Methodology

| Agent | Techniques Used | Sources Queried |
|---|---|---|
| RECON | General web search, GitHub profile API | Google-indexed web, `api.github.com/users/DrManzo` |
| NETPROBE | GitHub code search (secret-pattern sweep), local git log analysis | `search/code` API scoped to `user:DrManzo`, `git log --all` on djinn-vault |

SOCIAL, ARCHIVE, and TREND were not run — no seed data beyond the GitHub handle was in scope for this pass.

---

## Findings

### Identity & Profile

GitHub account `DrManzo`, created 2017-05-26, 11 followers, 10 public repos. Profile fields (`name`, `bio`, `company`, `location`, `email`, `blog`, `twitter_username`) are all empty — no PII surfaced from the profile page itself.

### Digital Footprint

`DrManzo` + `djinn-vault` does not appear in general web search results (Google-class indexing) — the repo is too new/low-traffic to be indexed yet. This is not real protection: GitHub's own search index found it instantly, and anyone with the direct handle or URL reaches it with zero friction.

Other public repos under the same account, none flagged by the secret-pattern sweep: `AI`, `faust`, `Faust_CLI`, `FinalProject`, `hypertrack-live-android`, `JourneyGame`, `sample-java-project`, `skadoosh`, `VLocksEnd`.

### Network & Infrastructure

Not applicable this pass — `djinn-vault` has no custom domain, DNS, or hosting infrastructure of its own to probe (it's a GitHub-hosted repo, not a live service).

### Social Graph

Not run — no other-platform handles were provided as seed data.

### Historical Record

The dead Penelope OctoPrint API key (redacted from the live file earlier this session, commit `bd2d6a3c`) is still present in 5 reachable commits in `djinn-vault`'s git history — `git filter-repo` was attempted but timed out on the repo's size; the purge is tracked as TASK-103 in QUEUE.md. Confirmed dead via a live 403 against the actual printer, so this is hygiene, not live exposure.

### Trend Signals

Not applicable — no market/community keyword tracking was in scope for a self-audit.

---

## Entity Link Map

Single entity (Javier / DrManzo) across two identifiers found: GitHub handle `DrManzo`, and two real email addresses — `typhonscyberforge@gmail.com` (already known) and `djinnstudio@gmail.com` (newly surfaced, via commit author metadata on `djinn-vault`, not the GitHub profile).

---

## Confidence Assessment

| Finding | Source Count | Confidence |
|---|---|---|
| `djinnstudio@gmail.com` exposed via commit metadata | 1 (direct `git log`) | High |
| Dead Penelope key still in git history | 2 (git log + `-S` pickaxe search) | High |
| Other 9 public repos clean of secret patterns | 1 (GitHub code search, 6 query patterns) | Medium — code search isn't exhaustive; a targeted manual review would raise confidence |
| Repo not yet indexed by general web search | 1 (WebSearch, 3 queries) | Medium — indexing lag, not a permanent property |

---

## Recommended Next Steps

1. Decide whether `djinnstudio@gmail.com` should be public. If not, future commits should use the GitHub noreply email (already used inconsistently — some commits use it, some don't).
2. Fold the `djinnstudio@gmail.com` history exposure into TASK-103's git-history purge — same `filter-repo` operation would need to run either way, better to do both at once than run the heavy rewrite twice.
3. Consider this the template for a recurring quarterly self-audit rather than a one-off — the workspace was built for exactly this and has sat unused since 2026-06-18.

---

## PII Notice

Two real email addresses were identified and are recorded in plaintext in the linked target file, per the operator's own explicit self-audit request (Javier auditing Javier — no third-party PII collected). No other PII was found or stored.

---

*Report assembled by SCRIBE — part of the Djinn OSINT system*
