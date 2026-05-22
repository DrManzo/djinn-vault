---
subject: 3D Print Process — Custom Parts
tags: [djinn, printer, process]
created: 2026-05-21
---

# Process: Designing and Printing a Custom Part

Repeatable workflow for any custom part going from idea → printed object. Written from the Puffco Proxy bubbler project as the first run-through.

---

## Stack

| Role | Tool | Notes |
|------|------|-------|
| CAD (prototype) | Tinkercad (browser) | tinkercad.com — free, no install |
| CAD (final) | Fusion 360 | Free personal license, download required |
| Slicer | OrcaSlicer | AppImage — install once on Salomon |
| Printer control | Moonraker API | http://192.168.1.113:7125 |
| File transfer | Moonraker upload or SD card | API preferred |

---

## Step 1 — Measure Before Designing

If you have calipers: measure the mating part (OD, ID, depth, joint size).

If no calipers: use the **fit-test collar method**:
1. Design a simple ring (10mm tall) at the expected ID
2. Print 3 variants: ID -0.5mm, nominal, +0.5mm
3. Test fit — pick the one that slides with light resistance
4. Use that confirmed ID in the real design

**Clearance rule:** Add 0.2–0.3mm to any socket/sleeve that needs to slide on. Printed tolerances are tight.

---

## Step 2 — Design in Tinkercad (Prototype)

1. Open tinkercad.com → New Design
2. Build geometry using primitives (cylinders, holes, tubes)
3. For a sleeve: cylinder (OD) minus cylinder (ID) = tube wall
4. Export → Download → `.stl`

**Tips:**
- Orient the model so layer lines run parallel to stress direction
- Keep walls ≥ 2mm for structural parts
- For watertight sections: ≥ 4 perimeter walls in slicer

---

## Step 3 — Slice in OrcaSlicer

**Install OrcaSlicer (first time only):**
```bash
# Download AppImage from github.com/SoftFever/OrcaSlicer/releases
chmod +x OrcaSlicer*.AppImage
./OrcaSlicer*.AppImage
```

**Slicer settings for prototypes (PLA):**
| Setting | Value |
|---------|-------|
| Layer height | 0.3mm (draft) |
| Infill | 20% |
| Walls | 3 perimeters |
| Bed temp | 60°C |
| Hotend temp | 215°C |
| Supports | Off (design to avoid) |

**For final watertight pieces (PETG/ASA):**
| Setting | Value |
|---------|-------|
| Layer height | 0.15mm |
| Infill | 40% |
| Walls | 4–5 perimeters |
| Bed temp | 70°C (PETG) |
| Hotend temp | 235°C (PETG) |

Export: `.gcode`

---

## Step 4 — Send to Printer

**Via Moonraker API (preferred):**
```bash
PRINTER_IP=192.168.1.113

# Upload gcode
curl -X POST http://$PRINTER_IP:7125/server/files/upload \
  -F "file=@/path/to/file.gcode" \
  -F "path=gcodes"

# Start print
curl -X POST http://$PRINTER_IP:7125/printer/print/start \
  -H "Content-Type: application/json" \
  -d '{"filename": "file.gcode"}'

# Check status
curl http://$PRINTER_IP:7125/printer/objects/query?print_stats
```

**Via Telegram (once wired):**
```
/print filename.gcode
/print_status
```

---

## Step 5 — Test and Iterate

1. Test fit immediately after print cools
2. Note what changed (ID too tight → +0.5mm next run)
3. Log the result in the project's Print Log table
4. Repeat until fit is correct, then move to final material

---

## Material Selection

| Material | Use | Heat Resistance | Notes |
|----------|-----|-----------------|-------|
| PLA | Prototypes only | ~60°C | Cheap, easy, warps near heat |
| PETG | Final structural | ~80°C | Good for sleeves, mouthpieces |
| ASA | Near-heat parts | ~100°C | Needs enclosure to print well |
| PC | Highest heat | ~120°C | Hard to print, high-temp hotend |

For water path parts: use glass tube insert regardless of filament. Plastic + water + heat = leaks and off-gassing over time.

---

## Djinn Integration

- Project notes live in `djinn/projects/`
- Print jobs logged in project's Print Log table
- Slicer profiles saved in `djinn/printer/config/`
- STL/gcode files referenced in `djinn/printer/models/`

---

*— Claude*
