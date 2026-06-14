---
subject: djinn/vault/tablet
tags:
  - development/tablet/obsidian/github
  - development/fleet/networking
  - development/lane-assignment
created: 2026-06-14
source: Perplexity export
---

# Development Tablet Setup

## Summary
This note outlines the setup process for a development tablet, integrating Obsidian and GitHub to ensure it functions as a full-fledged development device within the Djinn Vault ecosystem.

## Key Points
- The tablet is designated as an **Input / Command Terminal + Field Development** lane.
- It runs on the `192.168.1.x` subnet alongside Salomon, Typhon, and Orion.
- SSH access to the fleet is enabled for remote development tasks.
- Obsidian and GitHub are set up for local vault management.

## Details
The tablet has been configured as a full-fledged development device within the Djinn Vault ecosystem. Here’s how it was set up:

1. **Hardware & Fleet Position**: The Tablet sits on the same `192.168.1.x` subnet as Salomon (`225`), Typhon (`113`), and Orion (`176`). This allows for direct WiFi-direct API calls to all three devices without any tunneling.

2. **Lane Assignment**: The Tablet is designated as the **Input / Command Terminal + Field Development** lane, explicitly not Salomon's print lane, Claude's architecture lane, or Orion's long-inference lane. It serves as the physical device that Javier holds.

3. **S Pen Workflows → Djinn Pipeline**:
   - **Sketch → Media Ingest**: Via `djinn-media-ingest` on Salomon.
   - **Handwritten Notes → Vault**: Via Termux SSH pipe into the Clerk inbox.
   - **LSAT Diagrams → Vision Model**: Via Telegram + `llama3.2-vision:11b` on Salomon.

4. **Model Routing From Tablet**:
   - Quick ops / tool use: `Salomon` with `qwen2.5:7b`.
   - LSAT / deep reasoning: `Salomon` with `deepseek-r1:7b`.
   - Code: `Salomon` with `qwen2.5-coder:7b`.
   - Vision / sketch review: `Salomon` with `llama3.2-vision:11b`.
   - Heavy analysis: `Orion` with `llama3.3:70b`.
   - External research: Perplexity, Marcus lane.

5. **Pending Integration Work**:
   - Termux SSH key setup.
   - Obsidian Mobile GitHub sync to make the Tablet a real vault node rather than just a consumer device.

6. **Next Steps**:
   - Pull the vault on Salomon (`git pull`) so the file propagates.
   - Set up the Termux SSH keys.
   - Consider creating a Bash script for transferring necessary Vault files, ensuring Git and Obsidian are fully integrated.

## References
- [TABLET.md](https://github.com/DrManzo/djinn-vault/blob/main/djinn/machines/TABLET.md)
- [inventory.md](https://github.com/DrManzo/djinn-vault/blob/main/inventory.md)
- [devices.md](https://github.com/DrManzo/djinn-vault/blob/main/devices.md)
- [AGENTS.md](https://github.com/DrManzo/djinn-vault/blob/main/AGENTS.md)
- [INFRASTRUCTURE.md](https://github.com/DrManzo/djinn-vault/blob/main/INFRASTRUCTURE.md)

## Related
- [[Faust-Cli-Core-Adapters]] — similarity
- [[Equipment-And-Infrastructure-Setup-For-Meanas-Systems]] — similarity
