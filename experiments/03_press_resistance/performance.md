# Performance — Press resistance

Full tables: `results.md`.

| variant | pair checks | mean Spearman (20 goals) | weighted inversion penalty | A* optimal (380 pairs) | mean nodes expanded |
|---|---|---|---|---|---|
| **PR_sum, −log (beta=gamma=0.01)** | **8/8** | **0.993** | 0.002 | **100 %** | 5.36 |
| PR_sum, 1/x (doc's transform) | 6/8 | 0.973 | 0.001 | 100 % | 9.07 |
| PR_sum, −log, gamma=0.02 | 8/8 | 0.996 | 0.001 | 97.4 % | 5.07 |
| PR_sum, −log on value-aware xGT (tau=1) | 7/8 | 0.994 | 0.001 | 100 % | 4.99 |
| PR_count, theta=0.5 | 0/8 | 0.154 | 0.106 | 97.6 % | 9.07 |
| baseline: straight-line | 6/8 | 0.848 | 0.083 | 100 % | 6.81 |

## The weighted version: the surprise of this archive

- **Test 2:** 8/8, including Arad < Oradea for goal Sibiu (88 vs 95) — the case the cost-only passer gets wrong. Adding the outlets instead of averaging them removes the dilution.
- **Test 4/5:** Spearman 0.989 (Bucharest) / 0.994 (Sibiu); 3–5 inversions per goal, worst gap 28 (Hirsova 175 vs Fagaras 140; Fagaras looks better than it is because its one outlet, Sibiu, is a hub with high xGT).
- **Test 6:** 100 % optimal on all 380 pairs with 5.4 nodes expanded (UCS 11, straight-line 6.8). Because the sum over outlets is ≥ the best single outlet, `-ln(PR)` is a bit *below* the xGT-style cost, so after road-scaling h rarely overestimates → A* stays optimal while still being well guided.

## The count version: fails

Counting outlets throws away almost all information: most cities have 2–3 roads and only 1 outlet passes the `theta` test, so 15+ cities share the same value. Spearman 0.15, 0/8 pair checks. Not usable (and not creative — it is basically a degree count).

## Verdict

**Weighted version: keep.** A strong heuristic on its own, the second ingredient of
the combined model, and the source of the most useful single observation in the
project — summing over outlets instead of averaging over them flips the whole method
from over- to under-estimating. It was a serious candidate for the final pick; the
argument that decided against it is in `../../docs/05_why_xgt_won.md`, and it is
about the model's independence rather than its numbers.

**Count version: drop.** It is a degree count with extra steps.
