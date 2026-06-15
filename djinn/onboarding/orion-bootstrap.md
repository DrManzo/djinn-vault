# Orin Bootstrap — Djinn Node Setup

**Machine:** Orin (iMac, 192.168.1.176)
**Hardware:** Intel 8-core, 40GB RAM, 2TB storage
**OS:** macOS (fresh install)
**Role:** Large-model inference host, always-on storage node

Run these steps IN ORDER from a terminal on Orin.

---

## Step 1 — Homebrew + core tools

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

After install, follow the "Next steps" it prints (adds brew to PATH). Then:

```bash
brew install git python3 wget
```

Verify:
```bash
git --version && python3 --version
```

---

## Step 2 — Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Verify Ollama is running:
```bash
ollama list
```

Enable Ollama to accept remote connections (so Salomon can route to Orin):
```bash
# Add to ~/.zshrc or ~/.bash_profile:
export OLLAMA_HOST=0.0.0.0
```

Then restart Ollama:
```bash
launchctl stop com.ollama.ollama 2>/dev/null; ollama serve &
```

---

## Step 3 — Pull models (do these in order, largest last)

```bash
# ~900MB — fast, always useful
ollama pull nomic-embed-text

# ~8GB — phi4, familiar to djinn tools
ollama pull phi4:14b

# ~9GB — deepseek reasoning, better than 7b
ollama pull deepseek-r1:14b

# ~20GB — primary large model (pull overnight if needed)
ollama pull qwen2.5:32b
```

Verify all pulled:
```bash
ollama list
```

---

## Step 4 — Clone the vault

```bash
mkdir -p ~/Obsidian
git clone https://github.com/DrManzo/djinn-vault.git ~/Obsidian
```

---

## Step 5 — Install djinn tools

```bash
mkdir -p ~/.local/bin

# Copy tools from vault
cp ~/Obsidian/djinn/scripts/tools/djinn-local-report ~/.local/bin/
cp ~/Obsidian/djinn/scripts/tools/djinn-comms-auto ~/.local/bin/
chmod +x ~/.local/bin/djinn-local-report ~/.local/bin/djinn-comms-auto

# Add to PATH — add to ~/.zshrc:
export PATH="$HOME/.local/bin:$PATH"
source ~/.zshrc
```

---

## Step 6 — Configure OLLAMA_HOST for local use

On Orin, djinn tools should call localhost (not Salomon):

```bash
# Add to ~/.zshrc:
export OLLAMA_HOST=http://localhost:11434
```

---

## Step 7 — Verify connectivity

From Salomon, test that Orin's Ollama is reachable:
```bash
curl http://192.168.1.176:11434/api/tags
```

Should return JSON list of models.

From Orin, test a model call:
```bash
djinn-local-report --topic "orin-bootstrap-test" --no-commit
```

---

## Step 8 — Set up vault sync

```bash
# Add a cron job to pull vault every hour:
(crontab -l 2>/dev/null; echo "0 * * * * cd ~/Obsidian && git pull origin main >> /tmp/djinn-vault-sync.log 2>&1") | crontab -
```

---

## Step 9 — Heartbeat (optional, once Salomon deploys the service)

The heartbeat service will be configured by Salomon via QUEUE.md task.
Check HEARTBEAT-orin.md status in `~/Obsidian/djinn/communications/`.

---

## Verification checklist

- [ ] `brew --version` works
- [ ] `git --version` works
- [ ] `ollama list` shows all 4 models
- [ ] `curl http://localhost:11434/api/tags` returns JSON
- [ ] `curl http://192.168.1.176:11434/api/tags` works from Salomon
- [ ] `~/Obsidian` is cloned and `djinn/` directory exists
- [ ] `djinn-local-report --help` works
- [ ] `djinn-comms-auto --help` works
- [ ] `djinn-local-report --topic test --no-commit` generates a report

---

*— Claude, 2026-06-05 | Orin bootstrap doc*
