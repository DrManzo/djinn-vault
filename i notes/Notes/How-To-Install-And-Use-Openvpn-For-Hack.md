---
subject: tech/networking/openvpn/installation-usage
tags:
  - tech/networking/htb-challenges
  - tech/security/vpn
created: 2026-05-20
source: Perplexity export
---

# How to Install and Use OpenVPN for Hack the Box Challenges

## Summary
This note provides step-by-step instructions on installing and using OpenVPN on Parrot OS to connect to Hack the Box (HTB) challenges.

## Key Points
- Install OpenVPN 3 Linux Client.
- Download HTB-specific `.ovpn` file.
- Connect via terminal or NetworkManager.
- Verify connection with `ping`.

## Details
To install and use OpenVPN for connecting to Hack the Box challenges on Parrot OS, follow these steps:

### 1. Install OpenVPN

Open a terminal and run:
```bash
sudo apt update
sudo apt install openvpn network-manager-openvpn network-manager-openvpn-gnome
```

If prompted, enable the service or restart NetworkManager.

### 2. Download HTB `.ovpn` File

- Log into your Hack the Box account.
- Go to "Profile" → "Lab Access / VPN settings."
- Choose your region/server and protocol (usually UDP 1337).
- Click “Download VPN” to get a file like `Javier.ovpn`.

Move this file to your Parrot home folder, e.g., `~/VPN/htb.ovpn`.

### 3. Connect Using Terminal

Assuming the `.ovpn` file is in `~/Downloads`, run:
```bash
cd ~/Downloads
sudo openvpn htb.ovpn
```

- Enter your sudo password if prompted.
- Keep this terminal window open; close it to disconnect.

After a few seconds, you should see lines ending with "Initialization Sequence Completed." You can verify the connection by running:
```bash
ping 10.10.14.1
```
If successful, you should receive replies (`time=... ms`).

### 4. Connect Using NetworkManager

- Import the profile from the command line:
  ```bash
  nmcli connection import type openvpn file ~/Downloads/htb.ovpn
  ```
- Click the network icon in Parrot’s panel → VPN → select your new HTB VPN and toggle it on.

Now you can connect/disconnect via the UI instead of using `sudo openvpn`.

## Additional Notes

### Nmap Port Scanning

To scan a specific port with Nmap:
```bash
nmap -p <port> <target>
```
Example: 
```bash
nmap -p 80 10.10.10.10
```

For multiple or range of ports, use:
- Specific ports:
  ```bash
  nmap -p 22,80,443 10.10.10.10
  ```
- Range of ports:
  ```bash
  nmap -p 1-200 10.10.10.10
  ```
- All TCP ports:
  ```bash
  nmap -p- 10.10.10.10
  ```

### Telnet Connection

To connect to a TCP port 23 (Telnet):
```bash
telnet <IP_or_hostname> 23
```
Example: 
```bash
telnet 10.10.10.10 23
```

## References
- [How to Install FREE VPN for Kali Linux - OPENVPN](https://www.youtube.com/watch?v=m1puwrKy_Vw)
- [How to Install FREE VPN on Linux (Ubuntu, Kali Linux, etc.)](https://www.youtube.com/watch?v=qqRf30bErMQ)
- [How to Scan a Port with Nmap](https://www.phoenixnap.com/kb/how-to-scan-a-port-with-nmap)
- [Telnet Default Port 23](https://www.netcomlearning.com/tutorials/what-is-telnet-and-how-does-it-work/)
  
## Related
- [[HTB-VPN-Guide]] — Detailed guide for HTB-specific setup.
- [[Nmap-Scanning-Guide]] — Comprehensive Nmap scanning techniques.
- [[Telnet-Usage-Guide]] — Telnet connection and usage instructions.