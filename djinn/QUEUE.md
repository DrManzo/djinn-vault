---
subject: Agent Task Queue
updated: 2026-06-07
---

# QUEUE.md — Djinn Task Queue

Active tasks pending assignment or completion.
Agents append to this file. Javier sets priorities.

## Format

    TASK-NNN | [lane] | [agent] | [priority] | description

## Active Queue

- [ ] TASK-001 | all-lanes | all | HIGH | API reduction: implement top 20 script replacements (session 2026-06-07)

- [ ] TASK-002 | infra | Salomon | HIGH | Build Flask inbox endpoint on Salomon (port 8765) — accepts POST {text, session, agent}, writes to ~/djinn-inbox/. Unlocks phone + iMac + laptop chat ingestion.

- [ ] TASK-003 | infra | Salomon | HIGH | Deploy inbox-watcher.service — inotifywait on ~/djinn-inbox, fires marcus-sync.py --auto-detect-agent on any new file drop.

- [ ] TASK-004 | infra | Salomon | HIGH | Write marcus-sync.py — deterministic ingestor: reads ~/djinn-inbox/*.md, adds Obsidian frontmatter (date/agent/session/tags), routes to djinn/research/{agent}/sessions/, deletes inbox file, no LLM.

- [ ] TASK-005 | mobile | Javier | MEDIUM | Create iPhone Shortcut "Send to Djinn" — Share Sheet trigger, asks session name + agent, POSTs to Salomon Flask endpoint via Tailscale/local network.

- [ ] TASK-006 | desktop | Javier | MEDIUM | Add iMac Safari/Chrome bookmarklet — grabs page innerText, prompts session + agent, POSTs to Salomon Flask endpoint. One drag to bookmarks bar.

- [ ] TASK-007 | gemini-lane | Gemini | MEDIUM | Establish Gemini session-end GDrive write convention — at end of each session Gemini writes summary Doc to Typhons-Forge/gemini/reports/gemini-session-YYYY-MM-DD.md. Salomon rclone picks up on 2-min cycle.

- [ ] TASK-008 | infra | Salomon | LOW | Wire Firefox AI Chat Exporter output folder to ~/djinn-inbox/ drop target via SSH/SFTP mount or Tailscale file drop. Laptop-only, lowest priority since Flask endpoint covers all devices.

## Completed

- [x] TASK-002 | infra | Claude | 2026-06-07 | Flask inbox endpoint written: djinn/tools/inbox/flask_inbox.py — deploy to Salomon per README in that dir
- [x] TASK-003 | infra | Claude | 2026-06-07 | inbox-watcher.py + inbox-watcher.service written: djinn/tools/inbox/ — deploy to Salomon
- [x] TASK-004 | infra | Claude | 2026-06-07 | marcus-sync.py written: djinn/tools/inbox/marcus-sync.py — deploy to ~/.local/bin/ on Salomon
