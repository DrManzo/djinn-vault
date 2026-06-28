---
subject: gaming/linux/worldofwarcraft/installation
tags:
  - gaming/linux/compatibility/wine
  - gaming/linux/launcher/lutris
  - gaming/linux/launcher/bottles
  - gaming/linux/launcher/faugus
created: 2026-06-28
source: Perplexity export
---

# Can I Install World of Warcraft on Linux

## Summary
World of Warcraft can be installed and run on Linux using compatibility layers like Wine and launchers such as Lutris, Bottles, or Faugus.

## Key Points
- **Wine/Proton:** Use a Windows compatibility layer to run WoW.
- **Lutris:** A gaming manager that automates the setup process for Battle.net and WoW.
- **Bottles:** A GUI for Wine that simplifies running games in isolated environments.
- **Faugus Launcher:** A newer Flatpak app that wraps Wine and simplifies game installation.

## Details
To install World of Warcraft on Linux, follow these steps:

1. **Enable 32-bit Architecture:**
   - Install necessary drivers and 32-bit libraries to ensure compatibility with WoW.

2. **Install Wine (or a Wine Frontend):**
   - Use Lutris for an automated setup.
   - Alternatively, use Bottles or Steam/Proton for managing the Windows environment.

3. **Use Community Scripts:**
   - In Lutris, search for “Battle.net” or “World of Warcraft” and install them using a community script.
   - For Bottles, create a gaming bottle and install Battle.net inside it.

4. **Install WoW:**
   - Log into Battle.net and download WoW from the launcher.

## Things to Watch Out For
- **GPU Drivers & Vulkan:** Ensure you have up-to-date drivers for optimal performance.
- **Wine Version:** Use recent Wine-GE or Proton-GE builds for better compatibility.
- **File System:** Consider using ext4 or btrfs partitions for game libraries to avoid permission issues.

## References
- [Install World of Warcraft on Linux via Lutris and Wine](https://heds.nz/posts/install-world-of-warcraft-linux-lutris-wine/)
- [World of Warcraft on Linux Performance Dashboard](https://www.google.com/s2/favicons?sz=128&domain=us.forums.blizzard.com)
- [Does WoW's Anti-Cheat Conflict with Linux](https://www.reddit.com/r/linux_gaming/comments/zxi7t8/world_of_warcraft_on_linux/)

## Related
- [[Linux-Gaming-SOP]] — Step-by-step World of Warcraft install via Lutris and Wine.
- [[Wow-On-Linux-Performance-Dashboard]] — Tracking Wine-GE versions, Vulkan driver stability, and frame-rate benchmarks across common distributions.