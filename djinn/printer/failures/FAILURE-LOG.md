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
