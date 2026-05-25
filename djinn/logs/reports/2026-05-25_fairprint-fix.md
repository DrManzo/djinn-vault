---
title: Session Report — FairPrintAgent Bug Fix + Tool Validation
agent: Claude
date: 2026-05-25
tags: [djinn, report, fairprint, bugfix]
related: [[build-log]] | [[project_fairprint]]
---

# Session Report — FairPrintAgent Bug Fix + Tool Validation

**Date:** 2026-05-25
**Agent:** Claude
**Session type:** Debug
**Trigger:** First live test of djinn-print-quote on a real print job (Mario Pipe, 2026-05-24)

---

## Summary

First end-to-end validation of FairPrintAgent against real print data. Tool ran successfully on the Mario Pipe job (44g, 3.33h) and returned clean market comps from Etsy. A crash in `--quick` mode was discovered and fixed — the mode requires interactive terminal input but produced a confusing `ValueError` when stdin was piped. Fixed with a TTY guard and graceful EOF handling.

---

## What Was Built or Changed

- Ran `--coin` preset: confirmed clean output, $92.91 cost floor, 3 market comps fetched live
- Ran full JSON mode on Mario Pipe: $11.70 fair market, $15.09 market median (5 Etsy comps fetched live)
- Discovered `--quick` crash when stdin is piped (ValueError on float conversion of non-numeric input)
- Fixed `--quick` mode: TTY check at entry, helpful error + example command, EOF/KeyboardInterrupt handling throughout

---

## Technical Decisions

**TTY guard over input sanitization — Why:** The `--quick` mode is genuinely interactive — it prompts sequentially and has no non-interactive equivalent. Trying to parse piped input would require a full input protocol redesign. The right fix is to refuse non-TTY stdin immediately with a clear error that points to the correct alternative (`--simple` flags).

**Error message includes example command — Why:** User hitting this in the field (OpenClaw, script, cron) needs to know exactly what to run instead. Silent exit or generic error wastes time.

---

## Files Created or Modified

```
~/.local/bin/djinn-print-quote     ← --quick TTY guard + EOF handling added
~/Obsidian/djinn/logs/reports/2026-05-25_fairprint-fix.md  ← this file
```

---

## Dependencies Installed

None.

---

## Tests & Validation

| Test | Command | Result |
|------|---------|--------|
| Coin preset | `djinn-print-quote --coin` | ✅ $92.91 floor, 3 comps |
| Mario Pipe full JSON | `djinn-print-quote '<json>'` | ✅ $11.70 fair market, 5 comps |
| Piped input to --quick | `echo "test" \| djinn-print-quote --quick` | ✅ Clean error + example |
| --simple mode | `djinn-print-quote --simple --name "Mario Pipe" --grams 44 --hours 3.33` | ✅ Runs, library hit detected |

---

## Known Issues / Caveats

- `--simple` mode treats all print time as labor ($20/hr × print hours). This inflates cost significantly for long unattended prints — the machine runs itself, Javier isn't working. For Mario Pipe this produces $112.77 vs $11.70 from the full agent formula. The full JSON mode is more accurate for pricing real jobs.
- Coin preset labor is also high ($65) vs $15 market median — reflects design time (180 min) being charged. Accurate for original designs, misleading if used as a general template.

---

## What's Next

- [ ] Consider adding a `--print-hours` vs `--labor-hours` distinction to `--simple` mode — @Claude
- [ ] Build a price sheet for all completed prints using full JSON mode — @Javier
- [ ] Wire `djinn-print-quote` output to Instagram caption pipeline for commission posts — @Claude

---

*— Claude, 2026-05-25*
