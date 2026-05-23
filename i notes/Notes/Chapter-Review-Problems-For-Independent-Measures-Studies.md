---
subject: psychology/research-methods/statistics/independent-measures-studies
tags:
  - psychology/research-methods/analysis/methods
  - psychology/research-methods/t-tests
  - psychology/research-design/between-subjects
created: 2026-05-23
source: Perplexity export

# Chapter Review Problems for Independent-Measures Studies

## Summary
This note covers key concepts and problems related to independent-measures, or between-subjects, research studies in psychology.

## Key Points
- **Definition of an Independent-Measures Study**: Uses separate samples for each treatment or population.
- **Estimated Standard Error**: Measures variability in the sample mean difference.
- **Pooled Variance Calculation**:
  - Equal sample sizes: Pooled variance is halfway between the two sample variances.
  - Unequal sample sizes: Pooled variance leans towards the larger sample's variance.
- **Sample Mean Difference and Hypothesis Testing**:
  - Calculate pooled variance, estimated standard error, and t-statistic.
  - Determine significance based on critical t-values.

## Details
1. **Independent-Measures Study Definition**: An independent-measures study uses separate samples for each treatment or population being compared. This design is used to avoid carryover effects between treatments.
2. **Estimated Standard Error**:
   - Formula: \( \text{SE} = \sqrt{\frac{s_1^2}{n_1} + \frac{s_2^2}{n_2}} \)
   - Where \( s_1^2 \) and \( s_2^2 \) are the sample variances, and \( n_1 \) and \( n_2 \) are the sample sizes.
3. **Pooled Variance Calculation**:
   - Equal Sample Sizes: If both samples have the same size (\( n_1 = n_2 \)), the pooled variance is exactly halfway between the two sample variances.
     - Example 1: \( s_1^2 = 4, s_2^2 = 6 \)
       - Pooled Variance: \( s_p^2 = \frac{4 + 6}{2} = 5 \)
   - Unequal Sample Sizes: If the samples are of different sizes, the pooled variance leans towards the larger sample's variance.
     - Example 2: \( s_1^2 = 9, s_2^2 = 4 \), with \( n_1 > n_2 \)
       - Pooled Variance: \( s_p^2 \) will be closer to 9 than to 4.

4. **Hypothesis Testing**:
   - Calculate the pooled variance and estimated standard error.
   - Use the t-statistic formula: \( t = \frac{\bar{X}_1 - \bar{X}_2}{\text{SE}} \)
   - Compare the calculated t-value to the critical value for a given significance level (e.g., 0.05).

## Examples
- **Example 3**: Two samples, each with \( n = 10 \), have means of 86 and 99.
  - Sample Variances: \( s_1^2 = 4, s_2^2 = 9 \)
  - Pooled Variance: \( s_p^2 = \frac{4 + 9}{2} = 6.5 \)
  - Standard Error: \( \text{SE} = \sqrt{\frac{4}{10} + \frac{9}{10}} = \sqrt{1.3} \approx 1.14 \)
- **Example 4**: Sample means are 86 and 99, with variances of 4 and 9.
  - Pooled Variance: \( s_p^2 = 5.5 \)
  - Standard Error: \( \text{SE} = \sqrt{\frac{4}{10} + \frac{9}{10}} = \sqrt{1.3} \approx 1.14 \)

## Research Example
- **TV Viewing Habits and High School Grades**: A study by Anderson et al. (1998) found that high school students who watched Sesame Street as children had better grades than those who did not.
- **Hypothesis Testing**:
  - Sample Data: 
    - Watched Sesame Street: Mean = 86, \( n = 10 \)
    - Did Not Watch Sesame Street: Mean = 99, \( n = 10 \)
  - Null Hypothesis (\( H_0 \)): No difference in mean grades.
  - Alternative Hypothesis (\( H_a \)): There is a significant difference in mean grades.
  - Using a two-tailed test with \( \alpha = 0.05 \), the critical t-value is approximately 2.093.
  - Calculating the t-statistic: 
    - Pooled Variance: \( s_p^2 = \frac{4 + 9}{2} = 6.5 \)
    - Standard Error: \( \text{SE} = \sqrt{\frac{4}{10} + \frac{9}{10}} = \sqrt{1.3} \approx 1.14 \)
    - t-value: \( t = \frac{86 - 99}{1.14} \approx -12.7 \)
  - Conclusion: Reject the null hypothesis because the calculated t-value is more extreme than the critical value.

## References
- Anderson, D., Huston, A., Wright, J., & Collins, C. (1998). Television viewing and cognitive ability in early childhood. *Child Development*, 69(5), 1370-1384.
- Elbel, B., Gyamfi, M., & Kersh, R. (2011). Effects of menu labeling on fast-food purchases: A natural experiment. *Public Health Reports*, 126(2), 195-202.

## Related
- [[Psych-Stats-Study-Design]] — Overview of different research designs in psychology.
- [[Hypothesis-Testing-Methods]] — Detailed explanation of hypothesis testing procedures.
- [[T-Tests-and-P-Values]] — Understanding t-tests and p-values in statistical analysis.