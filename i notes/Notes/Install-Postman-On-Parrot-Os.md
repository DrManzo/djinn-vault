---
subject: technology/software/postman/installation/parrot-os
tags:
  - technology/software/postman/installation/parrot-os
created: 2026-05-23
source: Perplexity export
---

# Install Postman on Parrot OS

## Summary
This note provides detailed instructions for installing Postman on Parrot OS, a Debian-based operating system.

## Key Points
- **Option 1 – Using Snap (easiest)**
- **Option 2 – Manual install (no Snap)**

## Details
### Option 1 – Using Snap (easiest)
Parrot does not always ship with Snap enabled, so we set it up first.

**Steps:**
1. Update the package list:
   ```bash
   sudo apt update
   ```
2. Install `snapd`:
   ```bash
   sudo apt install snapd
   ```
3. Enable and start `snapd.apparmor` service:
   ```bash
   sudo systemctl enable --now snapd.apparmor
   sudo systemctl enable --now snapd
   ```
4. Log out and back in (or reboot) once `snapd` is installed.
5. Install Postman using Snap:
   ```bash
   sudo snap install postman
   ```

After that, you should find “Postman” in your application menu, or you can run it from the terminal with:

```bash
postman
```

Snap is recommended by Postman itself because the package bundles all required libraries.

### Option 2 – Manual install (no Snap)
If you prefer not to use Snap, you can download and unpack the official Linux build.

**Steps:**
1. Download the latest Linux x64 tarball from the [Postman Downloads](https://www.postman.com/downloads/) page.
2. Move to your Downloads folder and unpack it into `/opt`:
   ```bash
   cd ~/Downloads
   sudo tar -xzf Postman-linux-x64-*.tar.gz -C /opt
   ```
3. If the extracted folder name isn’t `Postman`, rename it:
   ```bash
   sudo mv /opt/Postman-linux-x64 /opt/Postman # only if needed
   ```
4. Create a symlink so `postman` runs from the terminal:
   ```bash
   sudo ln -sf /opt/Postman/Postman /usr/local/bin/postman
   ```
5. Start Postman with:
   ```bash
   postman &
   ```
6. (Optional) Add a desktop launcher so it shows in the menu:
   ```bash
   nano ~/.local/share/applications/postman.desktop
   ```
   Paste this into the file (adjust paths only if you used a different install directory):
   ```text
   [Desktop Entry]
   Type=Application
   Name=Postman
   Exec=/usr/local/bin/postman
   Icon=/opt/Postman/app/resources/app/assets/icon.png
   Comment=Postman API Client
   Categories=Development;IDE;
   Terminal=false
   ```
7. Update the desktop database or just log out and back in; Postman should appear in your launcher/menu.

## References
- [Snapcraft](https://snapcraft.io/)
- [Tecmint](https://www.tecmint.com/)
- [Gist.github](https://gist.github.com/)

## Related
- [[Linux-Basics]] — Basic Linux commands and setup
- [[Postman-Guide]] — Comprehensive guide to using Postman