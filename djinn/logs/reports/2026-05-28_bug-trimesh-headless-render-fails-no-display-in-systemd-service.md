---
title: Bug Report — trimesh headless render fails — no DISPLAY in systemd service
agent: Claude
date: 2026-05-28
severity: medium
status: fixed
tags: [djinn, bug, djinn-discord-watcher]
related: [[bugs]] | [[build-log]]
---

# Bug Report — trimesh headless render fails — no DISPLAY in systemd service

**Date:** 2026-05-28 21:09
**Agent:** Claude
**System:** djinn-discord-watcher
**Severity:** medium
**Status:** fixed

---

## Root Cause

djinn-model-fetch uses trimesh scene.save_image() which calls pyglet/OpenGL and requires a display connection. The djinn-discord-watcher systemd service had no DISPLAY env var, causing every render attempt to fail with 'Cannot connect to None'. Xvfb is installed and works — the render succeeds under DISPLAY=:98.

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

*— Claude, 2026-05-28*
