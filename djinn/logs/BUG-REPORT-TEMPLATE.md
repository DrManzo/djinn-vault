---
title: Bug Report — <title>
agent: <Claude | Salomon | Typhon>
date: YYYY-MM-DD
severity: <critical | high | medium | low>
status: <open | fixed | wont-fix>
tags: [djinn, bug, <system>]
---

# Bug Report — <title>

**Date:** YYYY-MM-DD  
**Agent:** who found it  
**System:** which system/service was affected  
**Severity:** critical / high / medium / low  
**Status:** open / fixed  

---

## Symptom

What the user or system observed. Exact error messages, log lines, or behavior. Be specific — "it didn't work" is not a symptom.

---

## Steps to Reproduce

1. Step one
2. Step two
3. Observed: X
4. Expected: Y

---

## Root Cause

The actual reason this happened. Not a guess — dig until you know. If you genuinely can't determine it, say so and list your hypotheses.

---

## Fix Applied

What was changed, where, and why it resolves the root cause. Include file paths and line references.

```
file: path/to/file
change: description of change
```

---

## Verification

How you confirmed the fix worked. Test output, log lines, API responses.

---

## Rule / Lesson

One sentence: the rule that prevents this class of bug in the future. This goes into the relevant agent's context or PROTOCOL.md.

> **Rule:** ...

---

## Related

- [[session-report-slug]] — session where this was found and fixed
- Any other related bugs or decisions

---

*— AgentName, YYYY-MM-DD*
