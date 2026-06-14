---
subject: 3d-printing/models/benchmark-ender-3-v3-plus
tags:
  - 3d-printing/calibration
  - 3d-printing/test-suite
  - 3d-printing/quality-assurance
created: 2026-06-14
source: Perplexity export
---

# Ender 3 V3 Plus — Full Benchmark Suite (PLA)

## Summary
This note provides a structured test plan for benchmarking an Ender 3 V3 Plus using PLA filament, covering foundational to advanced calibration and quality tests.

## Key Points
- **Calibration Cube (20×20×20mm)**
- **Temperature Tower (180–230°C)**
- **First Layer / Large Flat Square (200×200mm)**
- **CNC Kitchen Extrusion Benchmark**
- **SpeedBoat Benchy** at 3 speeds
- **Vibration/Ringing Tower**
- **Overhang Tower (20–80°)**
- **Bridging Test**
- **Fine Detail / Torture Test**
- **Tolerance/Clearance Gauge**
- **Functional Parts Test**

## Details
### Phase 1 — Baseline Calibration

1. **Calibration Cube (20×20×20mm)**
   - Run first to check X/Y/Z dimensions with calipers.
   - Adjust steps-per-mm if needed.

2. **Temperature Tower (180–230°C)**
   - Find the best layer adhesion, stringing, and surface quality for PLA.
   - Use this temperature setting for other tests.

3. **First Layer / Large Flat Square (200×200mm)**
   - Critical for 300×300 bed stability.
   - Tests CR Touch mesh leveling and Z-offset consistency edge-to-edge.

### Phase 2 — Speed & Flow Limits

1. **CNC Kitchen Extrusion Benchmark**
   - The most important speed test for high-speed machines like the V3 Plus.
   - Finds your true max volumetric flow to avoid under-extrusion at high speeds.

2. **SpeedBoat Benchy** (run at 3 speeds: stock, medium, and max)
   - Compare ringing, bridging, and hull quality at each speed.
   - Photograph results for analysis.

3. **Vibration/Ringing Tower**
   - Validate Klipper's input shaping calibration after settling on a speed from the Benchy test.

### Phase 3 — Quality & Detail

1. **Overhang Tower (20–80°)**
   - Tune part cooling fan and print speed for clean overhangs.
   - PLA usually handles up to 60–65° without support.

2. **Bridging Test**
   - Increasing bridge lengths; tune bridge speed and fan to 100% for cleanest results.

3. **Fine Detail / Torture Test**
   - Tiny text, thin walls, small holes.
   - Shows the real resolution ceiling of your motion system and slicer profile.

### Phase 4 — Dimensional Accuracy & Tolerances

1. **Tolerance/Clearance Gauge**
   - Prints pins and holes with gaps from 0.1–0.5mm.
   - Tells you the minimum clearance needed for functional parts on your specific machine.

2. **Functional Parts Test**
   - A small hinge, snap fit, or threaded part.
   - Confirms real-world usability and production-readiness of flow rate/elephant foot settings.

## References
- [CNC Kitchen Extrusion Benchmark](https://cnc-kitchen.com/extrusion-benchmark/)
- [All3DP Ender 3 Test Print Collection](https://all3dp.com/ender-3-test-print-collection/)
- [Tom's Hardware Benchy Profile for Ender 3 V3 Family](https://www.tomshardware.com/how-to/benchy-prusa-i3-mk2s)

## Related
- [[Setting-Benchmarks-For-Ender-3-V3-Plus]] — calibration
- [[SpeedBoat-Benchy-Test]] — speed-testing
