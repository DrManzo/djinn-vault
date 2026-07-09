# Support Decision Workflow Research for the Djinn/Calliope 3D Printing Pipeline

## Overview

This document provides a practical research foundation for implementing a support-decision model inside the Djinn workflow for Calliope, the Creality Ender-3 V3 Plus. The central conclusion is that supports should not be enabled by default because unnecessary supports increase material consumption, extend print time, add post-processing labor, and can reduce final surface quality.[cite:70][cite:74][cite:78]

A business-oriented support model should instead classify jobs by geometric risk, material behavior, and customer quality requirement, then apply supports only when the expected failure or finish risk is greater than the cost of added supports.[cite:74][cite:78][cite:91]

## Core Findings

### Supports are a cost center

Support structures add direct material cost, machine time, and post-processing labor without increasing the sale value of most parts.[cite:70][cite:74] This matters in a commission workflow because the extra plastic, extra print hours, and cleanup time reduce margin unless they are required to avoid failure or unacceptable cosmetic defects.[cite:71][cite:74]

Support use also increases waste, which operators commonly identify as one of the largest avoidable loss categories in desktop 3D printing workflows.[cite:76][cite:72] In practical terms, every support that can be removed through orientation, part splitting, or better threshold settings becomes recoverable profit capacity.[cite:78][cite:80]

### Geometry, not part size, determines support need

Whether a model is under one foot tall is not a reliable predictor of support need. Overhang angle, bridge length, unsupported horizontal spans, and local feature shape matter more than absolute model height.[cite:78][cite:80][cite:91]

The most common rule of thumb in FDM is the 45-degree overhang rule, meaning features steeper than roughly 45 degrees from vertical increasingly need support, while many printers can tolerate 45 to 60 degrees depending on material, cooling, layer height, and speed.[cite:81][cite:91] Bridge length matters as well; guidance for support-free design commonly recommends keeping unsupported bridges short, often around 10 to 15 mm, unless the printer and material have been specifically tuned for longer spans.[cite:80]

### Support-free printing is usually the better business default

Manufacturing guidance consistently recommends minimizing supports through orientation changes and self-supporting geometry because this reduces cost and improves throughput.[cite:78][cite:80] In an FDM commission environment, the default should be "supports off unless triggered," not "supports on unless manually removed," because the latter causes systematic overuse of material and labor.[cite:70][cite:78]

This is especially relevant for a workflow like Djinn, which already performs mesh analysis and dry-run slicing before confirmation.[cite:3] Because the consult stage already reports dimensions, overhang presence, and recommended profile paths, it is the correct insertion point for an automatic support-decision layer.[cite:3]

## Decision Variables

A workable support model should score a print using several variables rather than a single angle threshold.

### 1. Overhang severity

This is the most important factor. A simple operating model can divide overhangs into three bands:

- Low risk: generally printable without support when local overhangs are at or below the validated threshold for the current material and profile.[cite:81][cite:85]
- Medium risk: may print without support if the area is small, the finish is non-critical, and the part can be reoriented.[cite:80][cite:82]
- High risk: likely needs support when angles approach horizontal, when the unsupported region is large, or when failure would damage the visible finish.[cite:81][cite:91]

The exact threshold should be calibrated on Calliope with overhang test parts for each material-profile pair rather than assumed from generic internet values.[cite:82][cite:85] Your current workflow already recognizes that material profiles should be established through testing before real use, which aligns with this calibration-first approach.[cite:1]

### 2. Bridge length

A bridge can often print successfully without support even when it spans open air, but only up to a certain length. Support-free design guidance commonly places a conservative bridge target around 10 to 15 mm before sag risk rises materially, though printer tuning can stretch that higher.[cite:80]

This suggests a distinct rule in the workflow: do not trigger supports only because a feature is horizontal; first check whether the unsupported length is short enough to bridge cleanly with the active material and quality profile.[cite:80][cite:82]

### 3. Material behavior

Material choice changes support tolerance. PLA usually tolerates overhangs and bridging better because cooling is aggressive and layer solidification is faster, while PETG tends to sag and string more, and ABS adds warping and thermal-management concerns.[cite:82][cite:91]

That means support thresholds should be material-specific inside the workflow. A geometry that prints cleanly in PLA may be borderline in PETG and risky in ABS under the same orientation and layer height.[cite:82][cite:91]

### 4. Profile intent

