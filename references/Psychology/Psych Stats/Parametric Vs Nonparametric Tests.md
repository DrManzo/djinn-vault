---
subject: Psychology/Psych-Stats
tags: [statistics, psychology, gcu, psych-stats, parametric, nonparametric, chi-square, categorical-data, distribution-free]
created: 2026-05-19
source: Perplexity
course: Psychology Statistics
---

# Parametric Vs Nonparametric Tests

## Summary
Parametric tests assume a specific population distribution (typically normal) and estimate parameters like mean and variance, while nonparametric tests make few or no assumptions about the population distribution and are used with ordinal or nominal data. The chi-square test is the most common nonparametric test, analyzing frequencies of categorical outcomes without requiring normally distributed continuous data.

## Key Points
- **Parametric tests** assume a specific population distribution (usually normal) and estimate parameters (mean, variance)
- **Nonparametric tests** make few or no assumptions about the population distribution's form or parameters
- Nonparametric tests are often used with ordinal or nominal data where parametric assumptions cannot be met
- A **chi-square test** is nonparametric because it analyzes frequencies of categorical outcomes rather than assuming scores come from a normally distributed population
- Chi-square is distribution-free: the sampling distribution is derived from counts in categories, not requiring continuous or normally distributed dependent variables
- Chi-square requirements: data must be raw frequencies (counts), not percentages or transformed values
- Categories must be **mutually exclusive** — each observation falls into exactly one category per variable
- Observations must be **independent** — each subject contributes to only one cell
- Expected cell frequencies should generally be at least **5 per cell** for the chi-square approximation to be valid
- **Chi-square goodness of fit test**: used with one categorical variable to determine if observed frequencies match a specified theoretical distribution
- **Chi-square test for independence**: used with two categorical variables to evaluate whether there is an association between them in a contingency table
- In the goodness-of-fit test, expected frequencies come from external sources (theory, prior study, known ratio)
- In the test of independence, expected frequencies are calculated internally from the sample's own marginal totals
- The goodness-of-fit test is confirmatory (testing against a known expectation); the independence test is more exploratory
- The structure of data signals which test to use: a single row of observed vs. expected counts indicates goodness-of-fit; a two-way contingency table indicates independence

## Details

### Choosing Between Tests
| Question | Test to Use |
|----------|-------------|
| One variable vs. expected distribution | Chi-square goodness of fit |
| Two variables — are they related? | Chi-square test of independence |
| Continuous data, normal distribution | Parametric (t-test, ANOVA) |
| Ordinal/nominal data or non-normal | Nonparametric (chi-square, Mann-Whitney) |

### Chi-Square Formula
χ² = Σ[(fo - fe)² / fe]
where fo = observed frequency and fe = expected frequency

## References
- McHugh, M. L. (2013). The chi-square test of independence. *Biochemia Medica, 23*(2), 143-149. https://doi.org/10.11613/BM.2013.018
- Mayo Clinic. (n.d.). *Parametric and nonparametric: Demystifying the terms* [PDF]. Mayo Clinic Division of Biomedical Statistics and Informatics.
- Gravetter, F. J., Wallnau, L. B., Forzano, L. B., & Witnauer, J. E. (2021). *Essentials of statistics for the behavioral sciences* (10th ed.). Cengage.

## Related
- [[Psych Stats Hub]]
- [[Hypothesis Testing]]
- [[Probability]]
- [[Statistics In Psychology Overview]]
