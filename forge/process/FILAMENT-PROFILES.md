---
title: Filament Profiles
tags: [printer, filament, materials, profiles]
links: [INTAKE, BENCHMARKS, FILAMENT-TEST, PRINT-LOG]
updated: 2026-05-23
---

# Filament Profiles

Per-material settings tuned to the Ender-3 V3 Plus.
Each profile is established or refined by running the [[FILAMENT-TEST]] protocol.
Baseline settings are PLA — all other materials are deltas from that.

**Related:** [[INTAKE]] | [[FILAMENT-TEST]] | [[BENCHMARKS]] | [[PRINT-LOG]]

---

## Profile Template

```markdown
### Brand — Color — Material type

| Setting | Value |
|---------|-------|
| Hotend temp | °C |
| Bed temp | °C |
| Fan — layer 1 | OFF |
| Fan — layer 3+ | % |
| Retraction distance | mm |
| Retraction speed | mm/s |
| Flow | % |
| Pressure advance K | |
| Outer wall speed | mm/s |
| Max volumetric speed | mm³/s |
| Notes | |

Test result: [[PRINT-LOG#entry]]
Status: draft / established / refined
```

---

## PLA — Generic (Baseline)

All settings below are the machine baseline. Other profiles are tuned relative to this.

| Setting | Value |
|---------|-------|
| Hotend temp | 215°C |
| Bed temp | 60°C |
| Fan — layer 1 | OFF (M106 S0) |
| Fan — layer 3+ | 100% |
| Retraction distance | default (Creality profile) |
| Retraction speed | default |
| Flow | 100% |
| Pressure advance K | 0.042 |
| Outer wall speed | 40 mm/s |
| Inner wall speed | 50 mm/s |
| Travel speed | 150 mm/s |
| Notes | Proven on Benchy (185 layers clean) and cup geometry. Fan-off layer 1 is mandatory — early fan ramp causes nozzle_mcu EMI spike. See [[error_log]]. |

Test result: [[PRINT-LOG#2026-05-23--benchy-diagnostic-baseline]]
Status: ✅ Established 2026-05-23

---

## Materials To Profile

Run [[FILAMENT-TEST]] for each before using in real prints.

| Material | Status | Priority | Notes |
|----------|--------|---------|-------|
| PETG | ⏳ Not profiled | Medium | Higher temp, slower fan, may need bed adhesive |
| TPU | ⏳ Not profiled | Low | Flexible — slow speeds, direct drive recommended |
| ABS | ⏳ Not profiled | Low | Warping risk — enclosure needed |
| ASA | ⏳ Not profiled | Low | Like ABS, UV resistant |
| PLA+ | ⏳ Not profiled | Medium | Usually same as PLA, check stringing |

---

_Profiles added here as new filaments are tested. Each profile links back to its [[FILAMENT-TEST]] run and [[PRINT-LOG]] entry._
