---
id: 20260519-174919
created: 2026-05-19
type: permanent
title: Hack The Box Lab Access & Strategy
references:
  - [[Perplexity Chat Export 2026-05-19_17-49-19]]
links:
  - [[OpenVPN Setup on Kali Linux]]
tags: [cybersecurity, hackthebox, pentesting, ctf, learning]
---

## Summary
Guide to accessing and navigating Hack The Box labs, including VPN connection, machine selection, enumeration methodology, and progression path from beginner to advanced. Covers tool recommendations, note-taking strategies, and common pitfalls.

## Key Points
- HTB requires OpenVPN connection to access lab network (10.10.x.x range)
- Start with "Starting Point" tier (free, guided machines) before moving to active machines
- Enumeration methodology: Nmap scan → service identification → vulnerability research → exploitation → privilege escalation
- Essential tools: Nmap, Gobuster/FFUF, Burp Suite, Metasploit, LinPEAS/WinPEAS
- VIP subscription ($14/mo) unlocks active machines and faster servers
- Note-taking critical for tracking findings, credentials, and techniques
- Common trap: spending too long on one vector; pivot when stuck

## Details

### Getting Started
1. Create account at hackthebox.com
2. Download .ovpn config from Access tab
3. Connect via OpenVPN (see [[OpenVPN Setup on Kali Linux]])
4. Complete "Starting Point" machines in order

### Enumeration Framework
```bash
# Initial scan
nmap -sC -sV -oA initial <target>
# Full port scan
nmap -p- -oA full <target>
# UDP scan
nmap -sU --top-ports 100 -oA udp <target>
# Web enumeration
gobuster dir -u http://<target> -w /usr/share/wordlists/dirb/common.txt
```

### Privilege Escalation
Linux: Check SUID binaries, sudo -l, cron jobs, writable files, kernel exploits
Windows: Check service permissions, AlwaysInstallElevated, token impersonation, unquoted paths

### Learning Resources
- HTB Academy (structured learning paths)
- IppSec YouTube videos (walkthroughs)
- 0xdf.gitlab.io (write-ups)
- HTB Discord community

## References
- Hack The Box: hackthebox.com
- HTB Academy: academy.hackthebox.com
- IppSec YouTube: youtube.com/c/ippsec

## Related
- [[OpenVPN Setup on Kali Linux]] — Connection prerequisite
- [[Dual-Boot Linux Setup]] — Kali environment for HTB work
- [[OpenVPN-Kali-Linux-Setup]]
- [[Dual-Boot-Linux-Setup]]
