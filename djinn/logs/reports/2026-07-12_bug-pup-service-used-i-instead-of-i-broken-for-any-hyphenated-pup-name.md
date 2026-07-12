---
title: Bug Report — pup@.service used %I instead of %i — broken for any hyphenated pup name
agent: Claude
date: 2026-07-12
severity: medium
status: fixed
tags: [djinn, bug, hellhound]
related: [[bugs]] | [[build-log]]
---

# Bug Report — pup@.service used %I instead of %i — broken for any hyphenated pup name

**Date:** 2026-07-12 04:48
**Agent:** Claude
**System:** hellhound
**Severity:** medium
**Status:** fixed

---

## Root Cause

The template unit's EnvironmentFile/Environment/Description/SyslogIdentifier all used systemd's %I specifier (unescaped — converts encoded dashes back to slashes) instead of %i (literal instance name). Invisible for the only pup ever run (name: gateway, no hyphen), fatal the moment a hyphenated name was used: EnvironmentFile resolved to hellhound-inbound/probe.env instead of hellhound-inbound-probe.env, a nonexistent nested path, causing the new pup@inbound-probe.service to fail to start every time with 'Failed to load environment files'. Fixed by replacing all %I with %i in the unit.

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
