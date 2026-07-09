---
title: Filament Test Protocol
tags: [printer, filament, test, protocol]
links: [FILAMENT-PROFILES, BENCHMARKS, PRINT-LOG, INTAKE]
updated: 2026-05-23
status: draft — being refined through use
---

# Filament Test Protocol

Standard test sequence to characterise a new filament on the Ender-3 V3 Plus.
Run this before using any new spool (new brand, new material type, or after any hardware change).
Results go into [[FILAMENT-PROFILES]]. Log each test print in [[PRINT-LOG]].

**Related:** [[FILAMENT-PROFILES]] | [[BENCHMARKS]] | [[INTAKE]] | [[PRINT-LOG]]

---

> **Status: Draft**
> This protocol grows as more filaments are tested. Each run may reveal what the test object needs to cover.
> The test object and sequence will be locked down once the first two different material types are profiled.

---

## When to Run

| Trigger | Run? |
|---------|------|
| New brand, same material (e.g. different PLA) | Yes |
| New material type (PETG, TPU, ABS, etc.) | Yes — full sequence |
| Same brand/material, new colour | Optional — spot check only |
| After nozzle replacement | Yes — flow calibration minimum |
| After extruder hardware change | Yes — full sequence |
| After major printer.cfg changes | Yes — at least temp tower |

---

## Test Sequence

### 1 — Temperature Tower
**Goal:** Find optimal hotend temp for this material.
**Object:** Temperature tower (print multiple temp zones in one object).
**What to look for:** Layer adhesion, surface quality, stringing between zones.
**Record:** Optimal temp range → [[FILAMENT-PROFILES]] entry.
**Time estimate:** ~45 min

### 2 — Retraction Calibration
**Goal:** Eliminate stringing with minimum retraction.
**Object:** Retraction tower or 2-post stringing test.
**What to look for:** Clean travel moves with no strings at minimum retraction distance.
**Record:** Retraction distance and speed → [[FILAMENT-PROFILES]] entry.
**Time estimate:** ~20 min

### 3 — Flow Calibration
**Goal:** Confirm actual extrusion matches expected flow (100% = correct wall thickness).
**Object:** Single-wall cube — measure actual wall thickness with calipers.
**Target:** 0.4mm ± 0.05mm wall thickness.
**Adjust:** Flow % in slicer until measurement is in spec.
**Record:** Final flow % → [[FILAMENT-PROFILES]] entry.
**Time estimate:** ~15 min

### 4 — Benchmark Print (Benchy or CRtestcube)
**Goal:** Confirm all settings work together on a known reference shape.
**Object:** `3DBenchy-Ender-3 V3 Plus_14m28.gcode` (quick) or `CRtestcube_Ender-3 V3 Plus_26m.gcode` (dimensional).
**Compare to:** [[BENCHMARKS#benchy--calibration-boat]] (PLA baseline).
**Record:** Result in [[PRINT-LOG]], note differences from PLA baseline.
**Time estimate:** 15–26 min

---

## Test Object (To Be Defined)

A single small object covering all key failure modes — ideally < 30 min print time.

**Requirements:**
- Stringing test (two tall posts or arch)
- Overhang test (30°, 45°, 60° steps)
- Bridge test (20mm+ unsupported span)
- Fine detail (small text or sharp corners)
- Dimensional reference (known-size feature for calipers)

**Candidates:**
- `CRtestcube` (dimensional, fast) — 26 min, already on printer
- `ksr_fdmtest_v4` (comprehensive) — 1h 58m, all shape types, already on printer
- Custom combined test object — to be designed when personal CAD is active

_Decision pending: run ksr_fdmtest_v4 as the comprehensive baseline, then evaluate if a shorter custom object is needed._

---

## Log Format

Each filament test run gets one [[PRINT-LOG]] entry per print in the sequence.
Tag each entry with `filament-test` in the Notes field.
After the full sequence, add or update the profile in [[FILAMENT-PROFILES]].
