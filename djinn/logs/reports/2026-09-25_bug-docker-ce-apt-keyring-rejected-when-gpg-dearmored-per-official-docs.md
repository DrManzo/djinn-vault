---
title: Bug Report — Docker CE apt keyring rejected when GPG-dearmored per official docs
agent: Claude
date: 2026-09-25
severity: low
status: fixed
tags: [djinn, bug, Typhon (Ubuntu Server, Docker CE apt repo setup)]
related: [[bugs]] | [[build-log]]
---

# Bug Report — Docker CE apt keyring rejected when GPG-dearmored per official docs

**Date:** 2026-09-25 08:43
**Agent:** Claude
**System:** Typhon (Ubuntu Server, Docker CE apt repo setup)
**Severity:** low
**Status:** fixed

---

## Root Cause

typhon-bootstrap.sh followed Docker's official install docs: download the repo GPG key and pipe through gpg --dearmor into /etc/apt/keyrings/docker.asc. On new-Typhon's apt/gpg version this produced a binary keyring that apt rejected as unsupported filetype / NO_PUBKEY, blocking docker-ce install entirely. Root cause found by direct byte comparison against Salomon's own working /etc/apt/keyrings/docker.asc, which is still the raw ASCII-armored PGP block -- never dearmored. Fixed by piping the downloaded key straight to the keyring file via tee instead of gpg --dearmor. Back-ported the fix into typhon-bootstrap.sh so future rebuilds don't hit this again.

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
