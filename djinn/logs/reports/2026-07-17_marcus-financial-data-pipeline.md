---
title: Session Report — Marcus Financial Data Pipeline (built, then narrowed)
agent: Claude
date: 2026-07-17
tags: [djinn, report, marcus, finance, security]
related: [[QUEUE]] | [[build-log]] | [[decision-log]] | [[feedback-secrets]]
---

# Session Report — Marcus Financial Data Pipeline

**Date:** 2026-07-17
**Agent:** Claude
**Session type:** Architecture / Ops
**Trigger:** Javier provided 7 raw financial documents (Chase checking ...4344 + savings ...1679 activity, J.P. Morgan Self-Directed brokerage positions/tax lots ...0253, EAI report, 2 brokerage statement PDFs) and asked for them to reach Marcus for Personal CFO work.

---

## Summary

Built a pipeline for getting Javier's financial data to Marcus, then deliberately narrowed it after a security reconsideration mid-session. Raw source documents are archived locally only (gitignored, already covered by the existing Oroborus backup rotation). A redacted, no-account-number aggregate summary was extracted and committed to the git-tracked vault so Marcus can read it automatically. A separate private GitHub repo (`djinn-fin`) was created at Javier's request to hold the raw unredacted documents "for now," then deleted the same session once we confirmed a private repo doesn't actually serve the stated goal — Marcus has no auth path to read private repos — while adding a new place for sensitive data to live. Explicitly declined a follow-up request to grant Perplexity/Marcus GitHub write credentials.

---

## What Was Built or Changed

- Parsed 7 raw financial documents locally (Python stdlib `csv`, `xlrd` for the legacy `.xls`, `pdftotext -layout` for the two statement PDFs) to build category-level aggregates — no external calls, nothing left the machine during analysis.
- `personal/finance/raw/2026-07-14/` — raw source archive, gitignored, local only.
- `personal/finance/2026-07_cashflow-summary.md` — redacted summary, gitignored (Javier's own copy).
- `ai/marcus/finance/briefs/2026-07-14_cashflow-summary.md` — same summary, committed to git so Marcus reads it via normal vault navigation.
- `QUEUE.md` — added TASK-104, pointing Marcus at the brief.
- Created GitHub repo `DrManzo/djinn-fin` (private), uploaded all 7 raw documents as-is — then deleted the repo entirely later in the same session (see Technical Decisions).
- Local `~/djinn-fin/` working copy — created, then moved to system Trash via `gio trash` (no `trash` CLI installed on this box).

---

## Technical Decisions

**Aggregate summary, not raw documents, for the git-tracked Marcus path — Why:** Marcus's own stated preference (structured summaries, explicitly no raw documents/account numbers), and Marcus's only read mechanism is an unauthenticated public `raw.githubusercontent.com` URL — anything committed there is genuinely public regardless of the vault repo's own privacy conventions.

**Employer/income-source names kept, individual third-party names stripped — Why:** cross-checking Marcus's own example phrasing against the real transaction data confirmed Javier and Marcus already use short aliases for personal counterparties (e.g. a real weekly family transfer maps to the alias Marcus itself used unprompted). Employer names carry decision-relevant signal (income reliability); personal Zelle counterparties don't need to be named for cash-flow modeling.

**`djinn-fin` created, then deleted same session — Why:** Javier initially wanted raw docs in a new private repo "for now," accepting the risk himself. On follow-up ("how secure is this"), walked through GitHub's actual security model — private repos aren't reachable by Marcus's unauthenticated access mechanism anyway, so the repo added a new place sensitive data lived (a fourth copy, on a third-party server) without accomplishing the stated goal of getting Marcus access. Javier agreed to delete once that mismatch was clear. Confirmed zero collaborators and zero forks existed before deletion — full removal, not just unlisting.

**Declined to give Perplexity/Marcus GitHub write credentials — Why:** no supported integration exists for this (Perplexity is a chat interface, not a GitHub App/OAuth integration). The only mechanism would be pasting a live PAT into a third-party chat, which conflicts directly with this vault's own standing secrets rule (see [[feedback-secrets]] — never store tokens in chat content or git-tracked files, established after a prior token-in-COMMS.md incident) and creates a large, hard-to-revoke blast radius (a `repo`-scoped token reaches every private repo Javier owns, not just this one).

**No encryption-at-rest added — deferred, not rejected.** Existing gitignored local storage plus the Oroborus 23-day full-mirror backup (already scoped to include `personal/` and "financials" per its own description) was judged sufficient for now. Javier can revisit GPG-encrypting the raw archive later.

---

## Files Created or Modified

```
personal/finance/raw/2026-07-14/*                          ← raw source docs, gitignored, local only
personal/finance/2026-07_cashflow-summary.md                ← redacted summary, gitignored (Javier's copy)
ai/marcus/finance/briefs/2026-07-14_cashflow-summary.md     ← redacted summary, committed for Marcus
djinn/communications/QUEUE.md                                ← + TASK-104 (Marcus pointer)
(external, now deleted) github.com/DrManzo/djinn-fin        ← created private, uploaded raw docs, deleted same session
```

---

## Tests & Validation

- Confirmed the redacted summary contains no 6+ digit numeric runs (no account/routing numbers) before committing it to the git-tracked vault path.
- Confirmed `djinn-fin` had zero collaborators besides Javier and zero forks before deletion.
- Confirmed via `gh api repos/DrManzo/djinn-fin` (404) that the repo is fully gone post-deletion.
- Confirmed the local `~/djinn-fin` working copy no longer resolves after `gio trash`.

---

## Known Issues / Caveats

- Debit-card spend categorization in the summary is incomplete — roughly $1,390/mo across ~640 individual transactions couldn't be auto-bucketed by keyword matching against merchant descriptions. Would need real category definitions from Javier for a tighter breakdown.
- An existing decision-log entry states Djinn gets read access to "all personal domains except financial... local-only processing only." Today's redacted-summary path to Marcus is a narrow, deliberate exception to that standing rule — aggregate-only, no raw data, and the only cloud AI touching any of it gets numbers with zero account identifiers. Flagging for continuity, not reversing the standing rule.
- Raw financial documents currently exist in plaintext in two local locations: the original `~/Downloads/` files and the `personal/finance/raw/` archive. Encryption-at-rest was discussed and explicitly deferred by Javier ("leave for now").

---

## What's Next

- [ ] Javier — paste `ai/marcus/finance/briefs/2026-07-14_cashflow-summary.md` into a Perplexity/Marcus session when ready for CFO-style research (TASK-104)
- [ ] Javier — fill in Section 5 of the brief (risk tolerance, time horizon, hard rules) directly with Marcus; not derivable from the source documents
- [ ] Deferred, optional — GPG-encrypt `personal/finance/raw/` for defense-in-depth

---

*— Claude, 2026-07-17*
