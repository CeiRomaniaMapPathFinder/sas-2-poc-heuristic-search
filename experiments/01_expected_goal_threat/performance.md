# Performance — Expected Goal Threat

Generated tables: `results.md`. Baselines are in the same table there.

| variant | sanity pairs | mean Spearman | weighted inversions | A\* optimal | expanded |
|---|---|---|---|---|---|
| no pass risk, to convergence | 0/8 | 0.000 | – | 380/380 | 11.00 |
| no pass risk, 3 passes | 7/8 | 0.902 | 0.004 | 360/380 | 5.91 |
| no pass risk, 6 passes | 7/8 | 0.977 | 0.007 | 380/380 | 5.83 |
| cost-only, β 0.01 γ 0.01 | 7/8 | 0.990 | 0.002 | 287/380 | 4.72 |
| cost-only, β 0.05 γ 0.01 | 7/8 | 0.974 | 0.010 | 330/380 | 4.85 |
| cost-only, β 0.01 γ 0.02 | 7/8 | 0.993 | 0.001 | 319/380 | 4.83 |
| value-aware, τ 1 | 8/8 | 0.997 | 0.000 | 358/380 | 4.92 |
| value-aware, τ 2 | 8/8 | 0.999 | 0.000 | 380/380 | 4.94 |
| **value-aware, τ 1.5 β 0.02 (kept)** | **8/8** | **0.999** | **0.000** | **380/380** | **4.94** |
| baseline: straight-line | 6/8 | 0.848 | 0.083 | 380/380 | 6.81 |
| baseline: ring / minimum-edge | 4/8 | 0.975 | 0.001 | 380/380 | 5.60 |

## Test by test

**Goal sanity.** `h(goal) = 0` and unique for every variant except the degenerate
one, where everything is 0.

**The eight obvious pairs.** The cost-only passer gets 7 of 8. The failure is Arad
versus Oradea for goal Sibiu: 269 against 252, where the true costs are 140 and 151.
Arad has three roads, so the softmax spreads its pass probability onto Zerind and
Timisoara as well; Oradea has two. This is the dilution the brief warns about when it says raw xGT can
overvalue a city with many mediocre options. With τ = 1 it flips the right way (159 against 166).

**Full table and rings.** Every city is within three ranks of its true rank, and
every hop ring receives distinct values — four distinct values in a four-city ring,
five in a five-city ring. The ring baseline gives one value per ring by
construction, which is the specific weakness this method was meant to fix.

**Inversions.** Cost-only, goal Bucharest: 4 of 171 pairs, worst gap 30 (Craiova
239 against Eforie 269). At the kept settings: zero inversions for Bucharest, Sibiu
and Neamt.

**A\*.** Where the cost-only passer falls over. Only 287 of 380 routes come out
optimal, not because the order is wrong but because the scale is: `h` is about 1.8×
the true remaining cost — Timisoara to Bucharest is 932 against a true 536 — so `f`
is dominated by `h` and the search behaves like greedy best-first, taking
Sibiu → Fagaras → Bucharest (450) instead of Sibiu → Rimnicu Vilcea → Pitesti (418).

The inflation has the same cause as the dilution: every hop through a multi-road
city multiplies xGT by a probability below 1, and `−ln(P)/γ` adds 30 to 70 units per
hop. Fixing the passer fixes both — at the kept settings `h` sits 0–9 % above true
cost and all 380 routes come out optimal while expanding 4.94 cities.

## Verdict

The first formulation is unusable and the second is right in concept but wrong in
scale, which the brief itself predicted ("a scale or calibration error, not
necessarily a conceptual error"). The value-aware passer repairs both from inside
the football model, and that version is what the project kept —
see [`../../docs/05_why_xgt_won.md`](../../docs/05_why_xgt_won.md).

One caution for anyone extending this: do not raise τ past about 1.5 without
checking `../../docs/08_is_it_just_shortest_path.md`. At τ = 3 the heuristic for
Arad and Oradea toward Sibiu is 140 and 151 — the exact road costs — and the model
has turned into Dijkstra.
