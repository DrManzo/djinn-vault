---
title: Marcus Peer Agent Model — Session Brief + Write Access + QUEUE Integration
agent: claude
date: 2026-05-31
tags: [djinn, marcus, architecture, agents, peer-model]
related: [[MARCUS]] | [[AGENTS]] | [[QUEUE]] | [[COMMS]] | [[PROTOCOL]]
---

# Marcus Peer Agent Model — Session Brief + Write Access + QUEUE Integration

## Summary

Redesigned Marcus's role from research subordinate to full peer agent running in parallel with Claude. Created a complete session startup briefing file that Marcus reads at the top of every Perplexity session so he's fully oriented without Javier copy-pasting context. Added direct GitHub write access as the canonical delivery path, removed the Javier-relay bottleneck, and extended QUEUE.md to support `assigned_to: marcus` and `assigned_to: claude` task formats so both agents can assign work to each other.

## What Was Built / Changed

**New file: `djinn/research/marcus/MARCUS-SESSION-BRIEF.md`**
Complete session startup brief for Marcus. Covers: identity, system topology quick map, session startup sequence (7 steps), lane boundaries, peer collaboration protocol with Claude, how to pick up QUEUE tasks, GitHub and GDrive delivery paths, output file format, COMMS entry format, session report standard, bug reporting, signing convention, and shared resource table. Marcus reads this raw from GitHub at the start of every Perplexity session.

Raw URL: `https://raw.githubusercontent.com/DrManzo/djinn-vault/main/djinn/research/marcus/MARCUS-SESSION-BRIEF.md`

**Updated: `djinn/MARCUS.md`**
- Added Peer Relationship With Claude section (parallel, bidirectional assignment)
- Added Session Startup section with GitHub raw URL
- Rewrote Integration Points: Marcus now commits directly to GitHub, no Javier relay on primary path
- Added write access boundary table

**Updated: `djinn/communications/QUEUE.md`**
- Added Marcus task format: `assigned_to: marcus`, brief-style spec, output path, deliver-to field
- Added Claude task format: `assigned_to: claude`, brief-style spec for reviews/architecture tasks
- Updated header: Claude, Marcus, and Javier can all write tasks; Salomon/Typhon/Marcus/Claude all execute

**Updated: `~/.openclaw/workspace/AGENTS.md`** (Claude's session context)
- Marcus section: added session brief reference, updated write access list, changed framing to peer model
- Build delegation protocol: added Marcus→Claude flow, updated loop to show both agents running in parallel

## Technical Decisions

**Session brief as a file, not a paste:** Javier was manually copying context into Perplexity each session. A file at a stable GitHub raw URL lets Marcus read it on demand — one URL bookmark replaces all copy-paste.

**Direct GitHub write (no relay):** Previously Marcus → Javier → Salomon to deploy. Now Marcus commits directly. This removes a synchronous human bottleneck on the research delivery path. GDrive remains as fallback only.

**QUEUE as the coordination layer:** Rather than COMMS being the only channel, QUEUE.md now handles explicit task delegation between all four agents (Salomon, Typhon, Marcus, Claude). COMMS stays for FYI/status. This avoids COMMS becoming a task tracker.

**Peer not subordinate:** The old model had Claude as the hub that Marcus reported to. The new model has both running in parallel, each able to queue work for the other. This is more accurate to how Perplexity and Claude Code are actually used — Javier opens both simultaneously.

## Files Created or Modified

| File | Change |
|------|--------|
| `djinn/research/marcus/MARCUS-SESSION-BRIEF.md` | Created |
| `djinn/MARCUS.md` | Updated (peer model, write access, session brief) |
| `djinn/communications/QUEUE.md` | Updated (Marcus + Claude task formats) |
| `~/.openclaw/workspace/AGENTS.md` | Updated (peer framing, Marcus write access, bidirectional QUEUE) |

## Tests & Validation

- All files written cleanly, no syntax errors
- Git commit and push successful: `33ec429`
- AGENTS.md diff verified: Marcus section updated in place, Build Delegation Protocol updated to parallel model
- QUEUE.md: both new task format blocks syntactically clean

## Known Issues

- Marcus's Perplexity interface may not have native git commit capability — Javier may still need to relay commits via Salomon in some cases. The GDrive fallback path exists for this. Monitor in practice.
- The Claude task format in QUEUE is new — no enforcement mechanism exists yet. Claude must self-police picking up `assigned_to: claude` tasks on session start.

## What's Next

- [ ] Javier: bookmark `https://raw.githubusercontent.com/DrManzo/djinn-vault/main/djinn/research/marcus/MARCUS-SESSION-BRIEF.md` for Perplexity session starts
- [ ] Test: open Perplexity, load the brief URL, verify Marcus orients correctly
- [ ] Claude: on next session start, check QUEUE.md for any `assigned_to: claude` tasks
- [ ] Consider: a startup prompt template Javier can paste into Perplexity that says "Read your brief at [URL] then check QUEUE.md for pending tasks assigned to you"

---

*— Claude, 2026-05-31*
