---
subject: Psychology/Psych-Stats
tags: [statistics, psychology, gcu, psych-stats, hypothesis-testing, t-test, null-hypothesis, confidence-interval, effect-size]
created: 2026-05-19
source: Perplexity
course: Psychology Statistics
---

# Hypothesis Testing

## Summary
Hypothesis testing provides a formal procedure for evaluating whether observed differences in sample data reflect real population effects or are attributable to sampling error. The process involves stating null and alternative hypotheses, setting decision criteria, computing test statistics, and making decisions about the null hypothesis. Both independent-measures and repeated-measures t-tests are commonly used, with effect size measures (Cohen's d, r²) quantifying the practical significance of findings.

## Key Points
- The four steps of hypothesis testing: (1) Determine null and alternative hypotheses, (2) Set criteria for decision, (3) Collect data and compute sample statistic, (4) Decide whether to reject or fail to reject the null hypothesis
- A **t statistic** is used when the population standard deviation is unknown and must be estimated from the sample
- A **z-score** is used when the population standard deviation is known and/or the sample size is large (n ≥ 30)
- The t distribution accounts for extra uncertainty when estimating variability from a sample, especially with small samples
- **Standard error** for a t-test: sM = s / √n
- **t statistic**: t = (M - μ) / sM
- Degrees of freedom for single-sample t-test: df = n - 1
- For a two-tailed test with α = .05 and df = 15, tcritical = ±2.131
- **Cohen's d** measures effect size: d = (M - μ) / s — values of 0.2, 0.5, and 0.8 represent small, medium, and large effects
- **r²** measures percentage of variance accounted for: r² = t² / (t² + df)
- **Confidence intervals** estimate the range in which the population mean likely falls
- An **independent-measures** (between-subjects) study uses a separate sample for each treatment condition
- A **repeated-measures** (within-subjects) design uses the same sample in both treatment conditions, removing individual differences
- **Pooled variance** combines variance estimates from two samples, weighted by their degrees of freedom
- In a study on answering questions while studying, students who answered questions scored significantly higher (M = 78.3) than the class average (μ = 73.4), t(15) = 2.333, p < .05, d = 0.58
- Students using e-books scored significantly lower (M = 77.2) than the class average (μ = 81.7), t(8) = -2.37, p < .05, 90% CI [73.67, 80.73]
- Repeated-measures designs reduce variance by removing individual differences, increasing the likelihood of detecting treatment effects

## Details

### Independent-Measures t-Test
- Pooled variance: sp² = (SS1 + SS2) / (df1 + df2)
- Estimated standard error: s(M1-M2) = √(sp²/n1 + sp²/n2)
- t statistic: t = (M1 - M2) / s(M1-M2)
- df = n1 + n2 - 2

### Repeated-Measures t-Test
- Uses difference scores (D) for each participant
- t = MD / sMD, where sMD = sD / √n
- df = n - 1 (number of participants, not scores)
- Advantage: eliminates individual differences that contribute to variance

### When to Use t vs. z
| Condition | Use |
|-----------|-----|
| σ known, any n | z-test |
| σ unknown, n ≥ 30 | z-test (approximation) or t-test |
| σ unknown, n < 30 | t-test |

## References
- Gravetter, F. J., Wallnau, L. B., Forzano, L. B., & Witnauer, J. E. (2021). *Essentials of statistics for the behavioral sciences* (10th ed.). Cengage.
- Ackerman, R., & Goldsmith, M. (2011). Metacognitive regulation of text learning: On screen versus on paper. *Journal of Experimental Psychology: Applied, 17*(1), 18-32.
- Weinstein, Y., McDermott, K. B., & Roediger, H. L. (2010). A comparison of study strategies for passages: Rereading, answering questions, and generating questions. *Journal of Experimental Psychology: Applied, 16*(3), 308-312.

## Related
- [[Psych Stats Hub]]
- [[Probability]]
- [[Z-Scores]]
- [[Parametric Vs Nonparametric Tests]]
- [[Statistics In Psychology Overview]]
