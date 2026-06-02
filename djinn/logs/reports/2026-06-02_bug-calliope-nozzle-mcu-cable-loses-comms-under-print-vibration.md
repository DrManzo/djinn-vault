---
title: Bug Report — Calliope nozzle_mcu cable loses comms under print vibration
agent: Claude
date: 2026-06-02
severity: high
status: fixed
tags: [djinn, bug, calliope]
related: [[bugs]] | [[build-log]]
---

# Bug Report — Calliope nozzle_mcu cable loses comms under print vibration

**Date:** 2026-06-02 15:53
**Agent:** Claude
**System:** calliope
**Severity:** high
**Status:** fixed

---

## Root Cause

Sprite Pro extruder nozzle_mcu CAN/serial cable bundle goes intermittent under toolhead movement + thermal load. retransmit_seq skyrockets after ~500s, bytes_invalid spikes, Klipper triggers klippy_shutdown. Killed combined_jobs_2_3.gcode twice (jobs 000031, 000032) at 8-9min mark. Cable reseated at toolhead board and mainboard by Javier 2026-06-02. Monitor — if it recurs the cable assembly needs replacement.

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

*— Claude, 2026-06-02*
