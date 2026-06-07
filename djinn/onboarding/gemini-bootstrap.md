---
subject: Gemini Bootstrap Guide
updated: 2026-06-07
author: Marcus
---

# Gemini Bootstrap Guide

> **Critical note:** The djinn-vault GitHub repo is PRIVATE.
> Gemini cannot fetch raw GitHub URLs. All context delivery to Gemini goes through GDrive.
> This changes the bootstrap process entirely from the initial design.

---

## The Core Problem (Resolved)

Gemini's first response told us exactly what went wrong:
> "I cannot directly access or read the live URL because the repository is either private or currently inaccessible."

This is correct. The repo is private. GitHub raw URLs are inaccessible to Gemini.
**Solution: deliver all context via GDrive instead, where Gemini has native access.**

---

## One-Time Setup (Run on Salomon)

Before Gemini can work, these folders must exist in GDrive and the context files must be seeded:

```bash
# 1. Create Gemini's folder structure
rclone mkdir gdrive:Typhons-Forge/media/gemini
rclone mkdir gdrive:Typhons-Forge/media/gemini/diagrams
rclone mkdir gdrive:Typhons-Forge/gemini/docs
rclone mkdir gdrive:Typhons-Forge/gemini/context
rclone mkdir gdrive:Typhons-Forge/gemini/reports
rclone mkdir gdrive:Typhons-Forge/research/gemini

# 2. Seed Gemini's context inbox with the key vault files
rclone copy ~/Obsidian/djinn/GEMINI.md gdrive:Typhons-Forge/gemini/context/
rclone copy ~/Obsidian/djinn/AGENTS.md gdrive:Typhons-Forge/gemini/context/
rclone copy ~/Obsidian/djinn/GATEWAY.md gdrive:Typhons-Forge/gemini/context/
rclone copy ~/Obsidian/djinn/SYSTEM-STATE.md gdrive:Typhons-Forge/gemini/context/
rclone copy ~/Obsidian/djinn/QUEUE.md gdrive:Typhons-Forge/gemini/context/

# 3. Verify
rclone ls gdrive:Typhons-Forge/gemini/context/
```

Add this to the vault sync cron so context files stay current automatically:
```bash
# In djinn-vault-sync or a dedicated djinn-gemini-context-sync timer:
rclone copy ~/Obsidian/djinn/GEMINI.md gdrive:Typhons-Forge/gemini/context/
rclone copy ~/Obsidian/djinn/AGENTS.md gdrive:Typhons-Forge/gemini/context/
rclone copy ~/Obsidian/djinn/GATEWAY.md gdrive:Typhons-Forge/gemini/context/
rclone copy ~/Obsidian/djinn/SYSTEM-STATE.md gdrive:Typhons-Forge/gemini/context/
rclone copy ~/Obsidian/djinn/QUEUE.md gdrive:Typhons-Forge/gemini/context/
```

---

## Option 1 — Minimal Bootstrap (Most Sessions)

Open Gemini Advanced. Share the `GEMINI.md` file from GDrive in the session, then paste:

```
You are Gemini, the visual and multimodal agent of the Djinn workspace.
I have shared your session brief above (GEMINI.md from Typhons-Forge/gemini/context/).

After reading:
1. Confirm you have read the brief
2. State your lane in one sentence
3. State where your output goes (GDrive paths)
4. State the one rule you must follow before any write operation
Then wait for instructions.
```

Gemini reads the file you shared natively — no URL needed.

---

## Option 2 — Full Context Bootstrap

Share these files from GDrive in the session (from `Typhons-Forge/gemini/context/`):
- `GEMINI.md`
- `AGENTS.md`
- `GATEWAY.md`

Then paste:

```
You are Gemini, the visual and multimodal agent of the Djinn workspace.
I have shared three files above: GEMINI.md, AGENTS.md, and GATEWAY.md.

Read all three, then:
1. Confirm you have read all three
2. State your lane, delivery paths, and the peer agents
3. State what you cannot touch
Then wait for instructions.
```

---

## Option 3 — Live System Session

Share from `Typhons-Forge/gemini/context/`: `GEMINI.md`, `AGENTS.md`, `SYSTEM-STATE.md`, `QUEUE.md`

Then paste:

```
You are Gemini, the visual and multimodal agent of the Djinn workspace.
I have shared four files: GEMINI.md, AGENTS.md, SYSTEM-STATE.md, and QUEUE.md.

You are joining an active multi-agent session.
Agents currently active: [list: Marcus / Claude / DrManzo / Salomon]
Current task: [describe here]

Read all files, confirm your role in this session, then engage.
```

---

## Option 4 — Multi-Agent API Reduction Session (Today)

Share: `GEMINI.md`, `AGENTS.md`, `SYSTEM-STATE.md` from context folder.

Also paste the contents of:
- `djinn/research/marcus/` latest TASK file (Marcus's audit)
- `djinn/research/claude/2026-06-07_claude-automation-assessment.md` (Claude's assessment)

Then paste:

```
You are Gemini, the visual and multimodal agent of the Djinn workspace.
I have shared your brief and system context above.

Context: You are joining a multi-department session on reducing LLM/API usage across Djinn.
Active departments: Marcus (Perplexity), Claude (Anthropic), DrManzo, Salomon.

Marcus has produced: a 20-item vault audit + 5 orchestrator findings.
Claude has produced: a 30-item AI-to-script conversion list + honest assessment.

Your role:
1. Review what Marcus and Claude have produced (pasted above)
2. Identify visual output that would help the group (e.g. architecture diagram: LLM-backed vs script-backed services)
3. Flag anything in your lane the other departments may have missed
4. Confirm your GDrive delivery paths are ready

Confirm your role and engage.
```

---

## If Gemini Cannot Access the Shared File

Fallback: paste the full contents of `GEMINI.md` directly into the chat. It's ~2KB — small enough to paste without token concern.

```bash
# Get the text to paste:
cat ~/Obsidian/djinn/GEMINI.md
```

---

## Quick Reference — Gemini Delivery Paths

| What | GDrive Path |
|------|-------------|
| Images and renders | `Typhons-Forge/media/gemini/` |
| Architecture diagrams | `Typhons-Forge/media/gemini/diagrams/` |
| Google Docs and Slides | `Typhons-Forge/gemini/docs/` |
| Research with visuals | `Typhons-Forge/research/gemini/` |
| Text-only reports | `Typhons-Forge/research/gemini/` |
| Session reports | `Typhons-Forge/gemini/reports/` |
| Context inbox (read-only for Gemini) | `Typhons-Forge/gemini/context/` |

**GitHub is NOT in this table. Gemini does not write to GitHub.**

---

*Written by Marcus — 2026-06-07*
*Updated 2026-06-07 — full rewrite to GDrive-native workflow after Gemini confirmed GitHub raw URL access is blocked (private repo)*
