---
title: Bug Report — Salomon machine-topology IP stale (.225 documented, actual .80)
agent: Claude
date: 2026-07-12
severity: medium
status: open
tags: [djinn, bug, docs/machine-topology]
related: [[bugs]] | [[build-log]]
---

# Bug Report — Salomon machine-topology IP stale (.225 documented, actual .80)

**Date:** 2026-07-12 02:53
**Agent:** Claude
**System:** docs/machine-topology
**Severity:** medium
**Status:** open

---

## Root Cause

CLAUDE.md and djinn/AGENTS.md list Salomon at 192.168.1.225, but Salomon's actual current LAN IP is 192.168.1.80 (confirmed live: this session's own Bash tool runs on Salomon, and 192.168.1.225 is unreachable/no-route while .80 matches the forge dashboard URL already in COMMS.md). Likely a DHCP lease change that was never back-filled into the docs — same class of drift as the prior Calliope-IP and Penelope-API-key findings.

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

*— Claude, 2026-07-12*
