# Performance — Goal-seeded passing-network centrality

Full tables: `results.md`.

| variant | pair checks | mean Spearman (20 goals) | weighted inversion penalty | A* optimal (380 pairs) | mean nodes expanded |
|---|---|---|---|---|---|
| lambda=0.01 damping=0.85 | 6/8 | 0.971 | 0.012 | 100 % | 5.01 |
| lambda=0.01 damping=0.5 | 8/8 | 0.990 | 0.004 | 95.8 % | 5.04 |
| lambda=0.01 damping=0.95 | 5/8 | 0.906 | 0.047 | 100 % | 5.25 |
| lambda=0.02 damping=0.85 | 6/8 | 0.958 | 0.017 | 99.5 % | 5.02 |
| lambda=0 damping=0.85 | 7/8 | 0.956 | 0.021 | 90.0 % | 5.01 |
| baseline: ring min-edge | 4/8 | 0.975 | 0.001 | 100 % | 5.60 |

**Test 1.** `h(goal) = 0`, unique minimum (after the `ln(pi(goal)/pi(u))` transform; an earlier shift-by-minimum version tied Urziceni with the goal at 0 and was replaced).

**Test 2.** 6/8 at the default damping: fails **Giurgiu vs Pitesti** (174 vs 146) and **Fagaras vs Craiova** (276 vs 270). Both for the same reason — dead-end or low-degree cities receive fewer random visits than well-connected ones, regardless of road cost. A low damping (0.5, the ball restarts at the goal often) makes the walk short-ranged and fixes the ordering (8/8) but weakens A* (95.8 %).

**Test 4/5.** Spearman ≈ 0.95–0.97; 14–15 inversions per goal, worst gaps 20–30. Noticeably noisier than xGT / press resistance / pitch control.

**Test 6.** A* is 100 % optimal at damping 0.85 with 5.0 nodes expanded — good search behaviour, because the road-scaled values are generally under-estimates.

## Verdict

**Works, but middling; not chosen.** The centrality idea distinguishes hubs from dead ends nicely (what the design guide asks for when it criticises the ring method), but exactly that property fights the "closer = lower h" requirement for dead-end cities next to the goal (Giurgiu). Fine as a demonstration that goal-seeded random walks carry distance information; the absorbing version of the same walk (xGT) is simply the better fit for a heuristic.
