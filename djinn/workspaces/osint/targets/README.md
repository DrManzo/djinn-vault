# Targets — README

This directory holds named target files for active and completed OSINT operations.

---

## How to Create a Target

1. Copy `_template.md` to a new file: `<target-slug>.md`
2. Fill in the **Target Profile** section with what you know at start
3. Assign the appropriate Gateway tier based on operation scope
4. Add the target slug to DEVLOG.md when the operation opens
5. Update the file as agents return findings during the operation
6. When the operation closes, `SCRIBE` moves the file to `archived/`

---

## Naming Convention

- Slugs are lowercase, hyphenated: `acme-corp`, `twitter-handle-jsmith`, `domain-example-com`
- No real full names in filenames — use a slug or case code
- Filename format: `<slug>.md`

---

## PII Policy

- No real addresses, phone numbers, SSNs, or financial account numbers in plaintext here
- Use `[ENCRYPTED — see vault db]` as a placeholder when those fields are relevant
- Gateway Tier 3+ findings must be confirmed by operator before this file is updated

---

## Directory Structure

```
targets/
├── README.md           ← This file
├── _template.md        ← Copy this to start a new target
├── <slug>.md           ← Active targets
└── archived/           ← Closed operations
```