Prototype, production, and quality jobs should not share the same support threshold. Prototype jobs can tolerate minor underside defects if they save time and material, while quality jobs should trigger supports earlier when a visible face or client-facing surface is at risk.[cite:3][cite:74]

A production part also requires special handling because the correct question is not only whether the feature can print unsupported, but whether it can do so repeatably enough for customer delivery without costly failures or cleanup variance.[cite:74][cite:78]

### 5. Surface criticality

A support decision should consider whether the threatened region is a visible customer-facing surface, a hidden underside, or a functional mating face. Supports can preserve geometry in one area while degrading surface quality where they attach, so the workflow should not treat all faces as equally important.[cite:70][cite:74]

A functional interior cavity or hidden underside may be acceptable with minor sagging, while a decorative face, snap-fit area, or tolerance-sensitive contact surface may justify support or reorientation.[cite:78][cite:80]

## Recommended Business Logic

### Default policy

The recommended default policy is:

- Supports disabled by default.[cite:70][cite:78]
- Attempt orientation optimization first.[cite:78][cite:80]
- Apply supports only when geometry, material, and finish-risk thresholds are exceeded.[cite:78][cite:91]
- Flag the job for user confirmation when the model sits in a gray zone rather than forcing supports automatically.[cite:3][cite:74]

This policy is the best fit for a commission workflow because it protects margin while still allowing support use on prints where failure risk is genuinely expensive.[cite:74][cite:78]

### Suggested threshold framework

The following starting framework is suitable for implementation and later calibration on Calliope.

| Variable | Prototype | Production | Quality |
|---|---|---|---|
| Overhang trigger | Use supports only for clearly steep regions; prioritize speed and low waste.[cite:81][cite:85] | Use supports for high-risk regions where failure or deformation threatens delivery reliability.[cite:74][cite:91] | Trigger sooner on visible or customer-facing surfaces to protect finish quality.[cite:70][cite:74] |
| Bridge trigger | Allow short unsupported bridges if they fall within calibrated limits.[cite:80] | Allow only validated bridges with consistent success history.[cite:3][cite:80] | Use tighter limits to avoid visible sag.[cite:82] |
| Material adjustment | PLA most permissive; PETG and ABS more conservative.[cite:82][cite:91] | Material-specific thresholds required.[cite:82][cite:91] | Most conservative thresholds for PETG and ABS.[cite:82] |
| Surface rule | Hidden surfaces can accept minor defects.[cite:74] | Functional surfaces prioritize geometry repeatability.[cite:78] | Visible surfaces prioritize finish quality.[cite:70][cite:74] |

### Suggested decision tree

A first-pass workflow model can use the following logic:

1. Analyze model orientation candidates and estimate overhang severity and bridge lengths for each orientation.[cite:78][cite:80]
2. Select the orientation with the lowest combined support burden and lowest visible-face risk.[cite:78][cite:80]
3. Compare the chosen orientation against the active material threshold and profile intent threshold.[cite:82][cite:91]
4. If risk is below threshold, slice with supports off.[cite:78]
5. If risk is above threshold but limited to small regions, recommend tree or localized supports rather than full-area supports.[cite:70][cite:78]
6. If risk is ambiguous, present the user with a warning in the consult report rather than auto-enabling supports.[cite:3][cite:74]
7. Log the final outcome and post-print feedback to refine thresholds over time.[cite:3][cite:1]

## Proposed Workflow Integration

The current Djinn workflow already follows this sequence: file drop, mesh analysis, consult report, user slice command, slice report, confirmation, print, and feedback logging.[cite:3] The support model should be inserted between mesh analysis and consult generation so that support recommendations appear before the user commits to a slice.[cite:3]

### Recommended consult report additions

The consult report should add the following fields:

- Estimated support risk: low, medium, high.[cite:78][cite:81]
- Worst overhang angle or overhang severity band.[cite:81][cite:91]
- Longest unsupported bridge estimate.[cite:80]
- Best orientation recommendation with reason.[cite:78][cite:80]
- Suggested support mode: none, local, full.[cite:70][cite:78]
- Confidence score based on past print history for similar geometry and material.[cite:3][cite:1]

This would allow the user to decide quickly while still preserving manual control, which matches the current workflow design that requires explicit confirmation before printing.[cite:3]

### Proposed support modes

A three-mode model is more useful than a binary yes/no setting.

