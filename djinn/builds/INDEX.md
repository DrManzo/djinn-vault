---
title: Builds — Master Index
tags: [djinn, builds, planning, index]
updated: 2026-06-21
access: RESTRICTED
---

# Builds Workspace

> **ACCESS: Javier + Claude only.**
> Salomon, Typhon, Marcus, and all other agents are not permitted to read,
> write, or act on anything in this folder. No tasks from this space go to
> QUEUE.md. No briefs are forwarded to other agents without Javier's explicit
> instruction.

This is the central space for all build planning — from event calendar to model brief to print-ready prompt. Everything that becomes a print starts here.

---

## How it works

```
CALENDAR event → BRIEF (idea + dims + refs) → PROMPT (for Meshy/Marcus) → PRINT
```

1. Pick an event or idea from [[calendar/2026-events]]
2. Create a brief in `briefs/` using [[TEMPLATE-BRIEF]]
3. Write or paste the model generation prompt in `prompts/`
4. Add measurements and reference images in `reference/` if needed
5. Hand off to the print pipeline

---

## Folders

| Folder | What goes here |
|--------|---------------|
| `calendar/` | Event lists, build windows, seasonal planning |
| `briefs/` | One file per build idea — concept, dims, notes, status |
| `prompts/` | AI prompts for Meshy, Marcus, or Blender generation |
| `reference/` | Measurements, fit specs, style notes, inspiration |

---

## Active Briefs

*Add links here as you create briefs — works as a quick-access list on tablet.*

- [ ] (none yet — create your first brief from [[TEMPLATE-BRIEF]])

---

## Calendar

- [[calendar/2026-events]] — 47 events, Jul–Dec 2026, with build ideas per date

---

## Quick-add on tablet

To add a new build idea on the go:
1. Open `builds/briefs/`
2. Create new note — name it `YYYY-MM-DD_<slug>.md`
3. Paste the [[TEMPLATE-BRIEF]] content and fill in what you know
4. Leave blanks — Claude fills in dims, prompts, and pipeline steps later

---

*— Claude, 2026-06-21*
