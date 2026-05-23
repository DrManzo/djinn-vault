---
subject: Djinn/Operations
tags:
  - cs/djinn/operations/troubleshooting/reference
created: 2026-05-23
updated: 2026-05-23
---

# Djinn — Troubleshooting Reference

Quick diagnostics and fixes for every layer of the system. Read [[SYSTEM-STATE]] first.

---

## 1. Quick System Check

```bash
# All timers — are they running and when did they last fire?
systemctl --user list-timers

# OpenClaw gateway — is it up?
systemctl --user status openclaw

# Ollama — is it up and what's loaded?
curl -s http://127.0.0.1:11434/api/tags | python3 -m json.tool | grep name

# Last 50 lines of COMMS — what happened recently?
tail -n 50 ~/Obsidian/djinn/communications/COMMS.md

# Vault git status — is anything uncommitted?
cd ~/Obsidian && git status --short
```

---

## 2. OpenClaw Gateway

### Restart
```bash
systemctl --user restart openclaw
```

### Logs (last 100 lines)
```bash
journalctl --user -u openclaw -n 100
```

### Config location
```
~/.openclaw/openclaw.json
```

### Telegram / Discord not responding
1. Check OpenClaw is running: `systemctl --user status openclaw`
2. Check for `EmbeddedAttemptSessionTakeoverError` in logs — means session race condition
3. Reset the stuck session:
```bash
python3 - <<'EOF'
import json, uuid, pathlib
f = pathlib.Path.home() / '.openclaw/agents/main/sessions/sessions.json'
d = json.loads(f.read_text())
# Find stuck peer and reset it
for peer, s in d.items():
    print(peer, s.get('totalTokens'), s.get('status'))
EOF
```
4. If `totalTokens` is near `contextWindow` — session is full, needs reset:
```bash
# Reset a specific peer session (replace PEER_KEY with the key from above)
python3 -c "
import json, uuid, pathlib
f = pathlib.Path.home() / '.openclaw/agents/main/sessions/sessions.json'
d = json.loads(f.read_text())
peer = 'PEER_KEY_HERE'
d[peer] = {'id': str(uuid.uuid4()), 'totalTokens': 0, 'status': 'idle', 'compactionCount': 0}
f.write_text(json.dumps(d, indent=2))
print('reset done')
"
```
5. Restart gateway: `systemctl --user restart openclaw`

### NO_REPLY appearing in responses
- mistral:7b is hallucinating the gate signal as literal text
- The system prompt already has the fix. If it recurs, check `openclaw.json` main agent `systemPromptOverride` still contains the CRITICAL line

### Agent not switching (`/agent law` not working)
- Verify the law agent exists in `openclaw.json` under `agents.list`
- Check `~/.openclaw/agents/law/` directory exists
- Restart gateway after any `openclaw.json` edit

---

## 3. Ollama Models

### Check what's loaded
```bash
curl -s http://127.0.0.1:11434/api/tags | python3 -c "import json,sys; [print(m['name']) for m in json.load(sys.stdin)['models']]"
```

### Test a model directly
```bash
curl -s http://127.0.0.1:11434/api/generate \
  -d '{"model":"qwen2.5:7b","prompt":"ping","stream":false}' | python3 -m json.tool | grep response
```

### Model not loading / VRAM error
- Check VRAM usage: `nvidia-smi`
- phi4:14b needs CPU offload (9.1GB > 8GB VRAM) — normal, just slow
- If OOM: evict loaded models via `djinn-idle` or restart Ollama
```bash
systemctl --user restart ollama
```

### Context window overflow (LLM timeout)
- All models fixed to safe ctx in `openclaw.json` (16384 for 7b, 8192 for deepseek-r1)
- If Ollama is ignoring ctx settings: check `params.num_ctx` in `openclaw.json` model entries

---

## 4. Agent Scripts (Clerk / Slipbox / Embed)

### Clerk — manual run
```bash
# Process all unprocessed RAW/ files
djinn-clerk

# Process one specific file
djinn-clerk ~/Obsidian/RAW/SomeFolder/file.md
```

### Clerk — check what's been processed
```bash
python3 -c "
import json, pathlib
s = pathlib.Path.home() / '.local/share/djinn/clerk-processed.json'
d = json.loads(s.read_text()) if s.exists() else {}
print(f'{len(d)} files marked as processed')
"
```

### Clerk — force reprocess a file (remove from state)
```bash
python3 -c "
import json, pathlib
s = pathlib.Path.home() / '.local/share/djinn/clerk-processed.json'
d = json.loads(s.read_text())
key = '/home/drmanzo/Obsidian/RAW/FOLDER/FILENAME.md'
d.pop(key, None)
s.write_text(json.dumps(d, indent=2))
print('removed from state — will reprocess on next run')
"
```

### Slipbox — manual run
```bash
# Process all unlinked notes
djinn-slipbox --scan

# Process one note
djinn-slipbox ~/Obsidian/i\ notes/Notes/SomeNote.md
```

### Slipbox — "No similar notes" error
- Embedding cache is missing or stale
- Run: `djinn-embed` (incremental) or `djinn-embed --full` (rebuild everything)

### Slipbox — bad output (garbage appended)
- This was fixed 2026-05-23 — the surgical JSON approach replaced full-note rewrite
- If it recurs: check `djinn-slipbox` uses `apply_surgical_update()` not raw model output

### Embed — rebuild index
```bash
# Incremental (only new/changed files)
djinn-embed

# Full rebuild
djinn-embed --full
```

