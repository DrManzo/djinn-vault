---
subject: Psychology/Psych-Stats
tags: [statistics, psychology, gcu, psych-stats, probability, sampling, random-sampling, sampling-distribution, standard-error]
created: 2026-05-19
source: Perplexity
course: Psychology Statistics
---

# Probability

## Summary
Probability quantifies the likelihood of events and underpins statistical inference. Understanding probability requires distinguishing between sampling with and without replacement, recognizing that probabilities change when items are not replaced. The distribution of sample means forms the foundation for inferential statistics, with the central limit theorem ensuring that sample means approach normality as sample size increases regardless of population shape.

## Key Points
- When sampling **with replacement**, probabilities remain constant across draws because the population composition does not change
- When sampling **without replacement**, probabilities change after each draw because the population composition shifts
- In a bucket with 3 red, 4 white, and 3 blue balls (10 total): P(red) = 0.30, P(white) = 0.40, P(blue) = 0.30
- With replacement, second draw probabilities are identical to first draw probabilities
- Without replacement, second draw probabilities depend on what was drawn first (e.g., if first was red, P(red on second) = 2/9 ≈ 0.22)
- A **random sample** requires: each individual has an equal chance of selection, and probabilities stay constant for each individual selected
- The **standard error** of the mean: σM = σ / √n — it decreases as sample size increases
- The **central limit theorem**: for large samples (n ≥ 30), the distribution of sample means is approximately normal even if the population is skewed
- For small samples from a skewed population, the distribution of sample means is not guaranteed normal — probabilities cannot be determined
- For a population with μ = 58, σ = 12: P(X < 52) ≈ 0.3085, but P(M < 52) for n = 16 ≈ 0.0228 — larger samples produce more extreme z-scores for the same deviation
- Sample size needed for a target standard error: n = (σ / σM)²
- Knowing outcome tendencies (non-random behavior) changes optimal strategy — in rock-paper-scissors, if opponent throws scissors 55% of the time, throwing rock gives a 55% win probability
- For σ = 24: to achieve σM = 6 requires n = 16; σM = 3 requires n = 64; σM = 2 requires n = 144

## Details

### Sampling Distribution Properties
- The mean of the distribution of sample means equals the population mean (μ)
- The standard deviation of the distribution of sample means is the standard error (σM = σ / √n)
- As n increases, standard error decreases, making sample means cluster more tightly around μ
- The shape approaches normal as n increases (central limit theorem)

### When Normal Approximation Applies
| Population Shape | Sample Size | Can Use Normal Approximation? |
|-----------------|-------------|-------------------------------|
| Normal | Any n | Yes |
| Skewed | n < 30 | No — cannot be determined |
| Skewed | n ≥ 30 | Yes — central limit theorem |

## References
- Gravetter, F. J., Wallnau, L. B., Forzano, L. B., & Witnauer, J. E. (2021). *Essentials of statistics for the behavioral sciences* (10th ed.). Cengage.

## Related
- [[Psych Stats Hub]]
- [[Z-Scores]]
- [[Hypothesis Testing]]
- [[Population Distributions]]
- [[Statistics In Psychology Overview]]
