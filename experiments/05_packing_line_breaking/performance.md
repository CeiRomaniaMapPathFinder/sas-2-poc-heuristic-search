# Performance — Packing / line breaking

Full tables: `results.md`.

| variant | pair checks | mean Spearman (20 goals) | weighted inversion penalty | A* optimal (380 pairs) | mean nodes expanded |
|---|---|---|---|---|---|
| lines count | 0/8 | 0.599 | 0.102 | 98.7 % | 7.93 |
| lines weighted by road cost | 0/8 | 0.583 | 0.110 | 98.7 % | 7.92 |
| baseline: UCS | 0/8 | 0 | 0 | 100 % | 11.0 |

**Test 1.** `h(goal) = 0`, but it is not the unique minimum: for goal Bucharest, 12 other cities also get 0.

**Test 2.** 0/8. Six of the eight checks are ties at 0, and the two non-ties are wrong the other way: Giurgiu (1 bridge to cross) gets h = 203 while Pitesti (no line to cross) gets 0. Structurally true, but as a "how far is the goal" signal it is backwards.

**Test 4/5.** Spearman −0.24 for goal Bucharest (66 tied pairs, 65 inversions); 0.80 for goal Sibiu because from Sibiu the whole east *is* a sequence of lines.

**Ring discrimination.** Worse than the old ring method: ring 1 has 4 cities and 3 distinct values, ring 2 has 5 cities and 3 values.

**Test 6.** 98.7 % optimal only because h ≈ 0 almost everywhere → it is UCS with a slight push through the eastern corridor (7.9 nodes expanded vs 11).

## Verdict

**Drop as a standalone heuristic.** The Romania map has one 2-connected western block and one tree-like eastern tail; "lines to break" is a property of the tail only. It could serve as a tie-breaker or as an additive corridor penalty inside another method, but none of the stronger methods needed it, so it was not carried into the combined model.
