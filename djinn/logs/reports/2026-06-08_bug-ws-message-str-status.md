---
title: Bug Report — WebSocket message with str status crashes _handle_ws_message
agent: Claude
date: 2026-06-08
severity: low
status: fixed
system: djinn-print-track
---

# Bug: WebSocket message with str status crashes `_handle_ws_message`

**System:** djinn-print-track v2
**Severity:** low | **Status:** fixed
**Discovered:** 2026-06-08 during Phase 4 live test

## Root Cause

Moonraker occasionally sends a WebSocket notification where `status` is a string instead of a dict. The `_handle_ws_message` function iterated over `status.items()` without checking the type first. This caused `AttributeError: 'str' object has no attribute 'items'`.

The daemon self-recovered via the `except Exception` handler in `_ws_loop` (10s reconnect backoff), so no data loss occurred. The notification that caused it was likely an edge-case Moonraker message format.

## Fix

Added guard at `_handle_ws_message` line 441:
```python
if not isinstance(status, dict):
    return
```

This silently skips any malformed status messages instead of crashing.

## Rule/Lesson

Always guard `dict` iteration against type changes. Moonraker WebSocket messages are not guaranteed to have any specific type for any field. Any `for k, v in data.items()` on external data needs an `isinstance(data, dict)` gate. The daemon's `except Exception` handler is the last line of defense, but type guards prevent unnecessary reconnection storms.
