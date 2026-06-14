---
subject: 3d-printing/models/benchmark-3343/queue-management
tags:
  - 3d-printing/automation
  - 3d-printing/inventory-management
  - 3d-printing/models/ender-3v3-plus
created: 2026-06-14
source: Perplexity export
---

# 3D Print Queue & Inventory Automation for Ender 3v3 Plus

## Summary
This note outlines the key tools and practices for managing print queues, filament tracking, and job records in small-scale 3D printing operations, specifically focusing on the Ender 3v3 Plus model.

## Key Points
- **Queue Management Tools**: Moonraker's native `[job_queue]`, Spoolman, Obico.
- **Filament Tracking Accuracy**: Klipper's `filament_used` is sufficient for inventory tracking but requires conversion to grams using material density and diameter.
- **Metadata Schema**: De facto community schema from Moonraker's `print_stats`, Spoolman API, OctoPrint.

## Details
Small-scale 3D print operations require efficient queue management, accurate filament tracking, and detailed job record keeping. Here’s a structured approach:

### Queue Management Tools

1. **Moonraker `[job_queue]`**:
   - Native FIFO queue with REST + WebSocket support.
   - Auto-starts the next job after completion if `automatic_transition` is set to `true`.
   - Integrates seamlessly with Moonraker and can be managed via Salomon.

2. **Spoolman**:
   - Manages filament inventory, automatically deducting usage based on Klipper's `filament_used`.
   - Requires setup but provides robust tracking without cloud dependency.
   
3. **Obico (moonraker-obico)**:
   - AI failure detection and print event hooks.
   - Can call Python hooks for custom actions.

### Filament Tracking Accuracy

- **Klipper's `filament_used`**:
  - Reports filament extruded in millimeters, not grams.
  - Conversion formula: \( \text{grams} = \text{filament\_used\_mm} \times \pi \times (0.875)^2 \times \rho \div 1000 \).
  - `filament_used` only populates correctly when prints are started via the SD card print command or Moonraker/Mainsail interface.
  - For standard inventory deduction, Spoolman's integration handles mm to grams conversion automatically.

### Metadata Schema

- **Standard Job Record**:
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
    "thumbnail_path": "/thumbs/dragon_base_v3.png",
    "moonraker_raw": { ... }
  }
  ```

## References
- [Klipper Discourse](https://klipper.discourse.group/t/printer-print-stats-filament-used-always-returns-0/21041)
- [Math MIT](https://math.mit.edu/~djk/calculus_beginners/chapter00/section02.html)

## Related
- [[Filament-Recommendations-For-Ender-3v3-Plus]] — filament recommendations
- [[Djinn-3d-Printer-Overview-And-Filament-Recommendations]] — related automation tools
