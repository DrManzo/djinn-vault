---
subject: Puffco Proxy V2 Custom Bubbler
tags: [djinn, project, printer, active]
created: 2026-05-21
status: active
owner: Claude + Javier
phase: prototype-fit-test
---

# Project: Puffco Proxy V2 Custom Bubbler

Custom 3D-printed mini bubbler attachment for the Puffco Proxy V2 concentrate vaporizer.

---

## Goal

Design and print a mini bubbler that slides onto the Proxy V2 body, provides water filtration, and fits the 14mm joint connection at the top.

---

## Hardware Audit

| Item | Status | Notes |
|------|--------|-------|
| Ender-3 V3 Plus | ✅ Ready | 192.168.1.113, Moonraker live |
| PLA filament | ✅ Loaded | Fine for prototype fit-test only |
| PETG or ASA filament | ❌ Not on hand | Required for final piece (heat + water) |
| Calipers | ❌ Not on hand | Need to confirm Proxy body OD before final design |
| Slicer software | ❌ Not installed | Install OrcaSlicer AppImage on Salomon |
| CAD software | ⚠️ Unconfirmed | Use Tinkercad (browser, no install) for prototype |
| Fusion 360 | ❌ Not installed | Needed for final bubbler design with curves |

---

## Known Dimensions (Proxy V2 — unverified, calibrate with fit-test)

| Measurement | Value | Source |
|-------------|-------|--------|
| Body OD | 40.6mm nominal | Element Vape published spec — verify with gauge print |
| Body height | 71mm | Element Vape published spec |
| Top joint | 14mm female (on device) | Standard |

---

## Prototype Strategy

Prototype in PLA to confirm fit. Final piece in PETG/ASA + glass tube water chamber insert.

### Phase 1 — Fit Test (current)

Print a 10mm collar ring at multiple IDs to lock in the Proxy body diameter.

**Collar specs:**
- OD: 30mm
- ID: 22mm (starting point — print at 21.5 / 22.0 / 22.5mm variants)
- Height: 10mm
- Layer height: 0.3mm, 20% infill, no supports

**Pass condition:** Proxy body slides in with light resistance — not loose, not forced.

### Phase 2 — Bubbler Body Prototype (PLA)

Once fit is confirmed:
- Sleeve section (fits over Proxy body, ~30mm tall)
- Water chamber (simple cylinder, no internal downstem yet)
- Mouthpiece angled ~45°
- No water path in prototype — just geometry and ergonomics

### Phase 3 — Final Piece (PETG/ASA)

- Full water path with downstem
- Glass tube insert for water chamber
- Sealed with XTC-3D epoxy if needed

---

## Process

See `djinn/printer/config/process-3d-print.md` for the full workflow.

---

## Print Log

| Job | File | Phase | Material | Result | Date |
|-----|------|-------|----------|--------|------|
| — | — | — | — | — | — |

---

## Blockers

1. **Slicer not installed** — install OrcaSlicer before first print
2. **No calipers** — fit-test collar approach compensates for this
3. **PLA only** — acceptable for prototype, order PETG/ASA for final

---

*— Claude*
