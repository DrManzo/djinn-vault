---
subject: Gemini Bootstrap — How to Point Gemini at the Vault
tags: [onboarding, gemini, setup]
created: 2026-06-07
---

# Gemini Bootstrap — Pointing Gemini at Djinn

This doc is for **Javier** — the steps to orient a new Gemini session toward the vault.

---

## Option A — Direct GitHub URL (fastest)

Paste this at the start of any Gemini session:

```
You are Gemini, a peer agent in the Djinn platform.
Read your session brief fully before responding:
https://raw.githubusercontent.com/DrManzo/djinn-vault/main/djinn/GEMINI.md

After reading, confirm you have read it and state your lane.
```

Gemini can fetch raw GitHub URLs natively. This gives it the full brief in one shot.

---

## Option B — GDrive (if vault is synced to your Drive)

If `Typhons-Forge/` is mounted or accessible in the Gemini session:

```
You are Gemini, a peer agent in the Djinn platform.
Read: Typhons-Forge/djinn/GEMINI.md
Then read: Typhons-Forge/djinn/GATEWAY.md
Confirm you have read both before proceeding.
```

---

## Option C — Paste the brief directly

If neither URL nor GDrive is accessible in the session:
1. Open `djinn/GEMINI.md` on GitHub
2. Copy raw contents
3. Paste into Gemini with: "This is your session brief. Read it fully."

---

## After Gemini Confirms

Once Gemini signals readiness, route tasks using normal department syntax:

| Task type | Route |
|-----------|-------|
| Image generation | → Gemini, deliver to `Typhons-Forge/media/gemini/` |
| System diagram | → Gemini, deliver to `Typhons-Forge/media/gemini/` |
| Visual brief / slide deck | → Gemini, deliver to `Typhons-Forge/gemini/` |
| Multimodal research | → Gemini, deliver to `Typhons-Forge/research/gemini/` |
| Sprint review | → Gemini, read `djinn/decisions/2026-06-07-api-reduction-sprint.md` |

---

## GDrive Folder Structure for Gemini

Create these folders in `Typhons-Forge/` if they don't exist:

```
Typhons-Forge/
├── media/
│   └── gemini/          ← images, renders, diagrams
├── gemini/              ← docs, slides, visual briefs
├── research/
│   └── gemini/          ← research output with visuals
└── logs/
    └── gemini/          ← session reports
```

Salomon's rclone sync picks up everything in `Typhons-Forge/` every 2 minutes.
Gemini writes here → Salomon pulls → vault has it. No GitHub push needed for media.

---

## Notes

- Gemini's session brief is at `djinn/GEMINI.md` — update it as the platform evolves
- Gemini does NOT need to push to GitHub for media/images — GDrive is the canonical store
- Text-only outputs (analysis, research notes) can go to either GDrive or GitHub
- Always confirm Gemini has read GATEWAY.md before any session involving file writes

---

*— Marcus, 2026-06-07*
