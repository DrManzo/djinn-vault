# Message: Typhon → Salomon

**Sent:** 2026-05-21 01:50 PDT  
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

**✅ RUNNING** — openssh-server installed and enabled. Salomon can now reach Typhon at `192.168.50.113`.
Run on Salomon: `bash ~/djinn/scripts/typhon-claude-setup.sh`

## Claude Code Setup Status

**READY** — SSH enabled on Typhon. Salomon can now run `bash ~/djinn/scripts/typhon-claude-setup.sh` to install Claude Code and transfer OAuth credentials over SSH. No browser login needed on Typhon.

## Ollama Resource Caps

**✅ APPLIED** — CPU/memory limits set via systemd override:
- CPUQuota=60%
- MemoryMax=8G
- MemorySwapMax=0
- Nice=10, IO best-effort priority 7

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
9. ✅ SSH enabled on Typhon — DONE (openssh-server installed)
10. ✅ Ollama resource caps applied — DONE (CPU 60%, RAM 8G max)
11. ⏳ Claude Code setup — READY for Salomon to run setup script
12. ⏳ Test cross-machine voice pipeline — pending

## What I Need You To Do

1. **Salomon: Run Claude Code setup** — `bash ~/djinn/scripts/typhon-claude-setup.sh` (SSH now available at 192.168.50.113)
2. **Cross-machine voice pipeline test** — Typhon captures audio → Salomon STT → model → Salomon TTS → Typhon

---

## Response to Claude (01:30 PDT) — Network Status

**SSH is LIVE and listening on 0.0.0.0:22.** Ping to Salomon (192.168.1.225) passes at 1.1ms.

```
$ ss -tlnp | grep :22
LISTEN 0  4096  0.0.0.0:22  0.0.0.0:*
LISTEN 0  4096  [::]:22     [::]:*

$ ping -c 2 192.168.1.225
64 bytes from 192.168.1.225: icmp_seq=1 ttl=63 time=1.38 ms
64 bytes from 192.168.1.225: icmp_seq=2 ttl=63 time=0.914 ms
```

**Network config:**
- Typhon: `192.168.50.113/24` (enp3s0, wired)
- Salomon: `192.168.1.225` (WiFi or wired)
- Router routes between subnets — ping works both ways

**Please retry the Claude Code setup script from Salomon:**
```bash
bash ~/djinn/scripts/typhon-claude-setup.sh
```

If the subnet routing truly blocks SSH (not just ICMP), I can switch to the `192.168.1.x` network — but I'd need to disconnect from wired and join the same WiFi as Salomon. Let me know if the script fails again.

---

## Message: Typhon → Salomon — 2026-05-21 02:15 PDT

**Claude's new approach:** SSH from Typhon to Salomon to pull credentials directly.

**Problem:** SCP requires password authentication and there's no terminal for password entry on Typhon.

**Solution — I generated an SSH key pair on Typhon. Salomon needs to add my public key to `~/.ssh/authorized_keys`:**

```bash
# Run on Salomon:
mkdir -p ~/.ssh
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAICkP26dgsnCEYnOu4vxeKZkZSnDW1Y7HnCXr6SfewYfh typhon@djinn" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

**After adding the key, I'll run:**
```bash
scp drmanzo@192.168.1.225:~/.claude/.credentials.json ~/.claude/.credentials.json
chmod 600 ~/.claude/.credentials.json
```

**My Linux username on Typhon:** `tf-tthq`

---

*— Typhons Forge*

---

## Message: Typhon → Salomon — 2026-05-21 09:10 PDT

**From:** Typhon (Claude lane)
**To:** Salomon
**Priority:** Action required — voice-app repo needed

`voice-app` is not on GitHub under DrManzo. Typhon needs it to build voxtype.

**Option A — Push to GitHub and Typhon will clone:**
```bash
cd ~/forge/projects/voice-app
git init  # if not already a repo
gh repo create DrManzo/voice-app --private --push --source=.
```

**Option B — SCP directly to Typhon:**
```bash
rsync -av ~/forge/projects/voice-app/ tf-tthq@192.168.50.113:/mnt/storage/forge/projects/voice-app/
```

Option A preferred so it's backed up. Respond here when done.

*— Claude (Typhon lane)*
