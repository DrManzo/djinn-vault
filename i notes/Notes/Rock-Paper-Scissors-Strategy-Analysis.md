---
subject: psychology/probability/game-strategy
tags:
  - probability/strategy/rock-paper-scissors
  - psychology/human-behavior/predictive-analysis
created: 2026-05-23
source: Perplexity export

# Rock-Paper-Scissors Strategy Analysis

## Summary
This note discusses the optimal strategy for rock-paper-scissors when one player has observed tendencies in their opponent's choices. The analysis reveals that choosing 'rock' maximizes winning probability given certain probabilities of the opponent's choices.

## Key Points
- **Game Setup**: Rock beats scissors, scissors beat paper, and paper beats rock.
- **Scenario**: You are arguing with a roommate over control of the television remote using rock-paper-scissors.
- **Opponent’s Probabilities**:
  - Rock: 28%
  - Scissors: 55%
  - Paper: 17%
- **Optimal Choice**: Based on opponent's tendencies, 'rock' has the highest probability (55%) of winning.

## Details
To determine the best choice in rock-paper-scissors when you have information about your opponent’s choices, follow these steps:

### Step 1: Find the Missing Probability
Given probabilities:
- Rock: 28%
- Scissors: 55%
- Paper: \(1 - 0.28 - 0.55 = 0.17\) or 17%

### Step 2: Compute Winning Probabilities for Each Throw
- **Rock**:
  - Wins against scissors (55%).
  - Probability of winning with rock: \(P(\text{win} \mid \text{rock}) = P(\text{roommate scissors}) = 0.55\).

- **Paper**:
  - Wins against rock (28%).
  - Probability of winning with paper: \(P(\text{win} \mid \text{paper}) = P(\text{roommate rock}) = 0.28\).

- **Scissors**:
  - Wins against paper (17%).
  - Probability of winning with scissors: \(P(\text{win} \mid \text{scissors}) = P(\text{roommate paper}) = 0.17\).

### Conclusion
The highest probability of winning is with 'rock' at 55%. Therefore, choosing rock maximizes your chances of winning the game.

## References
- [Reddit Post](https://www.reddit.com/r/statistics/comments/8fx399/what_are_the_odds_you_win_rock_paper_scissors/)
![](https://www.google.com/s2/favicons?sz=128&domain=reddit.com)
![](https://www.google.com/s2/favicons?sz=128&domain=remptongames.com)

## Related
- [[Psych-Stats-Rock-Paper-Scissors]] — Detailed analysis of the game and strategies.
- [[Probability-Strategies-Games]] — General strategies for probability-based games.