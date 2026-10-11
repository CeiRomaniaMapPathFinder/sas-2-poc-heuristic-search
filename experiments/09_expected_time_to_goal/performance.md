# Performance — Expected time to goal (possession clock)

Full tables: `results.md`.

| variant | pair checks | mean Spearman (20 goals) | weighted inversion penalty | A* optimal (380 pairs) | mean nodes expanded |
|---|---|---|---|---|---|
| beta=0.01 kappa=0 (random easy-pass player) | 5/8 | 0.937 | 0.030 | 72.9 % | 4.77 |
| beta=0.01 kappa=0.002 | 7/8 | 0.982 | 0.006 | 75.3 % | 4.73 |
| beta=0.01 kappa=0.005 | 7/8 | 0.990 | 0.002 | 75.5 % | 4.72 |
| beta=0.01 kappa=0.01 | 7/8 | 0.994 | 0.001 | 76.3 % | 4.73 |
| beta=0.01 kappa=0.05 (≈ shortest path) | 8/8 | 0.998 | 0.000 | 100 % | 4.94 |
| beta=0.02 kappa=0.005 | 7/8 | 0.987 | 0.003 | 83.7 % | 4.84 |
| baseline: straight-line | 6/8 | 0.848 | 0.083 | 100 % | 6.81 |

**Test 1.** `h(goal) = 0` by construction, unique minimum.

**Test 2.** 7/8 for the sensible kappa range: the one failure is **Arad vs Oradea (goal Sibiu)** again (243 vs 224) — a three-road city's passer wastes more time on detours than a two-road city's. Same dilution mechanism as the cost-only passer in experiment 01, and the same cure: a smarter passer (kappa ↑), which at kappa = 0.05 passes 8/8 but is then essentially computing shortest paths.

**Test 3–5.** At kappa = 0.005: Spearman 0.99, 5–6 inversions per goal, worst gaps ~30 (Craiova vs Eforie, Hirsova vs Fagaras). Sensible ordering.

**Test 6.** Poor: 75 % optimal. `T` includes the time wasted on detours, so h is 1.7–1.8× the true remaining cost (Timisoara→Bucharest: 861 vs 536) and A* turns greedy — exactly the pattern of the cost-only passer in experiment 01. Increasing kappa fixes it only by turning the passer into Dijkstra.

**Honest assessment of the idea.** The "possession clock" is intuitive and produces a beautifully interpretable number (seconds to goal), and it needs no `-log` or calibration. But mean first-passage time is dominated by wandering unless the walk is strongly goal-directed, and a strongly goal-directed walk is a shortest-path computation in disguise. There is no kappa where it is both "football-random" and A*-optimal. xGT has the same dial (tau) but its `-ln/gamma` scale sits closer to the true cost, which is why xGT reaches 94–99.7 % optimal at the tau where this method is at 75 %.

## Verdict

**Interesting, ranks well, bad at guiding A*.** Kept as this archive's example of a heuristic that needs no unit conversion at all — and of why that convenience was not worth the search behaviour.
