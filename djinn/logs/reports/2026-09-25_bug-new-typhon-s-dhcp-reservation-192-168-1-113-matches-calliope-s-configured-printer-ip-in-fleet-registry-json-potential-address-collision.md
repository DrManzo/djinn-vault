---
title: Bug Report — New-Typhon's DHCP reservation (192.168.1.113) matches Calliope's configured printer IP in fleet-registry.json -- potential address collision
agent: Claude
date: 2026-09-25
severity: high
status: open
tags: [djinn, bug, Network / DHCP (Salomon router, Calliope, new-Typhon) -- unresolved, needs Javier to check the router's reservations and Calliope's actual current IP]
related: [[bugs]] | [[build-log]]
---

# Bug Report — New-Typhon's DHCP reservation (192.168.1.113) matches Calliope's configured printer IP in fleet-registry.json -- potential address collision

**Date:** 2026-09-25 09:49
**Agent:** Claude
**System:** Network / DHCP (Salomon router, Calliope, new-Typhon) -- unresolved, needs Javier to check the router's reservations and Calliope's actual current IP
**Severity:** high
**Status:** open

---

## Root Cause

Found while setting up hellhound's trusted-ips.txt and fleet-registry.json on new-Typhon: ~/.config/forge/fleet-registry.json (live file, dated 2026-09-05) lists Calliope's api_url/ui_url as http://192.168.1.113:7125 -- the exact IP new-Typhon's own DHCP reservation (tied to its NIC MAC) just claimed earlier this same migration session. At the moment of discovery nothing answers on 192.168.1.113:7125 (no Moonraker/printer response), so there is no LIVE conflict right now -- Calliope appears to be either powered off or already silently reassigned to a different address. But this is exactly the kind of landmine that breaks silently: if Calliope's own network stack still expects .113 (a router-level static reservation, or just its last-known DHCP lease) and it reconnects while Typhon is holding that address, one of the two loses the IP -- and either way, forge-print-monitor/shop-dashboard/anything reading fleet-registry.json would be silently pointed at the wrong host, or Calliope's actual printer traffic could hit new-Typhon's SSH/other ports instead. Also found: trusted-ips.txt's own comment already flagged '.113 -- currently using Typhon's old lease' for Calliope, meaning this exact ambiguity existed even before today's migration and was already a known loose thread, not something this migration introduced from scratch -- just surfaced and made more permanent by Typhon's now-stable MAC-based reservation.

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
