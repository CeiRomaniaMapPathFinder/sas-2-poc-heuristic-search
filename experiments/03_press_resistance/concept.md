# Press resistance

_Where the idea came from: the football brief's press-resistance section._

## The football idea

A player with only one passing option is easy to press: close that lane and the attack dies. A player with several **good** outlets is press-resistant. Translated to the map: a city is in a strong position if it has several roads that lead to threatening places.

## How h(n) is calculated

### The weighted version (the brief's)

1. `xGT(v)` for every city (the cost-only passer, experiment 01) and `C(u,v) = exp(-gamma*w)`.
2. Quality of one outlet = probability the pass arrives × how threatening the receiver is:

       quality(u,v) = C(u,v) * xGT(v)

3. Press resistance = all outlets added up (**not** averaged — more good outlets is better):

       PR(u) = sum over neighbours v of quality(u,v)

4. `raw(u) = -ln(PR(u))` (lower = better; the doc's `1/PR` is also tested), road-scaled to int, `h(goal) = 0`.

### The count version

`PR_count(u)` = number of neighbours whose quality is at least `theta` × the best quality at `u`; `h = 1/PR_count`, road-scaled. Tested with `theta = 0.5`.

The brief's route-redundancy section takes the same intuition to its structural extreme — count
independent channels all the way to the goal rather than outlets one hop away. That
is a different enough model that it lives in its own experiment,
[`../04_route_redundancy`](../04_route_redundancy).

### Worked example (goal = Bucharest, beta = gamma = 0.01)

**Giurgiu:** one outlet, `quality = C(90) · xGT(Bucharest) = 0.4066 · 1 = 0.4066`. `PR = 0.4066`, `raw = -ln(0.4066) = 0.90`.

**Pitesti:**

| outlet | C(u,v) | xGT(v) | quality |
|---|---:|---:|---:|
| → Bucharest (101) | 0.3642 | 1.0000 | 0.3642 |
| → Rimnicu Vilcea (97) | 0.3791 | 0.0205 | 0.0078 |
| → Craiova (138) | 0.2516 | 0.0126 | 0.0032 |

`PR(Pitesti) = 0.3752`, `raw = -ln(0.3752) = 0.98`. Road scale for this goal ≈ 67 → `h(Giurgiu) = 60`, `h(Pitesti) = 66`. Pitesti's two extra outlets earn it a small bonus (its `-ln` is only 0.08 above Giurgiu's although its direct pass is harder), which is exactly what press resistance is supposed to express.

Note the difference to xGT: xGT *averages* the outlets with the pass probabilities `P` (so extra weak outlets dilute the value); PR *adds* them (so extra outlets can only help). That single change makes PR under-estimate instead of over-estimate, which turns out to matter a lot for A*.

## Files

- `method.py` — `pr_sum`, `pr_count` and the builders.
- `experiment.py` — writes `results.md`.
- Java port of the weighted version: `../../tools/java/OtherHeuristics.java` (`PressResistance`). The count version was not ported; it failed the tests.
