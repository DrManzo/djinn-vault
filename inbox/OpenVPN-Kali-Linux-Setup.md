---
id: 20260519-174804
created: 2026-05-19
type: permanent
title: OpenVPN Setup on Kali Linux
references:
  - [[Perplexity Chat Export 2026-05-19_17-48-04]]
links:
  - [[HTB Lab Access]]
tags: [cybersecurity, openvpn, kali-linux, networking, vpn]
---

## Summary
Configuration and troubleshooting guide for OpenVPN client on Kali Linux, specifically for connecting to Hack The Box labs. Covers installation, configuration file setup, service management, common errors, and verification steps.

## Key Points
- Install via `sudo apt install openvpn` on Kali
- Configuration files (.ovpn) contain server address, certificates, and authentication details
- Run with `sudo openvpn --config file.ovpn` for foreground or `sudo systemctl start openvpn@client` for service
- Common issues: routing conflicts, DNS leaks, TUN/TAP device permissions, expired certificates
- Verify connection with `ip a` (tun0 interface), `ping` to HTB IP, and `curl ifconfig.me`
- Kill switch recommended to prevent IP leaks during pentesting activities

## Details

### Installation
```bash
sudo apt update && sudo apt install openvpn
```

### Configuration
Place .ovpn file in `/etc/openvpn/client/` or run directly. File contains server address, CA cert, client cert, key, and auth-user-pass directive. For HTB, download from lab access page.

### Connection Methods
Foreground: `sudo openvpn --config ~/Downloads/lab.ovpn`
Service: `sudo systemctl start openvpn@client` (requires config at `/etc/openvpn/client/client.conf`)
Auto-start: `sudo systemctl enable openvpn@client`

### Troubleshooting
- `RTNETLINK answers: File exists` — routing conflict, run `ip route flush table main` or use `--route-nopull`
- `TLS Error` — expired cert or wrong credentials, re-download .ovpn
- `TUN/TAP device not found` — `modprobe tun` or check permissions
- DNS not resolving — add `dhcp-option DNS` to config or use `systemd-resolved`

### Verification
```bash
ip a show tun0
ping 10.10.14.1
curl ifconfig.me
```

## References
- OpenVPN Documentation: openvpn.net
- Hack The Box: hackthebox.com
- Kali Linux Documentation: kali.org/docs

## Related
- [[HTB Lab Access]] — Target platform for VPN connection
- [[Dual-Boot Linux Setup]] — Kali installation environment
- [[HTB-Lab-Access-Strategy]]
- [[Dual-Boot-Linux-Setup]]
