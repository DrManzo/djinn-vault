---
subject: 3d-printing/filament/profiles/ender-3-v3-plus
tags:
  - 3d-printing/filament/profiles/ender-3-v3-plus/pla
  - 3d-printing/models/ender-3-pro
created: 2026-06-28
source: Perplexity export

---

# Djinn Vault — Ender-3 V3 Plus Filament Profile Report

## Summary
This report provides detailed settings and recommendations for PLA filament on the Creality Ender-3 V3 Plus, including thermal, flow, layer, speed, acceleration, retraction, infill, and cooling parameters.

## Key Points
- **Printer Model**: Creality Ender-3 V3 Plus with a 0.4mm hardened steel nozzle.
- **Filament Type**: PLA (Puffco Recycler).
- **Nozzle Temperature**: 220°C for print and initial layer.
- **Bed Temperature**: 55°C for all plate types.
- **Flow Ratio**: 98%.
- **Layer Height**: 0.16mm.

## Details
The report is based on the `Puffco Recycler PLA @Creality Ender3V3Plus` profile, which serves as a canonical baseline for the machine. Key settings include:
- **Thermal Settings**:
  - Nozzle Temp: 220°C (print and initial layer).
  - Bed Temp: 55°C.
  - Vitrification Temp: 60°C.

- **Flow & Material Properties**:
  - Filament Diameter: 1.75mm.
  - Filament Density: 1.24 g/cm³.
  - Flow Ratio: 98%.
  - Max Volumetric Speed: 15 mm³/s.
  - Slow Down Min Speed: 15 mm/s.

- **Layer & Wall Settings**:
  - Layer Height: 0.16mm.
  - Initial Layer Height: 0.20mm.
  - Wall Loops: 4.
  - Outer Wall Line Width: 0.42mm.
  - Inner Wall Line Width: 0.45mm.
  - Initial Layer Line Width: 0.50mm.

- **Speed Settings**:
  - Outer Wall: 60 mm/s.
  - Inner Wall: 150 mm/s.
  - Sparse Infill: 200 mm/s.
  - Internal Solid Infill: 200 mm/s.
  - Top Surface: 150 mm/s.
  - Bridge: 50 mm/s.
  - Internal Bridge: 150% (of bridge speed).
  - Support: 150 mm/s.
  - Support Interface: 80 mm/s.
  - Initial Layer: 40 mm/s.
  - Travel: 400 mm/s.
  - Gap Fill: 200 mm/s.

- **Acceleration Settings**:
  - Default: 4000 mm/s².
  - Outer Wall: 2000 mm/s².
  - Inner Wall: 3000 mm/s².
  - Top Surface: 5000 mm/s².
  - Initial Layer: 500 mm/s².
  - Travel: 8000 mm/s².

- **Retraction Settings**:
  - Retraction Length: 0.6mm.
  - Retraction Speed: 40 mm/s.
  - Deretraction Speed: 40 mm/s.
  - Minimum Travel Before Retract: 2mm.
  - Z-Hop Height: 0.12mm.
  - Z-Hop Type: Auto Lift.

- **Infill Settings**:
  - Sparse Infill Density: 15%.
  - Infill Pattern: Gyroid.
  - Infill Direction: 45°.
  - Infill Wall Overlap: 15%.
  - Min Sparse Infill Area: 15 mm².

- **Fan & Cooling**:
  - Not specified in the report.

## References
- [filament_profile.json](https://drive.google.com/file/d/1qrv5KwuCUYY776tnypZyzuELg_FclSD2/view?usp=drivesdk)
- [process_profile.json](https://drive.google.com/file/d/1QtSanm3Ytazi1k5XaDy9AsDNeMsHrBbw/view?usp=drivesdk)

## Related
- [[Ender-3-Pro-Printer-Specs]] — Printer specifications and setup.
- [[Creality-Ender-3-V3-Plus-Setup-Guide]] — Setup guide for the Ender 3 V3 Plus.