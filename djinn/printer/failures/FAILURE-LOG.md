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
