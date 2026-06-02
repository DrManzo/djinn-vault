# Djinn Inventory — Real-Time

| | Typhon | Salomon |
|---|---|---|
| **Hostname** | Typhon | Djinn |
| **IP** | 192.168.50.113 | 192.168.1.225 |
| **GPU** | GTX 1650 Max-Q (4GB) | RTX 5060 Laptop (8GB) |
| **RAM** | 14GB (6GB used) | 29GB (4GB used) |
| **Disk** | 916GB (1% used) | 937GB (32% used) |
| **Uptime** | 20h 43m | 21m |
| **OS** | Ubuntu (User) | Ubuntu (Server) |

## Tools & Services

| Tool | Typhon | Salomon | Notes |
|------|--------|---------|-------|
| Ollama server | ✅ | ✅ (0.0.0.0:11434) | Remote access to Salomon from Typhon |
| voxtype (STT) | ✅ v0.7.2 | ✅ v0.7.2 (symlinked) | Synced via SSH |
| Piper TTS | ✅ (en_GB-alba-medium) | ✅ (`~/.local/bin/piper`) | Synced via SSH |
| Claude Code | ✅ v2.1.148 | ❌ | Not needed on Salomon (runs via web) |
| Docker | ❌ | ✅ (djinn-core-djinn) | Containerized Djinn core on Salomon |
| SSH server | ✅ (0.0.0.0:22) | ✅ | |
| Printer agent | ✅ (qwen2.5-coder:7b) | ❌ | Ender-3 at 192.168.1.113:7125 |
| djinn-voice script | ✅ `~/.local/bin/djinn-voice` | ❌ | Unified TTS/STT/test/listen/say |

## Ollama Models

| Model | Typhon | Salomon | Notes |
|-------|--------|---------|-------|
| qwen2.5:7b | ✅ | ✅ | Shared |
| qwen2.5-coder:7b | ✅ | ✅ | Shared |
| qwen2.5:1.5b | ✅ | ❌ | Typhon-only |
| phi4:14b | ✅ | ✅ | Shared |
| llama3.2-vision:11b | ✅ | ✅ | Shared |
| nomic-embed-text | ✅ | ✅ | Shared |
| deepseek-r1:8b | ✅ | ❌ | Typhon-only |
| deepseek-r1:7b | ❌ | ✅ | Salomon-only |
| llama3.2:3b | ✅ | ❌ | Typhon-only |
| mistral:7b | ❌ | ✅ | Salomon-only |
| qwen3.6 (23GB) | ❌ | ✅ | Salomon-only, largest model |

## Systemd Timers

| Timer | Typhon | Salomon | Interval |
|-------|--------|---------|----------|
| vault-sync | ✅ | ✅ | 2 min |
| vault-git-pull | ✅ | ❌ | 2 min |
| heartbeat | ✅ | ✅ | 1h (Typhon) / 5 min (Salomon) |
| djinn-daily | ❌ | ✅ | 08:00 daily |
| djinn-weekly | ❌ | ✅ | Sunday 20:00 |

## Connected Devices (Salomon — USB)

| Device | Type | USB ID | Mode | Notes |
|--------|------|--------|------|-------|
| Samsung Galaxy Tab S (S Pen) | Android tablet | 04e8:6860 | MTP | Serial R52T10BL3BV, Verizon, ~7.6GB media |
| Apple iPhone | Smartphone | 05ac:12a8 | AFC + tether | USB tether: `enx12a2d37a331b`, Salomon IP 172.20.10.3 |

**Tablet media backup:** `/home/drmanzo/device-backups/samsung-galaxy-tab/` (Salomon)
**Full device doc:** `machines/devices.md`

---

## Gaps — What Each Machine Needs

### Both complete — no critical gaps remaining

| Need | Status |
|------|--------|
| Piper TTS on Typhon | ✅ Installed |
| voxtype on Salomon | ✅ Symlinked |
| Heartbeat timer fix (Salomon) | ✅ Fixed to 1h |
| Voice pipeline end-to-end | ✅ Tested PASS on Typhon |

### Nice-to-haves
- Claude Code on Salomon (not critical — web Claude or Typhon SSH handles it)
- Better whisper model on Typhon (base → small/medium for accuracy)
- Printer auto-start systemd service

### Cross-machine pipeline (voice)
```
Typhon mic → voxtype STT → text → SSH/HTTP to Salomon →
  → Ollama phi4:14b → response → Piper TTS on Salomon →
  → WAV file written to vault → vault-sync picks up on Typhon → play
```
