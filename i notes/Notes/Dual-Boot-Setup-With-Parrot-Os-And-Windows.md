---
subject: technology/computer-security/dual-boot-setup
tags:
  - technology/security-dev-tools/parrot-os
  - technology/windows-11-dual-boot
  - technology/storage-allocation
created: 2026-05-23
source: Perplexity export
---

# Dual Boot Setup with Parrot OS and Windows

## Summary
A detailed analysis of allocating storage for a dual boot setup between Parrot OS Security Edition and Windows on an Omen 016 Ryzen 9 laptop.

## Key Points
- **200 GB Allocation**: More than enough, providing ample space for tools, wordlists, VMs, and logs.
- **100 GB Allocation**: Feasible but tight; requires careful management of resources to avoid running out of space.

## Details
For a dual boot setup on an Omen 016 Ryzen 9 laptop with Parrot OS Security Edition and Windows 11:

### Official Space Requirements
- **Parrot OS Security Edition**:
  - Minimum: 40 GB
  - Recommended: 40+ GB

### Why 200 GB Is Reasonable
- **Tool Installations**: Pre-installed pentesting tools, Burp Suite Pro, custom exploits.
- **Wordlists and Datasets**: SecLists, RockYou/SecLists.
- **Virtual Machines / Docker Containers**: Lab environments for testing.
- **Capture Files and Logs**: PCAP files, forensic disk images.
- **Dev Environments**: IDEs, SDKs, project repos.

### Recommended Partition Layout (200 GB)
| Partition | Size | Purpose |
| --- | --- | --- |
| `/boot/EFI` | 512 MiB | UEFI boot |
| `/` (root) | 60–80 GB | OS + tools |
| `/home` | ~120 GB | Projects, wordlists, captures, VMs |
| Swap (optional) | 8–16 GB | With 16+ GB RAM on a Ryzen 9 |

### One Thing to Watch
- **Secure Boot**: Disable in BIOS.
- **Fast Startup**: Turn off in Windows Disk Management.

### What If I Wanted to Be Stingy and Do 100 Only?
- **Official Minimum**: 40 GB, fresh install uses about 12 GB.
- **Real Concerns**:
  - SecLists alone: ~1 GB; full wordlist collections (RockYou+, custom combo lists): 10–20 GB.
  - Docker images for lab targets: 2–8 GB each — 3–4 containers, 20+ GB.
  - Captured PCAP files: Stack up quickly.
  - Dev toolchains: Python envs, Rust, Go, Node, Burp Suite Pro, VS Code with extensions: 10–15 GB.
  - Updates and package cache: Parrot/Debian apt cache alone can grow to several GB if not pruned regularly.

### Real-World 100 GB Split
| Partition | Size | Remaining |
| --- | --- | --- |
| `/boot/EFI` | 512 MB | ~99.5 GB |
| `/` root | 40 GB | ~59.5 GB |
| `/home` | ~59 GB | 0 |

### Verdict
- **200 GB**: Solid, future-proof allocation for sec/dev work.
- **100 GB**: Feasible but tight; requires disciplined management of resources.

---

## References
- [Parrot Security OS Documentation](https://parrotsec.org/docs/installation/manual-installation/)
- [Dual Boot with Windows 11](https://parrotsec.org/docs/installation/dualboot-with-windows/)
- [Community Frame Laptop Experience](https://community.frame.work/t/parrot-os-home-edition-5-1-on-the-framework-12th-gen-the-story-so-far/21648)

## Related
- [[Parrot-OS-Guide]] — Detailed guide for Parrot OS installation and setup.
- [[Windows-11-Dual-Boot]] — Tips for dual booting Windows 11 with other operating systems.