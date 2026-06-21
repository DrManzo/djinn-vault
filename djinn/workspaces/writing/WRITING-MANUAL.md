# Writing — Workspace Manual

**Workspace:** `djinn/workspaces/writing/`
**Department Head:** Javier (DrManzo)
**Status:** Active
**Access:** Javier + Claude only — no other agents
**Created:** 2026-06-21

---

## What This Department Does

This is the private writing workspace for Javier's book projects. It owns the full lifecycle of written work — from raw notes and fragments captured on the go, to outlines, drafts, and finished material. Nothing here is forwarded to other agents or the pipeline without Javier's explicit instruction.

---

## File Structure

```
djinn/workspaces/writing/
├── WRITING-MANUAL.md               ← You are here
├── INDEX.md                        ← Master index, active projects, quick links
├── agents/
│   └── SCRIBE.md                   ← Claude's writing brief (how to assist)
├── projects/
│   ├── notes/                      ← Fragments, ideas, on-the-go captures
│   ├── outlines/                   ← Chapter maps, arc structure, planning
│   ├── drafts/                     ← Working drafts — chapters, sections, scenes
│   └── research/                   ← Source notes, facts, reference material
└── references/                     ← Style guides, voice notes, structural references
```

---

## Access Rule

**Javier + Claude only.** No other agents read or act on this workspace.
Nothing leaves this folder until Javier says it is ready.

---

## Workflow

```
FRAGMENT (notes/) → OUTLINE (outlines/) → DRAFT (drafts/) → READY
```

1. Javier drops raw ideas into `projects/notes/` — any format, any time, tablet or desktop
2. Claude develops fragments into outlines when instructed
3. Outlines become working drafts in `projects/drafts/`
4. Research and references accumulate in their folders as needed
5. When a piece is ready, Javier decides what happens next

---

## Quick-add on tablet

- Raw idea → `projects/notes/YYYY-MM-DD_<slug>.md`
- Chapter plan → `projects/outlines/`
- Drop anything, name it anything — Claude cleans it up later

---

## Agent Roster

| Agent | Role |
|-------|------|
| Claude | Primary writing partner — drafting, structure, research, editing |
| Javier | Author, creative director, final word on everything |

No other agents are assigned to this workspace.

---

*— Claude, 2026-06-21*
