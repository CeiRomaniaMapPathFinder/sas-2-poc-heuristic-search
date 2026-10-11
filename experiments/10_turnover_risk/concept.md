# Turnover risk (pressing chain)

_Where the idea came from: ours, not in the brief._

## The football idea

A possession does not only take time — it can be **lost**. Every pass has a completion probability; a failed pass is a turnover, the team has to win the ball back (that costs effort) and starts again from where it was. A city is a good possession state if the expected total effort — road actually travelled plus turnover penalties — until the ball reaches the goal is small. Cities that can only progress through long, risky roads look bad; cities with short safe outlets look good.

## How h(n) is calculated

Parameters: `beta` (preference for easy passes), `gamma` (completion probability decay), `L` (effort to win the ball back after a turnover — taken from the graph as the mean road cost, 108.0, not invented), `kappa` (passer's preference for team-mates with a cheaper expected finish; 0 = none).

1. Pass choice: `P(u->v) ∝ exp(-beta*w) * exp(-kappa*K(v))`.
2. Completion: `C(u,v) = exp(-gamma*w)`.
3. Expected remaining effort (iterate until stable):

       K(goal) = 0
       K(u) = sum_v P(u->v) * [ w(u,v)                       the pass itself
                                + C(u,v) * K(v)               completed: continue from v
                                + (1 - C(u,v)) * (L + K(u)) ] lost: pay L, start again at u

   `K(u)` appears on both sides (a turnover restarts at `u`); solving for it:

       K(u) = sum_v P [ w + C K(v) + (1-C) L ]  /  ( 1 - sum_v P (1-C) )

4. `K` is in road units → `h(u) = floor(K(u) + 0.5)`, `h(goal) = 0`.

### Worked example (goal = Bucharest, beta = 0.01, gamma = 0.005, kappa = 0.005, L = 108.0)

**Giurgiu:** one pass, `C = exp(-0.005·90) = 0.638`.

    numerator   = 90 + 0.638·0 + 0.362·108.0 = 129.1
    denominator = 1 − 0.362 = 0.638
    K(Giurgiu)  = 129.1 / 0.638 = 202.5  ->  h = 203     (the pass fails 36 % of the time; each failure costs 108 and a retry)

**Pitesti** (after convergence `K(Rimnicu Vilcea) = 573`, `K(Craiova) = 733`):

| pass | P | C | P·[w + C·K(v) + (1−C)·L] |
|---|---:|---:|---:|
| → Bucharest (101) | 0.928 | 0.604 | 133.5 |
| → Rimnicu Vilcea (97) | 0.055 | 0.616 | 27.1 |
| → Craiova (138) | 0.016 | 0.502 | 9.2 |

    numerator   = 133.5 + 27.1 + 9.2 = 169.8
    denominator = 1 − (0.928·0.396 + 0.055·0.384 + 0.016·0.498) = 0.603
    K(Pitesti)  = 169.8 / 0.603 = 281.8  ->  h = 282

`h(Giurgiu) = 203 < h(Pitesti) = 282`. Both are far above the road cost (90, 101) because the restart loop is counted in full.

## Files

- `method.py` — `turnover_cost`, `build`.
- `experiment.py` — beta/gamma/L sweep, with and without the goal-aware passer; writes `results.md`.
- Java port: `../../tools/java/OtherHeuristics.java` (`TurnoverRisk`).
