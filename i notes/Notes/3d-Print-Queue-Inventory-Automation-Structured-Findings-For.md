---
subject: 3d-printing/models/forge-upgrades
tags:
  - 3d-printing/automation
  - 3d-printing/inventory-management
  - 3d-printing/filament/tracking
  - cs/software-tools
created: 2026-06-14
source: Perplexity export
---

# 3D Print Queue & Inventory Automation: Structured Findings for Typhon's Forge

## Summary
This note compiles structured findings on queue management, filament tracking, and print record automation for a small-scale 3D printing operation using Moonraker, Spoolman, Obico, and other tools.

## Key Points
- **Queue Management:** Use Moonraker’s `[job_queue]` for FIFO tracking.
- **Filament Tracking:** Spoolman handles automatic usage deduction with `filament_used`.
- **Print Records:** Standard metadata schema includes job ID, order ID, filename, duration, and filament used.

## Details
### 1. Open-Source Queue-to-Completion Tracking Tools

**Primary Tool: Moonraker’s `[job_queue]`**
- Exposes a FIFO queue via REST endpoints.
- Supports `automatic_transition` for auto-starting next jobs after completion.

**Ecosystem Tools:**
- **Spoolman:** Manages filament inventory and automatic usage deduction.
- **Obico (moonraker-obico):** AI failure detection, print event hooks.
- **3D Print Log:** Cloud logging via Moonraker API key.
- **SimplyPrint:** Multi-printer queue + analytics.

For a one-printer self-hosted setup:
- **Moonraker job_queue + Spoolman + Obico** provides full-stack support with no cloud dependency.

### 2. `filament_used` Accuracy

- **Accuracy:** Sufficient for inventory tracking but not analytically precise.
- **Conversion Formula:**
  \[
  \text{grams} = \text{filament\_used\_mm} \times \pi \times (0.875)^2 \times \rho \div 1000
  \]
  Where \(\rho\) is material density (PLA ≈ 1.24 g/cm³, PETG ≈ 1.27, ABS ≈ 1.04).

- **Reliability:** Only populates correctly when prints are started via SD card or Moonraker/Mainsail interface.

### 3. Standard Metadata Schema for Print Job Records

**De Facto Community Schema:**
```json
{
 "job_id": "JOB-2025-06-08-001",
 "order_id": "ORD-0042",
 "filename": "dragon_base_v3.gcode",
 "model_name": "Dragon Mini Base",
 "started_at": "2025-06-08T21:00:00Z",
 "completed_at": "2025-06-08T23:45:00Z",
 "duration_seconds": 9900,
 "filament_used_mm": 4823,
 "filament_used_grams": 16.4,
 "material": "PLA+",
 "color": "Black",
 "spool_id": "SPOOL-007",
 "layer_count": 240,
 "outcome": "success",
 "failure_reason": null,
 "cancel_source": null,
 "thumbnail_path": "/thumbs/dragon_base_v3.png"
}
```

## References
- [Moonraker Documentation](https://moonraker.readthedocs.io/)
- [Spoolman Integration](https://github.com/spoolman/spoolman)
- [Obico Agent](https://github.com/moonraker-obico/moonraker-obico)

## Related
- [[3d-Print-Queue-Inventory-Automation-For-Ender-3v3]] — similarity 0.87
- [[Djinn-3d-Printer-Overview-And-Filament-Recommendations]] — filament tracking and recommendations
