---
title: "is the current version of ubuntu able to roon steam and xboxlive ?"
source: perplexity-pro
url: https://www.perplexity.ai/search/f3df0bfa-7232-40d4-a9e5-cc6fe3bd12c2
date: 2026-06-01
tags:
  - technology/software/linux
  - gaming/steam
  - gaming/xbox
  - ubuntu
---

# is the current version of ubuntu able to roon steam and xboxlive ?

Yes: current Ubuntu releases can run Steam very well, but they cannot run the native Xbox app or install Xbox/PC Game Pass titles directly; Xbox is limited to web/cloud streaming or remote play workarounds.
xbox
youtube
discourse.ubuntu

Ubuntu and Steam

Ubuntu 24.x is widely used for gaming and works fine with the native Linux Steam client once installed from the official .deb (or via Ubuntu’s store, snap, or flatpak) and configured with Proton for Windows games. Community testing of dozens of titles on Ubuntu 23.10–24.04 shows that most Steam games either work out of the box or need only minor tweaks, especially with Proton and a reasonably recent GPU/driver stack.
discourse.ubuntu

On a fresh Ubuntu install you would typically:

Enable the “Multiverse” repository and install the steam package, or download Valve’s .deb installer.

Turn on Steam Play/Proton in Steam settings for all titles to run Windows-only games.

Ensure up‑to‑date graphics drivers (Mesa for AMD/Intel, proprietary for NVIDIA) for good performance.
discourse.ubuntu

Ubuntu and Xbox / Xbox Live

Microsoft does not ship the Xbox app or PC Game Pass client for Linux, so you cannot natively install Game Pass games or use the Windows Xbox app on Ubuntu. The common approaches on Linux are:
steamcommunity
+1

Xbox Cloud Gaming (xCloud): Use a supported browser (often Microsoft Edge) to stream Game Pass games via the web interface on xbox.com/play; guides show this working on Ubuntu and other Linux distros, with controller support configured at the browser/Flatpak level.
youtube

Remote play / streaming: Stream from an Xbox console or a Windows PC that is running the Xbox app to your Ubuntu machine using third‑party clients or browser-based solutions.
steamcommunity

These rely on cloud or LAN streaming, not local installation of Xbox titles on Ubuntu, and require a solid internet connection for acceptable gameplay.
youtube
steamcommunity

If you tell me which GPU you’re using (NVIDIA vs AMD/Intel), I can walk you through an Ubuntu‑specific setup for Steam and Xbox cloud/remote play on your hardware.

## Related
- [[Ubuntu-and-Steam]] — gaming capabilities on Ubuntu
- [[Ubuntu-and-Xbox]] — limitations and workarounds for Xbox on Ubuntu
