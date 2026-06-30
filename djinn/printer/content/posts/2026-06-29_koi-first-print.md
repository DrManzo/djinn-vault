---
title: Koi Fish — First Print Post
date: 2026-06-29
printer: Penelope
model: Cute Koi (Tripo AI)
filament: Generic PLA
status: draft
tags: [content, post, penelope, pla, koi, lessons, first-print]
related: [[koi-figure]]
---

# Koi Fish — First Print Post

**First print off the new printer. Raw results, real lessons.**

Grabbed a koi fish model directly from an online slicer — no modifications, no profile adjustments, just hit print. General PLA.

The top came out clean. Really clean actually. That part I'm proud of.

The bottom told a different story.

Because this model doesn't have a flat base, I had to dial in the Z offset manually with babystep — the nozzle was sitting too high and the first layer wasn't catching. Once I found -0.599mm it gripped and we were off.

The real lesson came in the lower walls. Gaps everywhere. Weak enough that sections broke off. And strings — a lot of them — running between surfaces where the head traveled. The culprit for all of it? The online slicer's settings were tuned for a different machine. Flow too low for a Bowden extruder, retraction not dialed in for the longer filament path. Bowden needs more retraction distance and more flow compensation than a direct drive. The slicer didn't know that. I didn't catch it. The walls and the stringing paid for it.

Mid-print I swapped filament. That part actually went fine.

**What I'm taking from this:**

→ Foreign gcodes always need a Z babystep check if the model isn't flat-bottomed

→ Never trust an online slicer's retraction or flow settings on a Bowden machine — reslice with your own profile

→ Stringing = retraction problem. Gaps = flow problem. Both point to the same root cause: wrong settings for the extruder type

→ The top being perfect while the bottom fails tells you exactly where the problem started

Every print teaches you something. This one taught me three.
