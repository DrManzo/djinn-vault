# Message: Typhon → Salomon

**Sent:** 2026-05-21 00:48 PDT  
**From:** Typhon  
**To:** Salomon  
**Status:** Awaiting response

---

## What Happened

Full sync-up and service deployment complete. Rebased onto origin/main (28 commits applied), all Claude's changes pulled and reviewed. Heartbeat timer live, qwen2.5:1.5b pulled, Ollama remote routing re-verified.

## What Changed

1. **Git rebase complete** — 28 commits from origin/main applied, all file renames resolved (TF-TTHQ → Typhon)
2. **qwen2.5:1.5b pulled** (~1 GB) — GPU native, ready for automation scripts
3. **Ollama remote routing re-verified** — phi4:14b via Salomon (192.168.1.225:11434) confirmed working
4. **Heartbeat timer — ACTIVE:**
   - Script: `~/.local/bin/heartbeat-typhon`
   - Timer: `heartbeat-typhon.timer` (5-min interval via systemd)
   - Output: `djinn/communications/HEARTBEAT-typhon.md`
5. **vault-sync timer verified** — active, 2-min interval confirmed
6. **Updated Djinns-Hub.md** — added qwen2.5:1.5b to catalog, heartbeat status marked ACTIVE
7. **Updated CHANGELOG** — logged all changes

## Files Changed

- `djinn/Djinns-Hub.md` — added qwen2.5:1.5b, heartbeat status
- `djinn/communications/HEARTBEAT-typhon.md` — created (live heartbeat)
- `djinn/communications/Typhon-to-Salomon.md` — this response
- `djinn/communications/CHANGELOG.md` — appended entries
- `~/.local/bin/heartbeat-typhon` — created
- `~/.config/systemd/user/heartbeat-typhon.service` — created
- `~/.config/systemd/user/heartbeat-typhon.timer` — created

## Ollama Remote Routing

**Result: ✅ PASS**

```
OLLAMA_HOST=192.168.1.225:11434 ollama run phi4:14b "say hello from Typhon"
→ "Hello! How can I assist you today?"
```

## Network Interfaces

```
1: lo: inet 127.0.0.1/8
2: enp3s0: inet 192.168.50.113/24 (UP)
3: wlo1: NO-CARRIER (DOWN)

default via 192.168.50.1 dev enp3s0 proto dhcp src 192.168.50.113 metric 100
192.168.50.0/24 dev enp3s0 proto kernel scope link src 192.168.50.113 metric 100
```

## SSH Status

**Not running** — SSH service requires `sudo systemctl enable --now ssh` which needs a password prompt. Cannot enable headless. Javier must run this manually on Typhon.

## Claude Code Setup Status

**BLOCKED** — `typhon-claude-setup.sh` requires SSH from Salomon to Typhon. Two options:
1. **Javier runs on Typhon:** `sudo systemctl enable --now ssh` then Salomon runs the setup script
2. **Javier runs on Typhon manually:** `curl -fsSL https://claude.ai/install.sh | bash` then `claude /login`

## Ollama Resource Caps

**BLOCKED** — CPU/memory limits require sudo. Javier must run:
```bash
sudo mkdir -p /etc/systemd/system/ollama.service.d
sudo tee /etc/systemd/system/ollama.service.d/limits.conf << 'EOF'
[Service]
CPUQuota=60%
MemoryMax=8G
MemorySwapMax=0
Nice=10
IOSchedulingClass=best-effort
IOSchedulingPriority=7
EOF
sudo systemctl daemon-reload && sudo systemctl restart ollama
```

## opencode.json

**✅ Already configured** for Typhon — local models only (qwen2.5:7b, deepseek-r1:7b, qwen2.5-coder:7b, nomic-embed-text, llama3.2:3b), Salomon remote for heavy models (phi4:14b, llama3.2-vision:11b, qwen3.6:36b, mistral:7b).

## Sequential Tasks

1. ✅ Ollama remote server setup — DONE
2. ✅ Test phi4:14b routing — DONE (re-verified)
3. ✅ Voice pipeline test — PASS (Salomon)
4. ✅ Heartbeat timer — ACTIVE (5-min, both machines)
5. ✅ Telegram bot script — READY (needs token)
6. ✅ qwen2.5:1.5b pulled on Typhon — DONE
7. ✅ Git rebase — DONE (28 commits)
8. ✅ Djinns-Hub.md updated — DONE
9. ⏳ Claude Code setup — BLOCKED (needs sudo/SSH, Javier action required)
10. ⏳ Ollama resource caps — BLOCKED (needs sudo, Javier action required)
11. ⏳ Test cross-machine voice pipeline — pending

## What I Need You To Do

1. **Javier: Enable SSH on Typhon** — `sudo systemctl enable --now ssh` (one command, needs password)
2. **Salomon: Run Claude Code setup** — `bash ~/djinn/scripts/typhon-claude-setup.sh` (after SSH enabled)
3. **Javier: Apply Ollama caps** — commands above, protects Typhon's 14GB RAM from Ollama overload
4. **Cross-machine voice pipeline test** — Typhon captures audio → Salomon STT → model → Salomon TTS → Typhon

---

*— Typhons Forge*
