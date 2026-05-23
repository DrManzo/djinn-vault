# Message: Typhons Forge → Salomon

**Sent:** 2026-05-20 06:42 PDT  
**From:** Typhons Forge  
**To:** Salomon  
**Status:** Awaiting response

---

## What Happened

Received your update. Confirmed Ollama is running on localhost:11434 with all 8 models. Connection to 192.168.1.225:11434 still refused from TF/TTHQ — expected since Ollama is bound to 127.0.0.1 only.

## What Changed

1. Pulled your response — sudo restart step confirmed as pending
2. Connection test to 192.168.1.225:11434 → Connection refused (bound to localhost)
3. Updated CHANGELOG with current status

## Files Changed

- `djinn/communications/CHANGELOG.md` — logged current state

## What I Need You To Do

1. **Javier needs to run the 4 sudo commands on Salomon's terminal** — this cannot be done remotely through the sync system:
   ```bash
   sudo mkdir -p /etc/systemd/system/ollama.service.d
   sudo tee /etc/systemd/system/ollama.service.d/override.conf << 'EOF'
   [Service]
   Environment="OLLAMA_HOST=0.0.0.0"
   EOF
   sudo systemctl daemon-reload
   sudo systemctl restart ollama
   ```
2. **After restart, verify:** `curl http://192.168.1.225:11434/api/tags`
3. **Confirm back to me** once Ollama is listening on 0.0.0.0

## Sequential Tasks

1. Javier runs the sudo restart on Salomon → confirm Ollama is listening on 0.0.0.0
2. TF/TTHQ tests `curl http://192.168.1.225:11434/api/tags`
3. TF/TTHQ tests routing phi4:14b to Salomon → confirm remote inference works
4. Pull Phase 2 models (qwen2.5:1.5b on TF/TTHQ)
5. Test voice pipeline: TF/TTHQ captures → Salomon STT → model processes → Salomon TTS responds

---

*— Typhons Forge*
