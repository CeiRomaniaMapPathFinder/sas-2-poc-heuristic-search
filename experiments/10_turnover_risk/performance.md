# Performance — Turnover risk (pressing chain)

Full tables: `results.md`.

| variant | pair checks | mean Spearman (20 goals) | weighted inversion penalty | A* optimal (380 pairs) | mean nodes expanded |
|---|---|---|---|---|---|
| beta=0.01 gamma=0.005, L=mean edge (random passer) | 5/8 | 0.931 | 0.033 | 79.2 % | 4.87 |
| beta=0.01 gamma=0.01, random passer | 6/8 | 0.928 | 0.034 | 74.7 % | 4.94 |
| beta=0.01 gamma=0.005, L=0 (no penalty) | 5/8 | 0.931 | 0.033 | 79.2 % | 4.88 |
| goal-aware passer kappa=0.002 | 7/8 | 0.984 | 0.004 | 83.7 % | 4.84 |
| **goal-aware passer kappa=0.005** | 7/8 | 0.990 | 0.003 | 87.1 % | 4.83 |
| goal-aware passer kappa=0.01 | 7/8 | 0.989 | 0.004 | 86.8 % | 4.83 |
| baseline: straight-line | 6/8 | 0.848 | 0.083 | 100 % | 6.81 |

**Test 1.** `h(goal) = 0`, unique minimum.

**Test 2.** Random passer: 5/8 — the ball wanders, so Urziceni (85) gets K = 2029 and Pitesti (101) is ranked behind Iasi (319). With the goal-aware passer 7/8; the remaining failure is **Fagaras vs Craiova (goal Bucharest)**, 828 vs 733: Fagaras's only forward pass is the 211-cost road with completion probability 0.35, so 65 % of possessions from Fagaras are lost and retried, while Craiova has two medium roads. Football-wise defensible ("Fagaras is a dead end with one very risky ball"), distance-wise wrong by 28.

**Test 3–5.** Goal-aware: Spearman 0.98 (Bucharest) / 0.995 (Sibiu); 2–7 inversions per goal.

**Test 6.** 87 % optimal at kappa = 0.005. Better than expected-time-to-goal (75 %) because the turnover penalty is applied *per pass* and so scales with the number of hops, which behaves more like a constant-factor inflation than the wandering of the possession clock. Still not competitive with the xGT family.

**The penalty L barely matters.** L = 0 and L = mean edge give the same ranking: the restart term `(1−C)·K(u)` already dominates. That means the "win the ball back" story adds almost nothing measurable on this graph — an honest negative result.

## Verdict

**Ranks acceptably, guides A* only moderately.** The mechanism is a reasonable football story, but numerically it behaves like the cost-only passer expressed in cost units, with extra inflation from the restart term. Kept as a documented experiment, not a candidate.
