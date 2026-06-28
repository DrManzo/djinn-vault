---
subject: 3d-printing/models/puffco-proxy-redesign
tags:
  - 3d-printing/models/ender-3v3-plus - 3d-printing/design - 3d-printing/filament/types - 3d-printing/tuning/model
created: 2026-06-22
source: Perplexity export

---

# Convert Puffco Proxy v1 Bowl to 38.5mm Diameter

## Summary
The prompt details the conversion of a smoking pipe model from Google Drive into a functional 3D-printable adapter for the original Puffco Proxy v1, focusing on precise fitment and print settings.

## Key Points
- **Model Source**: [https://share.google/ZCm3WUM0Jc7tbprn8](https://share.google/ZCm3WUM0Jc7tbprn8)
- **Target Diameter**: 38.5mm inner diameter for the bowl/chamber interface
- **Tolerance**: ±0.2–0.3mm to account for FDM printing shrinkage
- **Filament Type**: Heat-resistant filament (HTPLA, ASA, or PETG-CF)
- **Wall Thickness**: ≥3mm at the seat for thermal mass and rigidity

## Details
The Puffco Proxy v1 has a 38.5mm inner diameter where the chamber seats against the glass via its O-rings. The outer body is 42mm in diameter, so ensure your design clears this if it slides over the base. The stock Proxy glass ID is 38.5mm ±0.5mm (O-ring compression), ensuring reliable sealing without binding.

### Specific Requirements
1. **Orientation**: Orient for maximum Z-strength at the bowl seat to avoid layer lines perpendicular to the sealing face.
2. **Chamfer/Lead-in**: Include a 0.5mm chamfer/lead-in at the entry for easier chamber insertion.
3. **Print Settings**:
   - Layer height: Adjust based on filament type and printer.
   - Infill: Standard infill (18-24%) to balance strength and print time.
   - Temperatures: Use heat-resistant settings, typically 250°C+ for HTPLA or ASA.
   - Print Orientation: Ensure the seat is oriented correctly with no layer lines perpendicular to the sealing face.

### Why 38.5mm?
The 38.5mm figure comes directly from measurements of the Proxy v1 glass attachment seat, ensuring a snug fit without binding. Printing at 38mm would be too loose; 38.7–38.8mm accounts for FDM shrinkage (~0.2–0.4%) and the O-ring's give.

### Related Notes
- [[LSAT-Comprehensive-Guide]] — For more on 3D printing and filament types.
- [[3d-printing/design/embossing]] — Tips on designing for 3D printing.

## References
- [Nemotron 3 Ultra](https://www.google.com/s2/favicons?sz=128&domain=nemotron.com)

---

This note captures the essential details needed to convert and print a functional Puffco Proxy v1 bowl adapter, ensuring it fits snugly with the original device.