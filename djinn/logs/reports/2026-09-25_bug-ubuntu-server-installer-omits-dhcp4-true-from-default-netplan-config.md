---
title: Bug Report — Ubuntu Server installer omits dhcp4:true from default netplan config
agent: Claude
date: 2026-09-25
severity: medium
status: fixed
tags: [djinn, bug, Typhon (Ubuntu Server install, netplan)]
related: [[bugs]] | [[build-log]]
---

# Bug Report — Ubuntu Server installer omits dhcp4:true from default netplan config

**Date:** 2026-09-25 08:40
**Agent:** Claude
**System:** Typhon (Ubuntu Server install, netplan)
**Severity:** medium
**Status:** fixed

---

## Root Cause

Fresh Ubuntu 26.04.1 Server install on new-Typhon brought up its ethernet interface with IPv6 SLAAC working automatically but no IPv4 lease at all -- the installer's generated netplan YAML for enp3s0 never set dhcp4: true. Cost ~30 min of troubleshooting before root cause was found (host was unreachable by LAN ping, reachable by nothing since it had no IPv4 to test with). Fixed by manually adding dhcp4: true and re-applying; Typhon then received its familiar DHCP-reserved 192.168.1.113 back.

---

## Symptom

<!-- Fill in: what the user or system observed -->

---

## Steps to Reproduce

1. <!-- steps -->

---

## Fix Applied

<!-- What was changed, where, and why -->

---

## Verification

<!-- How you confirmed the fix worked -->

---

## Rule / Lesson

> **Rule:** <!-- one sentence: what prevents this class of bug in the future -->

---

*— Claude, 2026-09-25*
