# Progressive passing

_Where the idea came from: the football brief's progressive-passing section._

## The football idea

Analysts separate ordinary passes from **progressive passes**: passes that move the ball into a clearly better attacking position. A player whose available passes are mostly progressive is in a good spot.

Here "better position" is measured with the Expected Goal Threat of the receiver (`xGT`, Method 1), **not** with road distance.

## How h(n) is calculated

1. Compute `xGT(v)` for every city (experiment 01, cost-only passer: `beta`, `gamma`).
2. Pass choice: `P(u->v) = exp(-beta*w(u,v)) / sum_k exp(-beta*w(u,k))`.
3. Progress of one pass = threat gained:

       Prog(u,v) = max(0, xGT(v) - xGT(u))

4. Expected progress of the next pass from `u`:

       PPS(u) = sum over neighbours v of  P(u->v) * Prog(u,v)

5. Convert to "lower = better":

       raw(u) = -ln(PPS(u))        (or 1 / PPS(u), the doc's version — both tested)

6. PPS has no road-cost unit, so the table is **road-scaled**: multiply every raw value by one number `mean(d*) / mean(raw)` so h is comparable in size to g, then round to int. (True remaining cost `d*` is used only for that single scale factor; it cannot change the order of any city.) `h(goal)` is forced to 0.

### Worked example (goal = Bucharest, beta = gamma = 0.01)

xGT values after Method 1 converged: Bucharest 1, Giurgiu 0.407, Pitesti 0.137, Rimnicu Vilcea 0.020, Craiova 0.013.

**Giurgiu** (one road, to Bucharest): `P = 1`, `Prog = 1 − 0.407 = 0.593`, `PPS = 0.593`, `raw = -ln(0.593) = 0.52`.

**Pitesti** (Bucharest 101, Rimnicu Vilcea 97, Craiova 138):

| pass | P | Prog = max(0, xGT(v) − 0.137) | P·Prog |
|---|---:|---:|---:|
| → Bucharest | 0.366 | 0.863 | 0.316 |
| → Rimnicu Vilcea | 0.381 | 0 (0.020 < 0.137) | 0 |
| → Craiova | 0.253 | 0 | 0 |

`PPS(Pitesti) = 0.316`, `raw = -ln(0.316) = 1.15`.

Road scale for this goal is ≈ 66, so `h(Giurgiu) = 35`, `h(Pitesti) = 77`. Ordering correct.

## Files

- `method.py` — the formula above (`pps`, `build`).
- `experiment.py` — runs the `-log` and `1/x` transforms and a small beta/gamma sweep; writes `results.md`.
- Java port: `../../tools/java/OtherHeuristics.java` (`ProgressivePassing`).
