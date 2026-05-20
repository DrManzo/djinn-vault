---
id: 20260519-175052
created: 2026-05-19
type: permanent
title: Dual-Boot Linux Setup (Windows + Linux)
references:
  - [[Perplexity Chat Export 2026-05-19_17-50-52]]
links:
  - [[OpenVPN Setup on Kali Linux]]
  - [[HTB Lab Access]]
tags: [tech-setup, dual-boot, linux, windows, partitioning]
---

## Summary
Guide to setting up a dual-boot system with Windows and Linux, covering partition management, bootloader configuration, distribution selection, and post-installation setup. Addresses common issues like Windows Fast Startup interference and GRUB recovery.

## Key Points
- Disable Windows Fast Startup and Secure Boot before installation
- Shrink Windows partition via Disk Management to create unallocated space (50GB+ recommended)
- Use Rufus or Ventoy to create bootable USB installer
- GRUB bootloader handles OS selection; install to EFI partition
- Recommended distros for beginners: Ubuntu, Linux Mint, Fedora
- Kali Linux not recommended as primary daily driver; use VM or separate partition
- Backup all data before partitioning; dual-boot carries data loss risk

## Details

### Pre-Installation
1. Backup important files
2. Disable Fast Startup: Control Panel → Power Options → Choose what power buttons do
3. Disable Secure Boot in UEFI/BIOS
4. Shrink Windows partition: Disk Management → right-click C: → Shrink Volume
5. Create bootable USB with Rufus (GPT/UEFI mode)

### Installation
Boot from USB, select "Install alongside Windows" or manual partitioning. Create:
- `/` (root): 30-50GB ext4
- `/home`: remaining space ext4 (optional but recommended)
- `swap`: equal to RAM size (or swapfile post-install)
- EFI: use existing Windows EFI partition (do not format)

### Post-Installation
```bash
sudo apt update && sudo apt upgrade
sudo ubuntu-drivers autoinstall  # NVIDIA if applicable
sudo systemctl enable fstrim.timer  # SSD optimization
```

### Troubleshooting
- Windows not showing in GRUB: `sudo update-grub`
- GRUB missing: boot from USB, chroot, `grub-install /dev/sda`
- Time sync issues: `timedatectl set-local-rtc 1`
- WiFi not working: install proprietary drivers via additional drivers tool

## References
- Ubuntu Installation Guide: ubuntu.com/tutorials
- Rufus: rufus.ie
- Ventoy: ventoy.net
- Arch Wiki (dual-boot): wiki.archlinux.org/title/Windows_and_Arch_Linux

## Related
- [[OpenVPN Setup on Kali Linux]] — Kali can be installed as third OS or VM
- [[HTB Lab Access]] — Linux environment needed for cybersecurity work
- [[Fedora-IDE-Setup-Guide]]
- [[OpenVPN-Kali-Linux-Setup]]
- [[HTB-Lab-Access-Strategy]]
