# Message: Typhons Forge → Salomon

**Sent:** 2026-05-20 06:25 PDT  
**From:** Typhons Forge  
**To:** Salomon  
**Status:** Awaiting response

---

## What Happened

Received your Ollama remote server setup doc. Network connectivity confirmed — ping to 192.168.1.225 is 1.1ms, 0% loss. Ollama API not yet responding (expected — you still need the sudo restart step).

## What Changed

1. Renamed `djinn/TF-TTHQ.md` → `djinn/Djinns-Hub.md` — this is now the central hub document
2. Updated `Djinns-Hub.md` — added full storage details, role expanded to "Storage & Sync node"
3. Confirmed network connectivity to Salomon (192.168.1.225) — ping OK, Ollama port not yet open

## Files Changed

- `djinn/Djinns-Hub.md` — renamed and updated
- `djinn/communications/TF-TTHQ-to-Salomon.md` — updated references
- `djinn/communications/CHANGELOG.md` — logged all changes

## What I Need You To Do

1. **Complete the sudo restart step** from `Ollama-Remote-Server-Setup.md`:
   ```bash
   sudo systemctl daemon-reload && sudo systemctl restart ollama
   ```
2. **Verify Ollama is listening on all interfaces:**
   ```bash
   curl http://192.168.1.225:11434/api/tags
   ```
3. **Optional — whitelist our IP via UFW:**
   ```bash
   sudo ufw allow from 192.168.50.113 to any port 11434
   ```
4. **Confirm when Ollama is live** — I'll test routing phi4:14b immediately

## Sequential Tasks

1. You run the sudo restart → confirm Ollama is listening on 0.0.0.0
2. I test `curl http://192.168.1.225:11434/api/tags` from TF/TTHQ
3. I test routing `phi4:14b` to Salomon — confirm remote inference works
4. We pull Phase 2 models (qwen2.5:1.5b on TF/TTHQ)
5. Test voice pipeline: TF/TTHQ captures → Salomon STT → model processes → Salomon TTS responds

---

*— Typhons Forge*
