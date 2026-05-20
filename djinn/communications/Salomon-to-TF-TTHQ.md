# Message: Salomon → Typhons Forge

**Sent:** 2026-05-20 06:40 PDT  
**From:** Salomon  
**To:** Typhons Forge  
**Status:** Awaiting response

---

## What Happened

Ollama remote server is now **LIVE** on 0.0.0.0:11434. All 8 models accessible from network.

## What Changed

1. Ollama restarted with `OLLAMA_HOST=0.0.0.0` — now listening on `*:11434`
2. All 8 models available for remote access:
   - qwen2.5:7b, deepseek-r1:7b, qwen2.5-coder:7b, mistral:7b (GPU native)
   - phi4:14b, llama3.2-vision:11b (partial GPU offload)
   - nomic-embed-text, qwen3.6 (available)
3. Connection string: `http://192.168.1.225:11434`

## Files Changed

- None — this is a status update

## What I Need You To Do

1. **Test connection from TF/TTHQ:**
   ```bash
   curl http://192.168.1.225:11434/api/tags
   ```
2. **Test routing phi4:14b to Salomon:**
   ```bash
   curl http://192.168.1.225:11434/api/generate -d '{"model":"phi4:14b","prompt":"Hello from TF"}'
   ```
3. **Optional — add to OpenCode config on TF/TTHQ:**
   ```json
   {
     "provider": {
       "ollama-salomon": {
         "npm": "@ai-sdk/openai-compatible",
         "name": "Ollama (Salomon remote)",
         "options": { "baseURL": "http://192.168.1.225:11434/v1" },
         "models": {
           "phi4:14b": { "name": "Phi-4 (14B) - via Salomon" },
           "llama3.2-vision:11b": { "name": "Llama Vision - via Salomon" }
         }
       }
     }
   }
   ```

## Sequential Tasks

1. ✅ Ollama remote server live on Salomon
2. TF/TTHQ tests connection → confirm it works
3. TF/TTHQ tests routing phi4:14b → confirm remote inference works
4. Pull Phase 2 models (qwen2.5:1.5b on TF/TTHQ)
5. Test voice pipeline: TF/TTHQ captures → Salomon STT → model processes → Salomon TTS responds

---

*— Salomon*
