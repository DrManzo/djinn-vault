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

# Can I Install World of Warcraft on Linux?

## Summary
World of Warcraft can be installed and run on Linux using a Windows compatibility layer (Wine) and a launcher like Lutris, Bottles, or Faugus.

## Key Points
- **Install GPU drivers and 32-bit/Vulkan support.**
- **Use Wine (or a Wine frontend) and Lutris or another launcher.**
- **Follow community scripts for Battle.net and WoW installation.**

## Details
World of Warcraft has no official Linux build, but it runs well via Wine on most modern distributions when set up correctly.

### Basic Idea
The usual pattern involves:
1. Enabling 32-bit architecture and installing Wine from WineHQ.
2. Adding the Lutris repository and installing Lutris.
3. Using a community script in Lutris to install Battle.net and then WoW.

Players report that WoW (retail and Classic) runs "very well" on Linux with this route, although ray tracing support is lost.

### Recommended Approaches
1. **Lutris + Wine (most common):**
   - Enable 32-bit architecture.
   - Install Wine from WineHQ.
   - Add the Lutris repository and install Lutris.
   - Search for “Battle.net” or “World of Warcraft” in the community installers and click Install.
   - Let the script complete, then log into Battle.net and install WoW.

2. **Bottles or Proton-based setups:**
   - Create a gaming bottle with Bottles to install Battle.net inside it, then install WoW.
   - Use Steam/Proton by treating Battle.net as a "non-Steam game" and forcing Proton.

3. **Faugus Launcher (newer, “easy mode”):**
   - Install Faugus Launcher from Flathub.
   - Open the Battle.net installer with it.
   - Log in to Battle.net and install WoW like on Windows.

### Things to Watch Out For
- Ensure proprietary NVIDIA or up-to-date Mesa drivers and Vulkan (plus 32-bit libs) are installed for good performance.
- Use recent Wine-GE or Proton-GE builds for best compatibility.
- Consider using ext4 or btrfs partitions for game libraries to avoid odd permission issues with Flatpak setups.
- WoW itself works, but some Activision titles may have different anti-cheat systems.

## References
- [Install World of Warcraft Linux Lutris Wine](https://heds.nz/posts/install-world-of-warcraft-linux-lutris-wine/)
- [World of Warcraft on Linux via Lutris and Wine](https://linuxfordevices.com/articles/2023/10/09/world-of-warcraft-on-linux-via-lutris-and-wine.htm)
- [World of Warcraft Performance Dashboard](https://www.youtube.com/watch?v=NUjQDl1xzGs)

## Related
- [[gaming/linux/wine/installation]] — Detailed guide on setting up Wine.
- [[gaming/linux/launcher/lutris-guide]] — Comprehensive Lutris setup and usage.