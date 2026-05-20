---
subject: Psychology/Psych-Stats
tags: [statistics, psychology, gcu, psych-stats, homework, practice-problems, excel, spss, descriptive-statistics-project]
created: 2026-05-19
source: Perplexity
course: Psychology Statistics
---

# Homework And Practice Problems

## Summary
This note consolidates key homework assignments and practice problems from the Psychology Statistics course, including the Project 1 Descriptive Statistics assignment using TV viewing data, end-of-chapter problems on independent-measures and repeated-measures t-tests, and practical Excel/SPSS guidance for computing descriptive statistics and creating visualizations.

## Key Points
- **Project 1: Descriptive Statistics** — analyzed hours of television watched by 30 elementary children
  - Level of measurement: **Ratio** (true zero at 0 hours, equal intervals, meaningful ratios)
  - Mean: 37.70 hours, Median: 40.00 hours, Mode: 52 hours (appears 3 times)
  - Range: 64 hours (0 to 64), Variance: 384.94, Standard Deviation: 19.62 hours
- **Frequency Distribution**: 25 unique values; 52 appears 3 times (mode), 24/39/63 each appear twice, all others appear once
- **Histogram creation in Excel**: Insert → Column → Clustered Column, then format with axis labels and title
- **Excel formulas**: =AVERAGE(), =MEDIAN(), =MODE.SNGL(), =MAX()-MIN(), =VAR.P(), =STDEV.P()
- **COUNTIF formula for frequency**: =COUNTIF($A$2:$A$31, B2) — drag down for all unique values
- **Independent-measures t-test problems** (Chapter 10): pooled variance, standard error, hypothesis testing with Sesame Street viewing, calorie labeling, creativity and cheating, anxiety and decision-making
- **Repeated-measures t-test problems** (Chapter 11): difference scores, before/after designs, swearing and pain tolerance, exercise in nature vs. lab, gamification effects on motivation
- **Key distinction**: Independent-measures uses separate samples (44 participants for 22 per condition); repeated-measures uses the same sample (22 participants total)
- **Matched-subjects design**: two different sets of subjects matched on a specific variable
- **Homogeneity of variance assumption**: the two populations from which samples are drawn should have equal variances for the independent-measures t-test to be valid
- Increasing sample size increases t value and likelihood of rejecting H0 but has little effect on effect size measures
- Increasing variance decreases t value, reduces likelihood of rejecting H0, and decreases effect size measures

## Details

### Sample Variance vs. Population Variance
- Sample variance uses n - 1 (degrees of freedom correction) to provide an unbiased estimate
- Population variance uses N (the actual population size)
- The correction accounts for the fact that the sample mean is used in place of the unknown population mean

### T-Test Decision Framework
1. Identify design: independent-measures or repeated-measures?
2. Calculate pooled variance (independent) or difference scores (repeated)
3. Compute standard error
4. Calculate t statistic
5. Compare to critical t value (based on df and α)
6. Compute effect size (Cohen's d, r²)
7. Write results in APA format

## References
- Gravetter, F. J., Wallnau, L. B., Forzano, L. B., & Witnauer, J. E. (2021). *Essentials of statistics for the behavioral sciences* (10th ed.). Cengage.

## Related
- [[Psych Stats Hub]]
- [[Population Distributions]]
- [[Hypothesis Testing]]
- [[Statistics In Psychology Overview]]
- [[Practice Tests and Study Guides]]
