---
subject: Gemini Bootstrap Guide
updated: 2026-06-07
author: Marcus
---

# Gemini Bootstrap Guide

> How to point a new Gemini session at the Djinn Vault so it knows the rules, its lane, and where to deliver output.

---

## Option 1 — Minimal (Fastest, Recommended for Most Sessions)

Paste this prompt at the start of any new Gemini session:

```
You are Gemini, the visual and multimodal agent of the Djinn workspace.
Read your session brief before responding:
https://raw.githubusercontent.com/DrManzo/djinn-vault/main/djinn/GEMINI.md

After reading:
1. Confirm you have read the brief
2. State your lane in one sentence
3. State where your output goes (GDrive path and GitHub path)
4. State the one file you must read before any write operation
Then wait for instructions.
```

Gemini will fetch and read `GEMINI.md` directly from GitHub. No copy-paste of the full file needed.

---

## Option 2 — Full Context (For Architecture or Multi-Agent Sessions)

Paste this prompt for sessions where Gemini needs to know the full system:

```
You are Gemini, the visual and multimodal agent of the Djinn workspace.

Read these files in order before responding:
1. Session brief (your lane and rules):
   https://raw.githubusercontent.com/DrManzo/djinn-vault/main/djinn/GEMINI.md

2. Full agent registry (all departments and routing):
   https://raw.githubusercontent.com/DrManzo/djinn-vault/main/djinn/AGENTS.md

3. Enforcement contract (read before any write):
   https://raw.githubusercontent.com/DrManzo/djinn-vault/main/djinn/GATEWAY.md

After reading all three:
1. Confirm you have read all three files
2. State your lane, your delivery paths, and the peer agents
3. State what you cannot touch
Then wait for instructions.
```

---

## Option 3 — Gemini Advanced / Deep Research Sessions

For sessions that need the live system state (what's running, what's queued):

```
You are Gemini, the visual and multimodal agent of the Djinn workspace.

Read these files before responding:
1. https://raw.githubusercontent.com/DrManzo/djinn-vault/main/djinn/GEMINI.md
2. https://raw.githubusercontent.com/DrManzo/djinn-vault/main/djinn/AGENTS.md
3. https://raw.githubusercontent.com/DrManzo/djinn-vault/main/djinn/SYSTEM-STATE.md
4. https://raw.githubusercontent.com/DrManzo/djinn-vault/main/djinn/QUEUE.md

You are joining an active multi-agent session. The other agents currently active are:
[list: Marcus / Claude / DrManzo / Salomon — as applicable]

Current task: [describe the session topic here]

Confirm you have read all files, state your role in this session, and then engage.
```

---

## GDrive Setup (First Time Only)

For Gemini to write to the Djinn workspace via Google Drive:

1. **Ensure Salomon rclone is configured** for `gdrive:Typhons-Forge/`
   - Check: `rclone ls gdrive:Typhons-Forge/ | head -20`
   - If not configured: run `rclone config` and add the Google Drive remote as `gdrive`

2. **Gemini output folders must exist:**
   ```bash
   rclone mkdir gdrive:Typhons-Forge/media/gemini
   rclone mkdir gdrive:Typhons-Forge/media/gemini/diagrams
   rclone mkdir gdrive:Typhons-Forge/gemini/docs
   rclone mkdir gdrive:Typhons-Forge/research/gemini
   ```

3. **Sync timer** — vault already syncs every 2 minutes via `djinn-vault-sync`. GDrive content lands in `~/Obsidian/djinn/` automatically. No manual step needed after initial setup.

4. **Gemini writes directly to GDrive** via its native Google Drive integration in Gemini Advanced. No API call or rclone needed from Gemini's side — it can create and write files in `My Drive` or `Shared Drives` natively.

---

## GitHub Write Access for Gemini (Text Output Only)

For text-only deliverables, Gemini can push directly to the vault:

- **Repo:** `github.com/DrManzo/djinn-vault`
- **Target path:** `djinn/research/gemini/`
- **Commit format:** `gemini: [description] (Gemini YYYY-MM-DD)`
- **Branch:** `main`

If Gemini does not have direct GitHub write access in the current session, the fallback is:
1. Gemini writes the markdown to GDrive at `Typhons-Forge/research/gemini/TASK-NNN_slug.md`
2. Salomon rclone pulls it into the vault on the next 2-minute sync
3. Claude or Marcus commits it to GitHub if needed

---

## Quick Reference — Gemini Delivery Paths

| What | Where |
|------|-------|
| Images and renders | `gdrive:Typhons-Forge/media/gemini/` |
| Architecture diagrams | `gdrive:Typhons-Forge/media/gemini/diagrams/` |
| Google Docs and Slides | `gdrive:Typhons-Forge/gemini/docs/` |
| Research with visuals | `gdrive:Typhons-Forge/research/gemini/` |
| Text-only research | `github: djinn/research/gemini/` |
| Session reports | `github: djinn/logs/reports/YYYY-MM-DD_gemini-<slug>.md` |

---

*Written by Marcus — 2026-06-07*
