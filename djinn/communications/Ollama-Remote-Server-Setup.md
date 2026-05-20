# Ollama Remote Server — Salomon

**Set up:** 2026-05-20 06:15 PDT  
**Host:** Salomon  
**Status:** ⚠️ Requires manual sudo step — run the 4 commands below on Salomon

---

## Connection Details

| Setting | Value |
|---------|-------|
| **Host** | Salomon |
| **IP** | 192.168.1.225 |
| **Port** | 11434 |
| **Protocol** | HTTP (Ollama API) |
| **Base URL** | `http://192.168.1.225:11434` |

## Manual Setup Required (Run on Salomon)

Ollama is currently running as a system service. To enable remote access:

```bash
# Step 1: Create override directory
sudo mkdir -p /etc/systemd/system/ollama.service.d

# Step 2: Create override file
sudo tee /etc/systemd/system/ollama.service.d/override.conf << 'EOF'
[Service]
Environment="OLLAMA_HOST=0.0.0.0"
EOF

# Step 3: Reload and restart
sudo systemctl daemon-reload
sudo systemctl restart ollama

# Step 4: Verify it's listening on all interfaces
curl http://192.168.1.225:11434/api/tags
```

## How TF/TTHQ Connects

After the above is done, on TF/TTHQ:

```bash
# Test connection
curl http://192.168.1.225:11434/api/tags

# Set environment variable for Ollama to use remote server
export OLLAMA_HOST=192.168.1.225:11434

# Test pulling a model through Salomon
ollama pull phi4:14b
```

Or in OpenCode config on TF/TTHQ, add a second provider:

```json
{
  "provider": {
    "ollama-salomon": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Ollama (Salomon remote)",
      "options": {
        "baseURL": "http://192.168.1.225:11434/v1"
      },
      "models": {
        "phi4:14b": { "name": "Phi-4 (14B) - via Salomon GPU" },
        "llama3.2-vision:11b": { "name": "Llama Vision - via Salomon GPU" }
      }
    }
  }
}
```

## Available Models on Salomon

| Model | Size | GPU Status | Notes |
|-------|------|------------|-------|
| qwen2.5:7b | 4.7 GB | GPU native | Live lane |
| deepseek-r1:7b | 4.7 GB | GPU native | Deep reasoning |
| qwen2.5-coder:7b | 4.7 GB | GPU native | Code / dev |
| mistral:7b | 4.1 GB | GPU native | Creative writing |
| phi4:14b | 9.1 GB | Partial GPU offload | Notes / APA |
| llama3.2-vision:11b | 7.8 GB | GPU native | Vision |
| nomic-embed-text | 274 MB | GPU native | Embeddings |

## Security Notes

- Currently will be open on all interfaces (0.0.0.0) — no auth
- For production: add firewall rules
- Only expose on local network, not internet
- To restrict to TF only: `sudo ufw allow from 192.168.1.X to any port 11434`

## Troubleshooting

- If connection fails: `sudo systemctl status ollama`
- If models not showing: `ollama list` on Salomon
- If slow: check network latency `ping 192.168.1.225` from TF

---

*— Salomon*
