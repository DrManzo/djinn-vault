# Reports — README

This directory holds completed intelligence reports assembled by the OSINT Scribe agent.

---

## Report Lifecycle

1. `CORRELATOR` finishes synthesis and hands off findings to `SCRIBE`
2. `SCRIBE` creates a new report file from `_template.md`
3. Report is written, PII-scrubbed, and confidence-scored
4. Operator reviews the report and marks it `Reviewed` or requests amendments
5. Report is committed to vault and linked from the corresponding target file

---

## Naming Convention

Format: `YYYY-MM-DD_<slug>.md`  
Example: `2026-06-18_acme-corp-footprint.md`

---

## Directory Structure

```
reports/
├── README.md           ← This file
├── _template.md        ← Copy this to start a new report
└── YYYY-MM-DD_<slug>.md  ← Completed reports
```
