---
subject: technology/software-architecture/ai-models/installation
tags:
  - ai/development/fedora/workstation
  - ai/models/performance-analysis
created: 2026-05-23
source: Perplexity export
---

# Ollama Model Installation on Fedora Workstation

## Summary
This note provides guidance on installing and running AI models, specifically the `qwen2.5-coder` model, on a Fedora workstation.

## Key Points
- The `qwen2.5-coder:32b` model is recommended for better performance but requires sufficient GPU memory.
- The `qwen2.5-coder:14b` model is easier to run and suitable as a fallback if the 32B model cannot be used.

## Details
To install Ollama on Fedora Workstation, you can use the following commands:

```bash
sudo dnf install ollama
```

For running specific models, use:

```bash
ollama pull qwen2.5-coder:14b
ollama run qwen2.5-coder:32b
```

If your system has enough memory and VRAM, `qwen2.5-coder:32b` is preferred for better coding quality. However, if you encounter issues with GPU memory, the 14B model can be used as a safer alternative.

## Hardware Considerations
Below is a script to audit your system's hardware capabilities:

```bash
#!/usr/bin/env bash
set -u

OUT="ollama_audit_$(hostname)_$(date +%Y%m%d_%H%M%S).txt"

exec > >(tee "$OUT") 2>&1

echo "=== OLLAMA / FEDORA LAPTOP AUDIT ==="
echo "Timestamp: $(date)"
echo

# OS Information
if [ -f /etc/os-release ]; then
 cat /etc/os-release
fi
uname -a
echo

# CPU Information
lscpu
echo

# Memory Information
free -h
echo "--- /proc/meminfo (top) ---"
grep -E 'MemTotal|MemFree|MemAvailable|SwapTotal|SwapFree|HugePages|AnonHugePages' /proc/meminfo || true
echo

# GPU/PCI Information
lspci | grep -Ei 'vga|3d|display' || true
echo

# Graphics Stack
echo "--- lsmod ---"
lsmod | grep -Ei 'nvidia|amdgpu|radeon|nouveau' || true
echo
echo "--- glxinfo renderer ---"
if command -v glxinfo >/dev/null 2>&1; then
 glxinfo -B || true
else
 echo "glxinfo not installed"
fi
echo

# NVIDIA Information
if command -v nvidia-smi >/dev/null 2>&1; then
 nvidia-smi
else
 echo "nvidia-smi not installed"
fi
echo

# AMD ROCm Information
if command -v rocminfo >/dev/null 2>&1; then
 rocminfo | sed -n '1,160p'
else
 echo "rocminfo not installed"
fi
echo
if command -v rocm-smi >/dev/null 2>&1; then
 rocm-smi || true
else
 echo "rocm-smi not installed"
fi
echo

# Vulkan Information
if command -v vulkaninfo >/dev/null 2>&1; then
 vulkaninfo --summary || true
else
 echo "vulkaninfo not installed"
fi
echo

# Storage Information
df -h /
echo
du -sh ~/.ollama 2>/dev/null || echo "~/.ollama not present"
echo

# Ollama Information
if command -v ollama >/dev/null 2>&1; then
 ollama -v || true
 echo
 ollama list || true
 echo
 systemctl is-active ollama 2>/dev/null || true
 systemctl status ollama --no-pager -n 30 2>/dev/null || true
else
 echo "ollama not installed"
fi
echo

# SELinux Information
if command -v getenforce >/dev/null 2>&1; then
 getenforce
else
 echo "getenforce not installed"
fi
echo

# Kernel/Drivers Information
rpm -qa | grep -Ei 'nvidia|cuda|rocm|amdgpu' | sort || true
echo

echo "=== DONE ==="
echo "Saved to: $OUT"
```

Save the script as `ollama-audit.sh` and run it to gather information about your system's capabilities.

## References
- [Fedora Documentation](https://docs.fedoraproject.org/en-US/quick-docs/ollama/)
- [Ollama Model Library](https://ollama.com/library/qwen2.5-coder)
- [System Requirements for Ollama](https://localaimaster.com/blog/ollama-system-requirements)

## Related
- [[Fedora-Workstation-Ide-Recommendations-For-Ai-Development]] — ai development on fedora
- [[Faust-Cli-Core-Adapters]] — similar cli adapter usage
