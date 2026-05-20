---
subject: Psychology/Psych-Stats
tags: [statistics, psychology, gcu, psych-stats, frequency-distribution, histogram, variance, standard-deviation, sum-of-squares]
created: 2026-05-19
source: Perplexity
course: Psychology Statistics
---

# Population Distributions

## Summary
Population distributions describe how scores are spread across a measurement scale. Understanding distributions involves organizing data through frequency distribution tables and histograms, then characterizing them with measures of central tendency and variability. Linear transformations affect the mean and standard deviation in predictable ways, and the shape of a distribution determines which statistical measures are most appropriate.

## Key Points
- A **regular frequency distribution table** shows the exact frequency for each individual score, preserving individual score data
- A **grouped frequency distribution table** shows frequencies for intervals, losing individual score information but managing large datasets
- **Bar graphs** are used for nominal or ordinal data with spaces between adjacent bars
- **Histograms** are used for interval or ratio data with adjacent bars touching at real limits
- The **population mean** formula: μ = ΣX / N
- The **population variance** formula: σ² = Σ(X - μ)² / N
- The **population standard deviation** formula: σ = √(Σ(X - μ)² / N)
- **Sum of Squares (SS)** definitional formula: SS = Σ(X - M)²
- **Sum of Squares (SS)** computational formula: SS = ΣX² - (ΣX)²/n
- **Sample variance** divides by n - 1: s² = SS / (n - 1)
- **Sample standard deviation**: s = √(SS / (n - 1))
- Adding a constant to all scores shifts the mean but does not change the standard deviation
- Multiplying all scores by a constant multiplies both the mean and standard deviation by that constant
- In a study of number-talk and children's math scores, high number-talk parents' children scored noticeably higher (M = 4.00) than low number-talk parents' children (M = 2.50)
- Reaction time data often follows non-normal distributions, making both mean and median valuable measures
- Older adults show more conservative decision criteria in cognitive tasks but their rates of evidence accumulation remain largely intact

## Details

### Linear Transformations
For a new variable Y = bX + A:
- Mean: μY = bμX + A
- Standard deviation: σY = |b| × σX
- Variance: σY² = b² × σX²

### Key Formulas Summary
| Measure | Population | Sample |
|---------|-----------|--------|
| Mean | μ = ΣX/N | M = ΣX/n |
| Variance | σ² = SS/N | s² = SS/(n-1) |
| Standard Deviation | σ = √(SS/N) | s = √(SS/(n-1)) |

### Interpolated Median (Continuous Scores)
Median = LRL + [(0.5N - fbelow) / fmedian] × width

## References
- Gravetter, F. J., Wallnau, L. B., Forzano, L. B., & Witnauer, J. E. (2021). *Essentials of statistics for the behavioral sciences* (10th ed.). Cengage.

## Related
- [[Psych Stats Hub]]
- [[Statistics In Psychology Overview]]
- [[Weighted Mean And Central Tendency]]
- [[Z-Scores]]
- [[Probability]]
