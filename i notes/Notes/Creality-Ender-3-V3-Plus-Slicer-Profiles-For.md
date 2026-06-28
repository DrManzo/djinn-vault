---
subject: djinn/calliope-printing-pipeline
tags:
  - cs/3d-printing/profiles/pla
  - cs/3d-printing/profiles/petg
  - cs/3d-printing/printer-settings
created: 2026-06-28
source: Perplexity export
---

# Creality Ender-3 V3 Plus Slicer Profiles for Djinn Calliope Pipeline

## Summary
This note provides detailed profiles for the Creality Ender-3 V3 Plus (Calliope) across three use cases—Prototype, Production, and Quality—for both PLA and PETG materials. The profiles are designed to optimize print quality and efficiency.

## Key Points
- **Use Cases:** Prototype, Production, Quality
- **Materials:** PLA, PETG
- **Printer Settings:** Hotend, Bed Temperature, Layer Height, Infill, Fan Speed, Retraction

## Details
The profiles are structured into three tiers based on the intended use of the prints. Each tier has specific settings for hotend and bed temperatures, layer heights, infill percentages, fan speeds, retraction distances, and travel speeds.

### Prototype — PLA
- **Hotend:** 210–215°C
- **Bed:** 55–60°C
- **Layer Height:** 0.28mm
- **Walls:** 2
- **Infill:** 8% gyroid
- **Fan Layer 1:** OFF
- **Fan Layer 3+:** 100%
- **Outer Wall Speed:** 60 mm/s (speed priority 150%)
- **Travel Speed:** 150 mm/s
- **Retraction:** 6mm @ 25mm/s

### Production — PLA
- **Hotend:** 215°C
- **Bed:** 60°C
- **Layer Height:** 0.20mm
- **Walls:** 4
- **Infill:** 25% gyroid
- **Fan Layer 1:** OFF
- **Fan Layer 3+:** 100%
- **Outer Wall Speed:** 40 mm/s
- **Inner Wall Speed:** 50 mm/s
- **Retraction:** 6mm @ 25mm/s
- **Flow:** 100%
- **Pressure Advance K:** 0.042
- **Brim:** 8mm recommended

### Quality — PLA
- **Hotend:** 210°C
- **Bed:** 55°C
- **Layer Height:** 0.12mm
- **Walls:** 4
- **Infill:** 15–20% grid
- **Fan Layer 1:** OFF
- **Fan Layer 3+:** 100%
- **Outer Wall Speed:** 25 mm/s (accuracy priority 60%)
- **Retraction:** 6mm @ 25mm/s
- **Pressure Advance K:** 0.042

### Prototype — PETG
- **Hotend:** 230°C
- **Bed:** 70°C
- **Layer Height:** 0.28mm
- **Walls:** 2
- **Infill:** 8% gyroid
- **Fan Layer 1:** OFF
- **Fan Layer 3+:** 50%
- **Outer Wall Speed:** 40 mm/s
- **Travel:** 150 mm/s
- **Retraction:** 4mm @ 25mm/s

### Production — PETG
- **Hotend:** 235°C
- **Bed:** 70–75°C
- **Layer Height:** 0.20mm
- **Walls:** 4
- **Infill:** 25% gyroid
- **Fan Layer 3+:** 50%
- **Outer Wall Speed:** 35 mm/s
- **Retraction:** 4mm @ 25mm/s
- **Flow:** 100–102%

## References
- [FILAMENT-PROFILES.md](https://drive.google.com/file/d/1wUVXcvW2VS5_Ig0bOwCEfCQFQeIpVFjv/view?usp=drivesdk)
- [PRINTER-MANUAL.md](https://drive.google.com/file/d/1NTSpuxXlJ44oRlnm5e2D-vC6SKapAntR/view?usp=drivesdk)
- [nikkoindustries](https://www.nikkoindustries.com/blogs/news/best-ender-3-cura-profile-settings-for-perfect-3d-prints)
- [thingiverse](https://www.thingiverse.com/groups/ender3/forums/general/topic:36347)

## Related
- [[LSAT-Comprehensive-Guide]] — For more detailed printer setup guides
- [[djinn-research-request-pa-layer-redesign]] — Relevant research requests for the pipeline