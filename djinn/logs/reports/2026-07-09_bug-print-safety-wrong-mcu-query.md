---
title: Bug Report — djinn-print-safety Never Actually Worked (wrong Moonraker object/field path + bad restart policy)
agent: Claude
date: 2026-07-09
tags: [djinn, bug, calliope, print-safety, moonraker, klipper, systemd]
related: [[2026-07-09_bug-calliope-cable-fixed]] | [[build-log]] | [[bugs]]
---

# Bug Report — djinn-print-safety Never Actually Worked

**Date:** 2026-07-09
**System:** `~/.local/bin/djinn-print-safety` + `~/.config/systemd/user/djinn-print-safety.service`
**Severity:** High
**Status:** Fixed

---

## What Happened

While watching Calliope's first production print after the BUG-014 cable replacement, the print-safety watchdog was armed and running (as confirmed via `systemctl --user status`), but `journalctl` showed it spamming an error on every single poll cycle throughout an actively-printing job:

```
⚠  Error: int() argument must be a string, a bytes-like object or a real number, not 'NoneType'
```

This wasn't a one-off — it repeated every ~5 seconds (the poll interval) for the entire duration the daemon ran, meaning it never successfully computed a failure probability, not once, during any of tonight's crashes.

---

## Root Cause

`get_mcu_stats()` in `djinn-print-safety` queried:

```
/printer/objects/query?mcu=bytes_retransmit,bytes_invalid,send_seq,retransmit_seq
```

Two things wrong with this:

1. **Wrong object.** The daemon's entire purpose is watching `nozzle_mcu` (the toolhead board, per its own docstring: "Tracks nozzle_mcu retransmit rate and bytes_invalid trend"). It was querying `mcu` — the *mainboard* MCU — instead.
2. **Wrong field path.** Even querying the correct object, `bytes_retransmit`/`bytes_invalid`/`send_seq`/`retransmit_seq` are not top-level attributes of a Moonraker `mcu` object — they live nested under `last_stats`. Requesting them as top-level fields via the query-string field filter returns `null` for all of them:

```json
{"result": {"status": {"mcu": {"bytes_retransmit": null, "bytes_invalid": null, "send_seq": null, "retransmit_seq": null}}}}
```

`int(mcu.get("bytes_retransmit", 0))` then crashes, because `.get(key, 0)` only supplies the default when the key is *absent* — here the key is present with an explicit value of `None`, so `int(None)` raises `TypeError`.

Verified the correct shape via direct query:

```
/printer/objects/query?mcu%20nozzle_mcu   (no field filter, full object)
→ status."mcu nozzle_mcu".last_stats.bytes_retransmit  (a real integer)
```

---

## Fix

`get_mcu_stats()` now queries `mcu%20nozzle_mcu=last_stats` and pulls fields from the nested dict, with `or 0` instead of `.get(key, 0)` (catches explicit `None`, not just missing keys):

```python
def get_mcu_stats():
    obj = moonraker_get("/printer/objects/query?mcu%20nozzle_mcu=last_stats")
    stats = obj.get("status", {}).get("mcu nozzle_mcu", {}).get("last_stats", {}) or {}
    return {
        "bytes_retransmit": int(stats.get("bytes_retransmit") or 0),
        "bytes_invalid":    int(stats.get("bytes_invalid") or 0),
        "send_seq":         int(stats.get("send_seq") or 0),
        "retransmit_seq":   int(stats.get("retransmit_seq") or 0),
        "ts":               time.monotonic(),
    }
```

Verified live against an in-progress print — clean output every poll, no errors:

```
Z=1.4mm | retx=0.0% | emi=0.00B/s | p=0%
```

---

## Second, Related Bug: Restart Policy

Separately, the systemd unit used `Restart=on-failure`, but the daemon's main loop exits with code **0** (success) whenever `print_stats.state` is `"complete"` at startup — the normal resting state Moonraker leaves in place after any successful print (it does not revert to `"standby"` automatically). `Restart=on-failure` does not trigger on a clean exit, so the watchdog silently stayed dead after every completed print until someone manually restarted it right as the next print began.

**Fix:** changed `Restart=on-failure` → `Restart=always`, `RestartSec=10` → `5`. Confirmed safe: the daemon's own loop already polls quietly at a 5s interval in every non-terminal state, so a 5s systemd restart cadence in the terminal-state case adds negligible overhead and makes the whole thing self-healing with zero manual intervention.

---

## Consequence

**This safety system has never once functioned as designed until tonight.** Every previous invocation — including monitoring attempts during the two klippy_shutdowns that happened on Calliope's first two post-cable-replacement production print attempts — was polling garbage and computing nothing. It could not have warned or auto-paused regardless of thresholds, because the failure-probability computation never received real data.

---

## Rule / Lesson

**Moonraker's object-query field filter (`?object=field1,field2`) only works for genuine top-level attributes of that object — nested sub-dicts like `last_stats` must be requested whole (`?object=last_stats`) and then indexed in code.** A query that silently returns `null` for every requested field (rather than erroring) is easy to miss if the consuming code doesn't fail loudly on `None` — this bug shipped and ran for an unknown number of prior sessions without anyone noticing, because `.get(key, 0)` masked the missing-vs-null distinction until an actual `int(None)` finally surfaced it.

**A daemon meant to run indefinitely across print jobs should not rely on `Restart=on-failure` if any of its normal exit paths use code 0.** `Restart=always` is the correct policy for "this should always be running, restart it no matter why it stopped" — reserve `on-failure` for daemons where a clean exit genuinely means "nothing more to do, ever."

---

## Files Modified

```
~/.local/bin/djinn-print-safety                      ← get_mcu_stats() query fixed
~/.config/systemd/user/djinn-print-safety.service     ← Restart=always, RestartSec=5
```

---

## What's Next

- [ ] Now that the watchdog actually works, let it run through a real PETG production print (the actual stress case) to see if it produces a meaningful warning/pause before a future crash — untested in its working state so far
- [ ] Consider adding an assertion/loud-fail in `get_mcu_stats()` if `last_stats` comes back empty, so a future Moonraker API change doesn't reintroduce silent-garbage-data the same way

---

*— Claude, 2026-07-09*