### Embed — check index size
```bash
python3 -c "
import json, pathlib
f = pathlib.Path.home() / '.djinn/embeddings/vault.json'
d = json.loads(f.read_text()) if f.exists() else {}
print(f'{len(d)} notes in index')
"
```

---

## 5. Systemd Timers

### Check all Djinn timers
```bash
systemctl --user list-timers | grep djinn
```

### Timer logs
```bash
# Clerk
journalctl --user -u djinn-clerk -n 50

# Comms processor
journalctl --user -u comms-processor -n 50

# Daily briefing
journalctl --user -u djinn-daily -n 50
```

### Restart a timer
```bash
systemctl --user restart djinn-clerk.timer
systemctl --user restart comms-processor.timer
```

### Run a service immediately (don't wait for timer)
```bash
systemctl --user start djinn-clerk.service
systemctl --user start comms-processor.service
```

---

## 6. COMMS.md Channel

### Read recent messages
```bash
tail -n 80 ~/Obsidian/djinn/communications/COMMS.md
```

### Write a task to an agent manually
Append to `~/Obsidian/djinn/communications/COMMS.md`:
```
---

### YYYY-MM-DD HH:MM UTC — @Claude → @Clerk: Process this file

**What:** Manual trigger.
**Action:** Process the RAW file at the path below.
**Paths:** `/home/drmanzo/Obsidian/RAW/SomeFolder/file.md`

— Claude
```
Then push: `cd ~/Obsidian && git add -A && git commit -m "manual comms entry" && git push`

### Comms processor not picking up tasks
1. Check it's running: `systemctl --user status comms-processor.timer`
2. Check state file (cursor position): `cat ~/.local/share/djinn/comms-processor-salomon.state`
3. If cursor is past the entry you wrote, reset it:
```bash
# Set cursor to 0 to reprocess all entries
echo 0 > ~/.local/share/djinn/comms-processor-salomon.state
```

---

## 7. Vault Git

### Vault not syncing
```bash
cd ~/Obsidian
git status
git pull
git push
```

### Uncommitted notes piling up
```bash
cd ~/Obsidian
git add -A
git -c user.name="Salomon" -c user.email="salomon@djinn" commit -m "manual vault sync"
git push
```

### GDrive sync stuck
```bash
systemctl --user status vault-sync.timer
journalctl --user -u vault-sync -n 20
```

---

## 8. Starting a Claude Session (Architecture Lane)

### Launch
```bash
djinn-claude
```

### What Claude reads at session start (in order)
1. `~/.openclaw/workspace/SOUL.md`
2. `~/.openclaw/workspace/IDENTITY.md`
3. `~/.openclaw/workspace/USER.md`
4. `~/.openclaw/workspace/AGENTS.md`
5. `~/Obsidian/djinn/communications/HEARTBEAT.md`
6. `tail -n 50 ~/Obsidian/djinn/communications/COMMS.md`

### Claude not finding context
- Check `~/.claude/CLAUDE.md` exists and points to correct paths
- Run `djinn-claude` from home directory, not a subdirectory

### Claude session ended without COMMS.md entry
- Append manually (see COMMS.md section above) with `@Claude → @All: Session summary`
- Commit and push vault

---

## 9. SSH — Salomon ↔ Typhon

```bash
# Salomon → Typhon
ssh -i ~/.ssh/id_ed25519 tf-tthq@192.168.1.113

# Test connectivity
ping 192.168.1.113

# Copy a file to Typhon
scp -i ~/.ssh/id_ed25519 /path/to/file tf-tthq@192.168.1.113:~/destination/
```

### SSH fails
- Verify both machines on same subnet: check router admin or `ip route`
- Check Typhon is on: ping first
- Key issue: `cat ~/.ssh/id_ed25519.pub` should match Typhon's `~/.ssh/authorized_keys`

---

## 10. Printer (Ender-3 V3 Plus)

```bash
# Check Moonraker is reachable
curl -s http://192.168.1.114:7125/printer/info | python3 -m json.tool | grep state

# Telegram commands (via @DjinnOCBot on Typhon)
/print_status
/print <filename>
/print_cancel
/print_queue
/print_log
```

### Printer bot not responding
```bash
ssh -i ~/.ssh/id_ed25519 tf-tthq@192.168.1.113
systemctl --user status djinn-printer-bot
journalctl --user -u djinn-printer-bot -n 30
systemctl --user restart djinn-printer-bot
```

---

## 11. Key File Locations

| File | Purpose |
|------|---------|
| `~/.openclaw/openclaw.json` | OpenClaw gateway config — agents, channels, models |
| `~/.openclaw/agents/main/sessions/sessions.json` | Active sessions — reset here if stuck |
| `~/.openclaw/workspace/SOUL.md` | Djinn behavioral rules |
| `~/.opencode/opencode.json` | opencode model config |
| `~/.local/bin/djinn-*` | All operational scripts |
| `~/.local/bin/comms-processor` | COMMS.md routing script |
| `~/.local/share/djinn/clerk-processed.json` | Clerk state — processed RAW files |
| `~/.local/share/djinn/comms-processor-salomon.state` | Comms cursor position |
| `~/.djinn/embeddings/vault.json` | Embedding index |
| `~/.config/djinn/telegram.conf` | Telegram BOT_TOKEN + CHAT_ID |
| `~/.config/djinn/printer-bot.env` | Printer bot secrets (Typhon) |
| `~/Obsidian/djinn/SYSTEM-STATE.md` | Live system state |
| `~/Obsidian/djinn/communications/COMMS.md` | Inter-agent message log |

---

*— Claude, 2026-05-23*
