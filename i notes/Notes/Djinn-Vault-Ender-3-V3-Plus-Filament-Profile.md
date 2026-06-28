---
subject: 3d-printing/filament/profiles/ender-3-v3-plus
tags:
  - 3d-printing/filament/profiles/ender-3-v3-plus/pla
  - 3d-printing/filament/profiles/puffco-recycler
created: 2026-06-28
source: Perplexity export
---

# Djinn Vault — Ender-3 V3 Plus Filament Profile Report

## Summary
This report provides detailed settings and recommendations for filament profiles, specifically focusing on PLA (Puffco Recycler) for the Creality Ender-3 V3 Plus printer.

## Key Points
- **Printer Model:** Creality Ender-3 V3 Plus with 0.4mm hardened steel nozzle.
- **Filament Type:** PLA (Puffco Recycler).
- **Nozzle Temperature Range:** 190°C to 230°C.
- **Initial Layer Height:** 0.20mm, Layer Height: 0.16mm.

## Details
The report outlines the thermal settings, flow properties, and specific print parameters for optimal PLA printing on the Ender-3 V3 Plus. The filament profile is based on a canonical PLA baseline with adjustments tailored to direct drive extruders.

### Thermal Settings
- **Nozzle Temp (print):** 220°C.
- **Nozzle Temp (initial layer):** 220°C.
- **Bed Temp:** 55°C for all plate types, with a vitrification temp of 60°C to prevent part softening.

### Flow & Material Properties
- **Filament Diameter:** 1.75mm.
- **Filament Density:** 1.24 g/cm³.
- **Flow Ratio:** 98% (0.98).
- **Max Volumetric Speed:** 15 mm³/s.
- **Initial Layer Line Width:** 0.50mm.

### Active Process Profile
The process profile is tuned for a 0.16mm layer height, with specific settings for wall loops and line widths to ensure robust prints.

### Layer & Wall Settings
- **Layer Height:** 0.16mm.
- **Initial Layer Height:** 0.20mm.
- **Wall Loops:** 4.
- **Outer Wall Line Width:** 0.42mm.
- **Inner Wall Line Width:** 0.45mm.

### Speed Settings
- **Outer Wall:** 60 mm/s.
- **Inner Wall:** 150 mm/s.
- **Sparse Infill:** 200 mm/s.
- **Internal Solid Infill:** 200 mm/s.
- **Top Surface:** 150 mm/s.
- **Bridge:** 50 mm/s.
- **Internal Bridge:** 150% of bridge speed.
- **Support:** 150 mm/s.
- **Support Interface:** 80 mm/s.
- **Initial Layer:** 40 mm/s.
- **Travel:** 400 mm/s.
- **Gap Fill:** 200 mm/s.

### Acceleration Settings
- **Default:** 4000 mm/s².
- **Outer Wall:** 2000 mm/s².
- **Inner Wall:** 3000 mm/s².
- **Top Surface:** 5000 mm/s².
- **Initial Layer:** 500 mm/s².
- **Travel:** 8000 mm/s².

### Retraction Settings
- **Retraction Length:** 0.6mm.
- **Retraction Speed & Deretraction Speed:** 40 mm/s each.
- **Minimum Travel Before Retract:** 2mm.
- **Z-Hop Height:** 0.12mm.
- **Z-Hop Type:** Auto Lift.

### Infill Settings
- **Sparse Infill Density:** 15%.
- **Infill Pattern:** Gyroid.
- **Infill Direction:** 45°.
- **Infill Wall Overlap:** 15%.
- **Min Sparse Infill Area:** 15 mm².

## References
- [filament_profile.json](https://drive.google.com/file/d/1qrv5KwuCUYY776tnypZyzuELg_FclSD2/view?usp=drivesdk)
- [process_profile.json](https://drive.google.com/file/d/1QtSanm3Ytazi1k5XaDy9AsDNeMsHrBbw/view?usp=drivesdk)

## Related
- [[LSAT-Comprehensive-Guide]] — General 3D printing guidelines and best practices.
- [[forge-slicer]] — Slicing software for the Ender-3 V3 Plus.