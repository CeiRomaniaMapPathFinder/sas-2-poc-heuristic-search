# Performance — Progressive passing

Full tables: `results.md`.

| variant | pair checks | mean Spearman (20 goals) | weighted inversion penalty | A* optimal (380 pairs) | mean nodes expanded |
|---|---|---|---|---|---|
| PPS, −log transform (beta=gamma=0.01) | 7/8 | 0.987 | 0.004 | 96.6 % | 5.26 |
| PPS, 1/x transform (doc's version) | 5/8 | 0.971 | 0.002 | 100 % | 9.21 |
| PPS −log, beta=0.02 | 7/8 | 0.990 | 0.002 | 97.4 % | 5.30 |
| PPS −log on value-aware xGT (tau=1) | 7/8 | 0.982 | 0.006 | 93.7 % | 5.20 |
| baseline: straight-line | 6/8 | 0.848 | 0.083 | 100 % | 6.81 |

**Test 1.** PPS(goal) = 0 by construction (nothing to progress to), which would give the goal the *worst* value. We force `h(goal) = 0`. Every other city has PPS > 0 because at least one neighbour is always more threatening (a consequence of `C < 1` in xGT).

**Test 2.** 7/8. The failure is again **Arad vs Oradea (goal Sibiu)**: h = 99 vs 83. Inherited from Method 1's dilution, because PPS is built on xGT with the same softmax pass choice.

**Test 3/4/5.** Spearman 0.98–0.99, 6–7 inversions of 171 pairs per goal, all with small gaps. Sensible ordering.

**Test 6.** Surprisingly good: 96.6 % optimal on all pairs with only 5.3 nodes expanded. Reason: `-ln(PPS)` **under**-estimates near the goal (Giurgiu 35 vs true 90, Pitesti 77 vs 101) and the road-scaling keeps the far cities around the true cost, so A* rarely gets greedy. The `1/x` transform is 100 % optimal but only because its values are tiny for most cities (it expands 9.2 nodes — almost UCS's 11), so it barely guides the search.

**What is unusual.** PPS rewards a city for the *jump* in threat the next pass gives, not for its own threat. Cities right next to the goal get very low h (Giurgiu 35, Urziceni 73) while mid-distance cities are close to true cost. As a standalone heuristic this makes the near-goal region "flat", which is harmless for A* but means the h values are not easy to read as "remaining cost".

## Verdict

**Usable standalone, better as a component.** Good ranking and good A* behaviour, but it inherits the Arad/Oradea inversion from the cost-only passer it is built on, and its values are harder to read as remaining cost. It is one of the three ingredients of the combined model (`../08_combined_model/`).
