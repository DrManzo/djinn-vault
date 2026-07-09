#!/bin/bash
# Run once on Typhon to set up Djinn Print agent.
set -e

echo "=== Djinn Print Agent — Typhon Setup ==="

# Pull model
echo "Pulling qwen2.5-coder:7b..."
ollama pull qwen2.5-coder:7b

# Python deps
echo "Installing Python deps..."
pip3 install --user ollama requests

# Verify Moonraker reachable
echo "Checking Moonraker..."
curl -s http://192.168.1.113:7125/printer/info | python3 -c \
    "import json,sys; d=json.load(sys.stdin); print('Printer:', d.get('result',{}).get('hostname','?'))"

echo ""
echo "Done. Run with:"
echo "  python3 print_agent.py"
echo "  python3 print_agent.py 'make a 30mm ring, 5mm wall, 10mm tall'"
