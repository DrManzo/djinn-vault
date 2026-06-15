---
title: Bug Report — Webcam Monitor Milestone Clips 1-Frame Output
agent: Claude
date: 2026-06-15
tags: [djinn, bug, webcam-monitor, milestone-clips]
related: [[build-log]] | [[bugs]]
---

# Bug Report — Webcam Monitor Milestone Clips 1-Frame Output

**Date:** 2026-06-15
**System:** djinn-webcam-monitor
**Severity:** medium
**Status:** fixed

---

## Root Cause

`ms_writer.write(frame)` was placed inside the `MONITOR_INTERVAL` gate — the 10-second analysis block guarded by `if now - self.t_check < MONITOR_INTERVAL: continue`. Only one frame was written per 10-second interval. With `VideoWriter` configured at 30fps, each "10-second" milestone clip contained a single frame that played for 33ms. The `MILESTONE_DURATION = 10` timer ran correctly, but the clip file was essentially empty.

The scheduled and failure recorders correctly write before the gate (`if self.writer: self.writer.write(frame)` at the top of the loop). The milestone writer was missed when it was added.

---

## Fix

Moved `ms_writer.write(frame)` and the `ms_end` timer check to before the `MONITOR_INTERVAL` gate, alongside the scheduled/failure recorder write. The threshold check (`_ms_check`) stays inside the gate — it only needs to run every 10 seconds.

```python
# Before (inside 10s gate — 1 frame per clip):
if state == "printing":
    if self.ms_writer:
        self.ms_writer.write(frame)
        if time.time() >= self.ms_end:
            self._ms_stop()
    self._ms_check(progress, time.time())

# After (write before gate — every frame; check stays gated):
if self.ms_writer:
    self.ms_writer.write(frame)
    if time.time() >= self.ms_end:
        self._ms_stop()
# ... interval gate ...
if state == "printing":
    self._ms_check(progress, time.time())
```

**Commit:** a61059de

---

## Lesson

Any VideoWriter that needs real-time frame data must write before the analysis interval gate. The gate is for CPU-expensive operations (Moonraker API calls, frame diff, state decisions) — not for I/O to recorders. Pattern: write first, gate the analysis.

---

*— Claude, 2026-06-15*