| Mode | Use Case | Business Effect |
|---|---|---|
| None | Geometry falls inside validated support-free thresholds.[cite:78][cite:81] | Lowest cost and fastest throughput.[cite:70][cite:74] |
| Local | Only isolated regions are risky, such as a chin, arm, lip, or shelf.[cite:80][cite:91] | Moderate cost increase with limited cleanup burden.[cite:70] |
| Full | Large unsupported regions or orientation cannot be improved enough.[cite:81][cite:91] | Highest cost, highest post-processing load, should be exceptional rather than standard.[cite:70][cite:74] |

## Data Model for Implementation

A practical implementation can score each print with structured variables that are easy to derive from mesh analysis and slicing metadata.

### Input features

- Material: PLA, PETG, ABS.[cite:1][cite:3]
- Profile intent: prototype, production, quality.[cite:3]
- Layer height and speed priority from selected profile.[cite:3]
- Percentage of faces above threshold overhang band.[cite:81][cite:91]
- Maximum overhang severity.[cite:81]
- Longest unsupported bridge length.[cite:80]
- Visible-face involvement or critical-face tags if available.[cite:70][cite:74]
- Prior success or failure history by material and geometry class.[cite:3][cite:1]

### Output fields

- `supports_recommended`: true or false
- `support_mode`: none, local, full
- `risk_score`: 0 to 100
- `reason_codes`: e.g., `steep_overhang`, `long_bridge`, `visible_face`, `petg_sag_risk`
- `user_message`: plain-language explanation for the consult report

### Example heuristic score

A simple starting heuristic can be used before any machine learning model exists:

- Add risk for steep overhang area above calibrated threshold.[cite:81][cite:85]
- Add risk for bridge lengths beyond calibrated support-free span.[cite:80]
- Add risk for PETG and ABS relative to PLA.[cite:82][cite:91]
- Add risk for quality jobs and visible surfaces.[cite:70][cite:74]
- Subtract risk for successful prior prints with similar geometry/material.[cite:3][cite:1]
- Trigger local supports at moderate scores and full supports only at high scores.[cite:70][cite:78]

This approach is transparent, easy to audit, and appropriate for early production use before enough print history exists for a learned model.[cite:3][cite:74]

## Calibration Plan

The best implementation path is staged calibration rather than trying to solve everything with theory.

### Phase 1: Establish machine thresholds

Print standardized overhang and bridge tests for PLA, PETG, and ABS using the real production profiles planned for use on Calliope.[cite:82][cite:85] Record the clean threshold, acceptable threshold, and failure threshold for each material-profile combination.[cite:82][cite:85]

### Phase 2: Validate support recommendations

Run a curated set of real customer-like models across categories such as brackets, enclosures, figurines, cosplay pieces, and decorative items. Compare three strategies for each model: no supports, local supports, and full supports.[cite:74][cite:78]

### Phase 3: Close the loop with feedback

The current workflow already logs feedback by file hash and uses prior notes to inform later prints.[cite:3] That makes it possible to store support outcomes and progressively refine thresholds based on actual success, cleanup time, and final quality rather than intuition alone.[cite:3][cite:1]

## Operational Recommendations

### Recommended policy statement

For the Djinn workflow, supports should be treated as a controlled exception, not a default behavior. The system should optimize for orientation first, support-free printing second, localized supports third, and full supports only when the geometry or finish requirement clearly justifies the added cost.[cite:70][cite:78][cite:80]

### Implementation priorities

1. Add support-risk analysis to the consult stage.[cite:3]
2. Add material-specific overhang and bridge thresholds after calibration.[cite:82][cite:85]
3. Replace binary support decisions with none, local, and full support modes.[cite:70][cite:78]
4. Log support usage, failures, cleanup burden, and customer-facing quality results.[cite:3][cite:74]
5. Periodically review whether support-trigger thresholds are reducing failures without inflating cost per successful print.[cite:74][cite:78]

### Key business rule

The correct optimization target is not "maximum print safety at any cost." The correct target is "minimum total cost per successful customer-acceptable print," which includes material, machine hours, labor, failure rate, and finish quality together.[cite:74][cite:78]

## Conclusion

The evidence strongly supports implementing a selective support-decision model in the Djinn printing workflow rather than leaving supports on by default.[cite:70][cite:74][cite:78] A rules-based system using orientation, overhang severity, bridge length, material behavior, profile intent, and feedback history is practical now and can later evolve into a learned model as more print data accumulates.[cite:3][cite:80][cite:91]

The highest-value implementation path is to add support-risk scoring to the consult report, calibrate thresholds on Calliope with material-specific tests, and log post-print outcomes so the workflow improves over time.[cite:1][cite:3][cite:82]
