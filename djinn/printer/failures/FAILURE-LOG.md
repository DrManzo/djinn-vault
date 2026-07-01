# Print Failure Log — Callie (Ender-3 V3 Plus)

Each entry: one incident. Append only.

---

### 2026-05-25 — Temp Tower v1 (temp-tower.gcode)
**Slicer:** PrusaSlicer 2.9.4
**Root Cause:** Raw Klipper gcode (M190/M109/G28) — Creality Nebula firmware requires `START_PRINT`/`END_PRINT` macros
**Symptoms:** Printer showed "printing" state but never moved. No heat, no homing.
**Resolution:** Re-sliced with Creality macro start/end gcode.
**Prevention:** Always wrap PrusaSlicer output with Creality macros.

---

### 2026-05-25 — Temp Tower v2 (temp-tower-fixed.gcode)
**Slicer:** PrusaSlicer 2.9.4 + M109 injection
**Root Cause:** Creality firmware blocks `M109` (wait for temp) commands mid-print. Required `M104` (set temp, don't wait) instead.
**Symptoms:** Printed successfully but uniform temperature — all temp zones printed at the initial 205°C. M109 commands logged in gcode but firmware never executed them.
**Resolution:** Switched to `M104 S<temp>` for non-blocking temperature changes.
**Prevention:** Never use M109 for mid-print temperature changes on Creality firmware. Use M104 or SET_HEATER_TEMPERATURE + TEMPERATURE_WAIT.

---

### 2026-05-25 — Temp Tower v3 attempt (temp-tower-klipper.gcode)
**Slicer:** PrusaSlicer 2.9.4 + SET_HEATER_TEMPERATURE injection
**Root Cause:** Firmware restart (`printer/firmware_restart`) during active print — corrupted Klipper state (temperature targets zeroed, file handle orphaned). Touchscreen UI app crashed.
**Symptoms:** Print started but extruder target was 0°C. Ran 17% on residual heat before cooling failed. Could not cancel remotely — touchscreen app crashed, API cancel blocked.
**Resolution:** Power cycle at printer.
**Prevention:** Never restart Klipper firmware while a file is loaded. Always cancel print first, wait for SD idle, then restart if needed.

---

### Template for future entries
```
### YYYY-MM-DD — [Print name]
**Root Cause:**
**Symptoms:**
**Resolution:**
**Prevention:**
```
=== FAILURE DETECTED ===
  File: combined_flipped_creality.gcode
  Progress: 0%
  Transition: printing → cancelled
  Time: 2026-05-27 02:12:55 UTC
=== FAILURE DETECTED ===
  File: combined_flipped_creality.gcode
  Progress: 0%
  Transition: printing → cancelled
  Time: 2026-05-27 05:55:05 UTC
=== FAILURE DETECTED ===
  File: combined_flipped_creality.gcode
  Progress: 0%
  Transition: printing → cancelled
  Time: 2026-05-27 06:01:07 UTC
=== FAILURE DETECTED ===
  File: 2holster_mixvases_creality.gcode
  Progress: 99%
  Transition: printing → error
  Time: 2026-05-27 15:45:39 UTC
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== ERROR STATE ===
  Message: {"code":"key95","msg":"Must home axis first: 8.000 146.290 160.901 [69038.435]", "values":[8.000, 146.290, 160.901, 69038.435]}
=== FAILURE DETECTED ===
  File: javi_vase_creality.gcode
  Progress: 0%
  Transition: printing → cancelled
  Time: 2026-05-27 19:35:56 UTC
=== FAILURE DETECTED ===
  File: 2holster_mixvases_creality.gcode
  Progress: 0%
  Transition: printing → standby
  Time: 2026-05-27 19:41:58 UTC
=== FAILURE DETECTED ===
  File: javi_vase_job1.gcode
  Progress: 100%
  Transition: printing → complete
  Time: 2026-05-28 06:38:17 UTC
=== FAILURE DETECTED ===
  File: cup_engraved_final_job1.gcode
  Progress: 100%
  Transition: printing → complete
  Time: 2026-05-29 01:42:13 UTC
=== FAILURE DETECTED ===
  File: cup_engraved_FINAL_job2.gcode
  Progress: 0%
  Transition: printing → cancelled
  Time: 2026-05-29 03:41:52 UTC
=== FAILURE DETECTED ===
  File: model_job2.gcode
  Progress: 100%
  Transition: printing → complete
  Time: 2026-05-30 22:18:21 UTC
=== FAILURE DETECTED ===
  File: Proxy Stand_job5.gcode
  Progress: 100%
  Transition: printing → complete
  Time: 2026-06-02 03:39:56 UTC
=== FAILURE DETECTED ===
  File: vase_plate_job.gcode
  Progress: 0%
  Transition: printing → cancelled
  Time: 2026-06-02 03:52:00 UTC
=== FAILURE DETECTED ===
  File: Proxy_Stand_job5_v23_final.gcode
  Progress: 100%
  Transition: printing → complete
  Time: 2026-06-02 11:35:48 UTC
=== FAILURE DETECTED ===
  File: combined_jobs_2_3.gcode
  Progress: 100%
  Transition: printing → complete
  Time: 2026-06-02 20:40:24 UTC
=== FAILURE DETECTED ===
  File: CRtestcube_Ender-3 V3 Plus_26m.gcode
  Progress: 100%
  Transition: printing → complete
  Time: 2026-06-03 03:57:56 UTC
=== FAILURE DETECTED ===
  File: Proxy_Stand_TF_solo_patched.gcode
  Progress: 0%
  Transition: printing → cancelled
  Time: 2026-06-03 04:57:15 UTC
=== FAILURE DETECTED ===
  File: ProxyStandTF_brim.gcode
  Progress: 0%
  Transition: printing → cancelled
  Time: 2026-06-03 05:38:29 UTC
=== FAILURE DETECTED ===
  File: gcodes/Proxy_Tornado_Recycler_job1.gcode
  Progress: 0%
  Transition: printing → cancelled
  Time: 2026-06-03 08:16:18 UTC
=== FAILURE DETECTED ===
  File: gcodes/ProxyStand_TCF.gcode
  Progress: 0%
  Transition: printing → cancelled
  Time: 2026-06-03 08:31:22 UTC
=== FAILURE DETECTED ===
  File: ProxyStand_TTHQ_cursive_centered_job6.gcode
  Progress: 100%
  Transition: printing → complete
  Time: 2026-06-03 13:16:33 UTC
=== FAILURE DETECTED ===
  File: applacrabus_cored.gcode
  Progress: 0%
  Transition: printing → cancelled
  Time: 2026-06-04 23:39:36 UTC

--- DETAIL ---
  Print: applacrabus_cored.gcode
  Date: 2026-06-04
  Root cause: Claw support structure collapsed mid-print
  Details: Sparse support settings (4.5mm grid, 2mm interface, 0.3mm gap, 60° threshold) were
    insufficient for the claw geometry. One claw support fell, print was manually cancelled.
  Status: ON HOLD — needs support strategy review before reprint
  Action needed: Tighter grid (≤3mm) or tree supports specifically on the claw arms.
    Consider printing claws at a different orientation to minimize unsupported overhangs.
---
=== FAILURE DETECTED ===
  File: Camood_TTHQ_engraved_job8.gcode
  Progress: 0%
  Transition: printing → cancelled
  Time: 2026-06-05 01:39:14 UTC
=== FAILURE DETECTED ===
  File: Camood_TTHQ_engraved_job9.gcode
  Progress: 0%
  Transition: printing → cancelled
  Time: 2026-06-05 05:25:50 UTC
=== FAILURE DETECTED ===
  File: Camood_TTHQ_engraved_job10_pause530.gcode
  Progress: 0%
  Transition: printing → cancelled
  Time: 2026-06-05 17:36:02 UTC
=== FAILURE DETECTED ===
  File: Camood_TTHQ_x3_job13.gcode
  Progress: 0%
  Transition: printing → standby
  Time: 2026-06-05 21:25:22 UTC
=== FAILURE DETECTED ===
  File: Camood_TTHQ_x3_job13.gcode
  Progress: 0%
  Transition: printing → standby
  Time: 2026-06-05 21:32:24 UTC
=== FAILURE DETECTED ===
  File: Camood_TTHQ_x3_job13.gcode
  Progress: 0%
  Transition: printing → cancelled
  Time: 2026-06-05 21:34:25 UTC
=== FAILURE DETECTED ===
  File: Camood_TTHQ_job14.gcode
  Progress: 0%
  Transition: printing → standby
  Time: 2026-06-05 22:35:02 UTC
=== FAILURE DETECTED ===
  File: Camood_TTHQ_job14.gcode
  Progress: 0%
  Transition: printing → standby
  Time: 2026-06-05 22:53:52 UTC
=== FAILURE DETECTED ===
  File: Camood_TTHQ_job14.gcode
  Progress: 0%
  Transition: printing → standby
  Time: 2026-06-05 23:00:53 UTC
=== FAILURE DETECTED ===
  File: Camood_TTHQ_job14.gcode
  Progress: 0%
  Transition: printing → standby
  Time: 2026-06-05 23:33:06 UTC
=== FAILURE DETECTED ===
  File: Camood_TTHQ_job14.gcode
  Progress: 0%
  Transition: printing → standby
  Time: 2026-06-05 23:40:05 UTC
=== FAILURE DETECTED ===
  File: Camood_TTHQ_job14.gcode
  Progress: 0%
  Transition: printing → standby
  Time: 2026-06-05 23:55:10 UTC
=== FAILURE DETECTED ===
  File: Camood_TTHQ_test_job15.gcode
  Progress: 0%
  Transition: printing → cancelled
  Time: 2026-06-06 04:58:56 UTC
=== FAILURE DETECTED ===
  File: Camood_TTHQ_test_job15_final.gcode
  Progress: 0%
  Transition: printing → standby
  Time: 2026-06-06 05:07:59 UTC
=== FAILURE DETECTED ===
  File: Camood_TTHQ_job16.gcode
  Progress: 0%
  Transition: printing → standby
  Time: 2026-06-06 05:13:00 UTC
=== FAILURE DETECTED ===
  File: Camood_TTHQ_job17.gcode
  Progress: 0%
  Transition: printing → standby
  Time: 2026-06-06 05:35:09 UTC
=== FAILURE DETECTED ===
  File: Camood_TTHQ_job17.gcode
  Progress: 0%
  Transition: printing → cancelled
  Time: 2026-06-06 05:43:11 UTC
=== FAILURE DETECTED ===
  File: ksr_fdmtest_v4 by Autodesk&kickstart-Ender-3 V3 Plus_1h58m.gcode
  Progress: 100%
  Transition: printing → complete
  Time: 2026-06-06 07:46:53 UTC
=== FAILURE DETECTED ===
  File: Camood_TTHQ_job18.gcode
  Progress: 0%
  Transition: printing → cancelled
  Time: 2026-06-06 07:52:56 UTC
=== FAILURE DETECTED ===
  File: ksr_fdmtest_v4 by Autodesk&kickstart-Ender-3 V3 Plus_1h58m.gcode
  Progress: 100%
  Transition: printing → complete
  Time: 2026-06-06 17:37:59 UTC
=== ERROR STATE ===
  Message: {"code":"key165", "msg": "Error evaluating 'gcode_macro START_PRINT:gcode': gcode.CommandError: Bed not cleared. Run BED_CLEARED after checking the build plate.
", "values": ["gcode_macro START_PRINT:gcode", "gcode.CommandError: Bed not cleared. Run BED_CLEARED after checking the build plate.
"]}
=== ERROR STATE ===
  Message: {"code":"key165", "msg": "Error evaluating 'gcode_macro START_PRINT:gcode': gcode.CommandError: Bed not cleared. Run BED_CLEARED after checking the build plate.
", "values": ["gcode_macro START_PRINT:gcode", "gcode.CommandError: Bed not cleared. Run BED_CLEARED after checking the build plate.
"]}
=== ERROR STATE ===
  Message: {"code":"key165", "msg": "Error evaluating 'gcode_macro START_PRINT:gcode': gcode.CommandError: Bed not cleared. Run BED_CLEARED after checking the build plate.
", "values": ["gcode_macro START_PRINT:gcode", "gcode.CommandError: Bed not cleared. Run BED_CLEARED after checking the build plate.
"]}
=== ERROR STATE ===
  Message: {"code":"key165", "msg": "Error evaluating 'gcode_macro START_PRINT:gcode': gcode.CommandError: Bed not cleared. Run BED_CLEARED after checking the build plate.
", "values": ["gcode_macro START_PRINT:gcode", "gcode.CommandError: Bed not cleared. Run BED_CLEARED after checking the build plate.
"]}
=== ERROR STATE ===
  Message: {"code":"key165", "msg": "Error evaluating 'gcode_macro START_PRINT:gcode': gcode.CommandError: Bed not cleared. Run BED_CLEARED after checking the build plate.
", "values": ["gcode_macro START_PRINT:gcode", "gcode.CommandError: Bed not cleared. Run BED_CLEARED after checking the build plate.
"]}
=== ERROR STATE ===
  Message: {"code":"key165", "msg": "Error evaluating 'gcode_macro START_PRINT:gcode': gcode.CommandError: Bed not cleared. Run BED_CLEARED after checking the build plate.
", "values": ["gcode_macro START_PRINT:gcode", "gcode.CommandError: Bed not cleared. Run BED_CLEARED after checking the build plate.
"]}
=== ERROR STATE ===
  Message: {"code":"key165", "msg": "Error evaluating 'gcode_macro START_PRINT:gcode': gcode.CommandError: Bed not cleared. Run BED_CLEARED after checking the build plate.
", "values": ["gcode_macro START_PRINT:gcode", "gcode.CommandError: Bed not cleared. Run BED_CLEARED after checking the build plate.
"]}
=== ERROR STATE ===
  Message: {"code":"key165", "msg": "Error evaluating 'gcode_macro START_PRINT:gcode': gcode.CommandError: Bed not cleared. Run BED_CLEARED after checking the build plate.
", "values": ["gcode_macro START_PRINT:gcode", "gcode.CommandError: Bed not cleared. Run BED_CLEARED after checking the build plate.
"]}
=== ERROR STATE ===
  Message: {"code":"key165", "msg": "Error evaluating 'gcode_macro START_PRINT:gcode': gcode.CommandError: Bed not cleared. Run BED_CLEARED after checking the build plate.
", "values": ["gcode_macro START_PRINT:gcode", "gcode.CommandError: Bed not cleared. Run BED_CLEARED after checking the build plate.
"]}
=== ERROR STATE ===
  Message: {"code":"key165", "msg": "Error evaluating 'gcode_macro START_PRINT:gcode': gcode.CommandError: Bed not cleared. Run BED_CLEARED after checking the build plate.
", "values": ["gcode_macro START_PRINT:gcode", "gcode.CommandError: Bed not cleared. Run BED_CLEARED after checking the build plate.
"]}
=== ERROR STATE ===
  Message: {"code":"key165", "msg": "Error evaluating 'gcode_macro START_PRINT:gcode': gcode.CommandError: Bed not cleared. Run BED_CLEARED after checking the build plate.
", "values": ["gcode_macro START_PRINT:gcode", "gcode.CommandError: Bed not cleared. Run BED_CLEARED after checking the build plate.
"]}
=== ERROR STATE ===
  Message: {"code":"key165", "msg": "Error evaluating 'gcode_macro START_PRINT:gcode': gcode.CommandError: Bed not cleared. Run BED_CLEARED after checking the build plate.
", "values": ["gcode_macro START_PRINT:gcode", "gcode.CommandError: Bed not cleared. Run BED_CLEARED after checking the build plate.
"]}
=== ERROR STATE ===
  Message: {"code":"key165", "msg": "Error evaluating 'gcode_macro START_PRINT:gcode': gcode.CommandError: Bed not cleared. Run BED_CLEARED after checking the build plate.
", "values": ["gcode_macro START_PRINT:gcode", "gcode.CommandError: Bed not cleared. Run BED_CLEARED after checking the build plate.
"]}
=== FAILURE DETECTED ===
  File: Camood_TTHQ_fresh.gcode
  Progress: 0%
  Transition: printing → standby
  Time: 2026-06-07 23:54:59 UTC
=== FAILURE DETECTED ===
  File: Camood_TTHQ_fresh.gcode
  Progress: 0%
  Transition: printing → standby
  Time: 2026-06-08 00:03:00 UTC
=== FAILURE DETECTED ===
  File: Camood_TTHQ_fresh.gcode
  Progress: 0%
  Transition: printing → cancelled
  Time: 2026-06-08 00:06:01 UTC
=== ERROR STATE ===
  Message: {"code":"key165", "msg": "Error evaluating 'gcode_macro START_PRINT:gcode': gcode.CommandError: Bed not cleared. Run BED_CLEARED after checking the build plate.
", "values": ["gcode_macro START_PRINT:gcode", "gcode.CommandError: Bed not cleared. Run BED_CLEARED after checking the build plate.
"]}
=== ERROR STATE ===
  Message: {"code":"key165", "msg": "Error evaluating 'gcode_macro START_PRINT:gcode': gcode.CommandError: Bed not cleared. Run BED_CLEARED after checking the build plate.
", "values": ["gcode_macro START_PRINT:gcode", "gcode.CommandError: Bed not cleared. Run BED_CLEARED after checking the build plate.
"]}
=== ERROR STATE ===
  Message: {"code":"key165", "msg": "Error evaluating 'gcode_macro START_PRINT:gcode': gcode.CommandError: Bed not cleared. Run BED_CLEARED after checking the build plate.
", "values": ["gcode_macro START_PRINT:gcode", "gcode.CommandError: Bed not cleared. Run BED_CLEARED after checking the build plate.
"]}
=== ERROR STATE ===
  Message: {"code":"key165", "msg": "Error evaluating 'gcode_macro START_PRINT:gcode': gcode.CommandError: Bed not cleared. Run BED_CLEARED after checking the build plate.
", "values": ["gcode_macro START_PRINT:gcode", "gcode.CommandError: Bed not cleared. Run BED_CLEARED after checking the build plate.
"]}
=== ERROR STATE ===
  Message: {"code":"key165", "msg": "Error evaluating 'gcode_macro START_PRINT:gcode': gcode.CommandError: Bed not cleared. Run BED_CLEARED after checking the build plate.
", "values": ["gcode_macro START_PRINT:gcode", "gcode.CommandError: Bed not cleared. Run BED_CLEARED after checking the build plate.
"]}
=== FAILURE DETECTED ===
  File: ksr_fdmtest_v4 by Autodesk&kickstart-Ender-3 V3 Plus_1h58m.gcode
  Progress: %
  Transition: printing → error
  Time: 2026-06-08 03:21:17 UTC
=== ERROR STATE ===
  Message: {"code":"key165", "msg": "Error evaluating 'gcode_macro START_PRINT:gcode': gcode.CommandError: Bed not cleared. Run BED_CLEARED after checking the build plate.
", "values": ["gcode_macro START_PRINT:gcode", "gcode.CommandError: Bed not cleared. Run BED_CLEARED after checking the build plate.
"]}
=== FAILURE DETECTED ===
  File: ksr_fdmtest_v4 by Autodesk&kickstart-Ender-3 V3 Plus_1h58m.gcode
  Progress: %
  Transition: printing → error
  Time: 2026-06-08 03:24:18 UTC
=== ERROR STATE ===
  Message: {"code":"key165", "msg": "Error evaluating 'gcode_macro START_PRINT:gcode': gcode.CommandError: Bed not cleared. Run BED_CLEARED after checking the build plate.
", "values": ["gcode_macro START_PRINT:gcode", "gcode.CommandError: Bed not cleared. Run BED_CLEARED after checking the build plate.
"]}
=== ERROR STATE ===
  Message: {"code":"key165", "msg": "Error evaluating 'gcode_macro START_PRINT:gcode': gcode.CommandError: Bed not cleared. Run BED_CLEARED after checking the build plate.
", "values": ["gcode_macro START_PRINT:gcode", "gcode.CommandError: Bed not cleared. Run BED_CLEARED after checking the build plate.
"]}
=== ERROR STATE ===
  Message: {"code":"key165", "msg": "Error evaluating 'gcode_macro START_PRINT:gcode': gcode.CommandError: Bed not cleared. Run BED_CLEARED after checking the build plate.
", "values": ["gcode_macro START_PRINT:gcode", "gcode.CommandError: Bed not cleared. Run BED_CLEARED after checking the build plate.
"]}
=== ERROR STATE ===
  Message: {"code":"key165", "msg": "Error evaluating 'gcode_macro START_PRINT:gcode': gcode.CommandError: Bed not cleared. Run BED_CLEARED after checking the build plate.
", "values": ["gcode_macro START_PRINT:gcode", "gcode.CommandError: Bed not cleared. Run BED_CLEARED after checking the build plate.
"]}
=== ERROR STATE ===
  Message: {"code":"key165", "msg": "Error evaluating 'gcode_macro START_PRINT:gcode': gcode.CommandError: Bed not cleared. Run BED_CLEARED after checking the build plate.
", "values": ["gcode_macro START_PRINT:gcode", "gcode.CommandError: Bed not cleared. Run BED_CLEARED after checking the build plate.
"]}
=== ERROR STATE ===
  Message: {"code":"key165", "msg": "Error evaluating 'gcode_macro START_PRINT:gcode': gcode.CommandError: Bed not cleared. Run BED_CLEARED after checking the build plate.
", "values": ["gcode_macro START_PRINT:gcode", "gcode.CommandError: Bed not cleared. Run BED_CLEARED after checking the build plate.
"]}
=== ERROR STATE ===
  Message: {"code":"key165", "msg": "Error evaluating 'gcode_macro START_PRINT:gcode': gcode.CommandError: Bed not cleared. Run BED_CLEARED after checking the build plate.
", "values": ["gcode_macro START_PRINT:gcode", "gcode.CommandError: Bed not cleared. Run BED_CLEARED after checking the build plate.
"]}
=== ERROR STATE ===
  Message: {"code":"key165", "msg": "Error evaluating 'gcode_macro START_PRINT:gcode': gcode.CommandError: Bed not cleared. Run BED_CLEARED after checking the build plate.
", "values": ["gcode_macro START_PRINT:gcode", "gcode.CommandError: Bed not cleared. Run BED_CLEARED after checking the build plate.
"]}
=== ERROR STATE ===
  Message: {"code":"key165", "msg": "Error evaluating 'gcode_macro START_PRINT:gcode': gcode.CommandError: Bed not cleared. Run BED_CLEARED after checking the build plate.
", "values": ["gcode_macro START_PRINT:gcode", "gcode.CommandError: Bed not cleared. Run BED_CLEARED after checking the build plate.
"]}
=== ERROR STATE ===
  Message: {"code":"key165", "msg": "Error evaluating 'gcode_macro START_PRINT:gcode': gcode.CommandError: Bed not cleared. Run BED_CLEARED after checking the build plate.
", "values": ["gcode_macro START_PRINT:gcode", "gcode.CommandError: Bed not cleared. Run BED_CLEARED after checking the build plate.
"]}
=== FAILURE DETECTED ===
  File: Camood_TTHQ_fresh.gcode
  Progress: 0%
  Transition: printing → cancelled
  Time: 2026-06-08 04:29:38 UTC
=== FAILURE DETECTED ===
  File: ksr_fdmtest_v4_by_Autodesk_1h58m.gcode
  Progress: 100%
  Transition: printing → complete
  Time: 2026-06-08 07:23:38 UTC
=== FAILURE DETECTED ===
  File: Camood_TTHQ_engraved.stl_PLA_2h50m58s.gcode
  Progress: 100%
  Transition: printing → complete
  Time: 2026-06-09 03:37:25 UTC
=== FAILURE DETECTED ===
  File: CRtestcube_Ender-3 V3 Plus_26m.gcode
  Progress: 100%
  Transition: printing → complete
  Time: 2026-06-09 06:01:16 UTC
=== FAILURE DETECTED ===
  File: Fuss_PETG_2h55m34s.gcode
  Progress: 99%
  Transition: printing → complete
  Time: 2026-06-09 10:03:33 UTC
=== FAILURE DETECTED ===
  File: Apple_bored.stl_PETG_2h55m50s.gcode
  Progress: 100%
  Transition: printing → complete
  Time: 2026-06-09 17:24:14 UTC
=== FAILURE DETECTED ===
  File: obj_18_Motor_Gear.stl_PLA_1h6m7s.gcode
  Progress: 100%
  Transition: printing → complete
  Time: 2026-06-10 08:22:40 UTC
=== FAILURE DETECTED ===
  File: obj_1_Butterfly.stl_PLA_3h13m10s.gcode
  Progress: 0%
  Transition: printing → standby
  Time: 2026-06-10 13:52:49 UTC
=== FAILURE DETECTED ===
  File: Kraken_pipe_Charlie.stl_PLA_5h12m22s.gcode
  Progress: 0%
  Transition: printing → cancelled
  Time: 2026-06-18 06:43:35 UTC
=== FAILURE DETECTED ===
  File: Kraken_pipe_Charlie.stl_PLA_5h52m42s.gcode
  Progress: 100%
  Transition: printing → complete
  Time: 2026-06-18 12:41:35 UTC
=== FAILURE DETECTED ===
  File: Backpack_Boyz_Core.stl_PLA_6h39m26s.gcode
  Progress: 100%
  Transition: printing → complete
  Time: 2026-06-19 13:35:59 UTC
=== FAILURE DETECTED ===
  File: Kraken_pipe_Charlie.stl_PLA_14h32m42s.gcode
  Progress: 100%
  Transition: printing → complete
  Time: 2026-06-20 20:49:06 UTC
=== FAILURE DETECTED ===
  File: ender3_spoolholder_sidemount.stl_PLA_1h1m30s.gcode
  Progress: 0%
  Transition: printing → error
  Time: 2026-06-21 06:05:29 UTC
=== FAILURE DETECTED ===
  File: ender3_spoolholder_sidemount.stl_PLA_1h1m30s.gcode
  Progress: 100%
  Transition: printing → complete
  Time: 2026-06-21 06:27:29 UTC
=== FAILURE DETECTED ===
  File: calliope-filament-guide.gcode
  Progress: 100%
  Transition: printing → complete
  Time: 2026-06-21 07:35:56 UTC
=== FAILURE DETECTED ===
  File: mario-pipe-marked_job4.gcode
  Progress: 0%
  Transition: printing → cancelled
  Time: 2026-06-24 07:14:13 UTC
=== FAILURE DETECTED ===
  File: Object_1_PLA_10h28m54s.gcode
  Progress: 100%
  Transition: printing → complete
  Time: 2026-06-24 17:51:54 UTC
=== FAILURE DETECTED ===
  File: calliope-mario-pipe-treesup.gcode
  Progress: 100%
  Transition: printing → complete
  Time: 2026-06-26 00:20:59 UTC
=== FAILURE DETECTED ===
  File: lid.stl_PLA_23m8s.gcode
  Progress: 100%
  Transition: printing → complete
  Time: 2026-06-26 01:14:19 UTC
=== FAILURE DETECTED ===
  File: obj_1_Paracord Jig Ruler Side.stl_PLA_6h3m16s.gcode
  Progress: 100%
  Transition: printing → complete
  Time: 2026-06-26 07:35:42 UTC
=== FAILURE DETECTED ===
  File: Camood_TTHQ_engraved.stl_PETG_2h53m7s.gcode
  Progress: 0%
  Transition: printing → cancelled
  Time: 2026-06-28 10:45:17 UTC
=== FAILURE DETECTED ===
  File: Camood_TTHQ_engraved.stl_PETG_2h53m7s.gcode
  Progress: 100%
  Transition: printing → complete
  Time: 2026-06-28 13:37:20 UTC
=== FAILURE DETECTED ===
  File: Camood_clean-marked.stl_PETG_2h50m0s.gcode
  Progress: 0%
  Transition: printing → standby
  Time: 2026-06-29 03:01:36 UTC
=== FAILURE DETECTED ===
  File: Camood_clean-marked_PETG_240C.gcode
  Progress: 0%
  Transition: printing → cancelled
  Time: 2026-06-29 05:44:28 UTC
=== FAILURE DETECTED ===
  File: Camood_clean-marked.stl_PETG_2h48m53s.gcode
  Progress: 0%
  Transition: printing → cancelled
  Time: 2026-06-29 06:44:48 UTC
=== FAILURE DETECTED ===
  File: .Camood_clean-marked_gcode.3mf/Camood_clean-marked_gcode_plate_1.gcode
  Progress: 100%
  Transition: printing → complete
  Time: 2026-06-29 10:50:20 UTC
=== FAILURE DETECTED ===
  File: holder.stl_PLA_2h3m17s.gcode
  Progress: 0%
  Transition: printing → cancelled
  Time: 2026-06-29 17:42:49 UTC
=== FAILURE DETECTED ===
  File: holder.stl_PLA_2h3m17s.gcode
  Progress: 100%
  Transition: printing → complete
  Time: 2026-06-29 19:44:29 UTC
=== FAILURE DETECTED ===
  File: clamp.stl_PLA_1h33m58s.gcode
  Progress: 100%
  Transition: printing → complete
  Time: 2026-06-30 04:09:33 UTC
=== FAILURE DETECTED ===
  File: Object_8_PLA_4h2m34s.gcode
  Progress: 100%
  Transition: printing → complete
  Time: 2026-06-30 08:38:09 UTC
=== FAILURE DETECTED ===
  File: Camood_TerpTribeHq.stl_PETG_6h52m8s.gcode
  Progress: 0%
  Transition: printing → standby
  Time: 2026-06-30 22:17:01 UTC
=== FAILURE DETECTED ===
  File: Camood_TerpTribeHq.stl_PETG_6h52m8s.gcode
  Progress: 0%
  Transition: printing → standby
  Time: 2026-06-30 22:21:03 UTC
=== FAILURE DETECTED ===
  File: Camood_clean-marked.stl_PETG_10h8m17s.gcode
  Progress: 0%
  Transition: printing → standby
  Time: 2026-06-30 22:31:07 UTC
=== FAILURE DETECTED ===
  File: drpuffco - med core. - manual smooth.stl_PETG_52m43s.gcode
  Progress: 66%
  Transition: printing → error
  Time: 2026-06-30 23:53:40 UTC
=== ERROR STATE ===
  Message: {"code":"key561","msg":"Lost communication with MCU 'nozzle_mcu'"}
=== ERROR STATE ===
  Message: {"code":"key561","msg":"Lost communication with MCU 'nozzle_mcu'"}
=== ERROR STATE ===
  Message: {"code":"key561","msg":"Lost communication with MCU 'nozzle_mcu'"}
=== ERROR STATE ===
  Message: {"code":"key561","msg":"Lost communication with MCU 'nozzle_mcu'"}
=== ERROR STATE ===
  Message: {"code":"key561","msg":"Lost communication with MCU 'nozzle_mcu'"}
=== ERROR STATE ===
  Message: {"code":"key561","msg":"Lost communication with MCU 'nozzle_mcu'"}
=== ERROR STATE ===
  Message: {"code":"key561","msg":"Lost communication with MCU 'nozzle_mcu'"}
=== ERROR STATE ===
  Message: {"code":"key561","msg":"Lost communication with MCU 'nozzle_mcu'"}
=== FAILURE DETECTED ===
  File: Object_1_PETG_54m9s.gcode
  Progress: 82%
  Transition: printing → error
  Time: 2026-07-01 01:32:16 UTC
=== ERROR STATE ===
  Message: {"code":"key561","msg":"Lost communication with MCU 'nozzle_mcu'"}
=== ERROR STATE ===
  Message: {"code":"key561","msg":"Lost communication with MCU 'nozzle_mcu'"}
=== FAILURE DETECTED ===
  File: 3DBenchy-Ender-3 V3 Plus_14m28.gcode
  Progress: 0%
  Transition: printing → cancelled
  Time: 2026-07-01 02:24:34 UTC
=== FAILURE DETECTED ===
  File: proxy_holster_bore_fixed.stl_PETG_48m26s.gcode
  Progress: 100%
  Transition: printing → complete
  Time: 2026-07-01 05:07:34 UTC
=== FAILURE DETECTED ===
  File: proxy_holster_bore_fixed.stl_PETG_46m25s.gcode
  Progress: 100%
  Transition: printing → complete
  Time: 2026-07-01 07:59:37 UTC
=== FAILURE DETECTED ===
  File: proxy_holster_bore_fixed.stl_PETG_45m53s.gcode
  Progress: 100%
  Transition: printing → complete
  Time: 2026-07-01 16:40:39 UTC
