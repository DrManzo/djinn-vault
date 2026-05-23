---
subject: psychology/statistics/nonparametric-testing/chi-square-test
tags:
  - cs/statistics
  - cs/testing/nonparametric
  - cs/testing/chi-square
  - cs/testing/distributions
created: 2026-05-23
source: Perplexity export
---

# Parametric vs. Nonparametric Testing: Chi-Square Test Explanation

## Summary
This note explains the difference between parametric and nonparametric testing, focusing on why a chi-square test is considered nonparametric.

## Key Points
- Parametric tests assume specific population distributions.
- Nonparametric tests make few or no assumptions about the distribution's form.
- Chi-square tests analyze categorical frequencies without assuming normality.

## Details
Parametric tests assume that data comes from a specific, often normal, distribution and estimate parameters like mean and variance. In contrast, nonparametric tests do not rely on such assumptions, making them suitable for ordinal or nominal data (McHugh, 2013; Mayo Clinic, n.d.).

A chi-square test is considered nonparametric because it evaluates the frequencies of categorical outcomes rather than assuming that scores come from a normally distributed population. It does not require distributional assumptions about the underlying population and can be used with raw frequency counts in contingency tables (McHugh, 2013; Mayo Clinic, n.d.).

To conduct a chi-square analysis, several key conditions must be met:
- Data in the contingency table should be raw frequencies.
- Categories for each variable must be mutually exclusive.
- Observations must be independent.
- Expected cell frequencies should generally be at least 5 per cell to ensure the chi-square approximation is valid.

## References
- McHugh, M. L. (2013). The chi-square test of independence. *Biochemia Medica*, 23(2), 143–149. https://doi.org/10.11613/BM.2013.018
- Mayo Clinic. (n.d.). Parametric and nonparametric: Demystifying the terms [PDF]. Mayo Clinic Division of Biomedical Statistics and Informatics. <https://www.mayo.edu/research/documents/parametric-and-nonparametric-demystifying-the-terms/doc-20408960>

## Related
- [[Parametric Vs Nonparametric Tests]] — similarity 0.92
- [[Hypothesis Testing]] — similarity 0.76
