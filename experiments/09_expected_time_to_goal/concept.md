# Expected time to goal (possession clock)

_Where the idea came from: ours, not in the brief._

## The football idea

Commentators talk about how long a team needs to get from its own half into the box. Instead of asking "how likely is a goal from here?" (xGT) we ask **"how many seconds does a possession starting here need until the ball reaches the goal?"** — averaged over every passing sequence the players might realistically produce, back-passes and wasted detours included.

| Romania graph | Football reading |
|---|---|
| road cost `w` | seconds the pass takes |
| `T(city)` | expected seconds from here until the goal is reached |

## How h(n) is calculated

Parameters: `beta` (preference for easy passes), `kappa` (how strongly the passer prefers team-mates who are closer to finishing).

1. Pass choice (a smart passer looks at both):

       P(u->v) = exp(-beta * w(u,v)) * exp(-kappa * T(v))  /  sum over neighbours of the same

   `kappa = 0` is a player who only cares about easy passes and wanders; `kappa` large is a player who always finds the fastest route.

2. Expected time (iterate until stable, start with 0):

       T(goal) = 0
       T(u)    = sum over neighbours v of  P(u->v) * ( w(u,v) + T(v) )

   "Time of the next pass, plus the expected time from wherever it lands."

3. `T` is already in road units, so

       h(u) = floor( T(u) + 0.5 )      h(goal) = 0 automatically.

No calibration, no `-log`, no shortest-path distance anywhere.

### Worked example (goal = Bucharest, beta = 0.01, kappa = 0.005)

After convergence `T(Rimnicu Vilcea) = 366`, `T(Craiova) = 405`.

**Giurgiu:** one pass, `T = 90 + 0 = 90`.

**Pitesti:** three options.

| pass | w | exp(-beta w) | exp(-kappa T(v)) | P (normalised) | P·(w + T(v)) |
|---|---:|---:|---:|---:|---:|
| → Bucharest | 101 | 0.364 | 1.000 | 0.795 | 0.795·(101 + 0) = 80.3 |
| → Rimnicu Vilcea | 97 | 0.379 | 0.160 | 0.133 | 0.133·(97 + 366) = 61.5 |
| → Craiova | 138 | 0.252 | 0.132 | 0.072 | 0.072·(138 + 405) = 39.3 |

`T(Pitesti) = 80.3 + 61.5 + 39.3 = 181.1` → `h = 181`.

`h(Giurgiu) = 90 < h(Pitesti) = 181`. Pitesti's number is far above its road cost 101 because 20 % of the time this passer sends the ball the wrong way first and has to come back — the "possession clock" counts that whole detour.

### The kappa dial

- `kappa = 0`: pure random walk. From Urziceni (85 from Bucharest) the ball wanders for an expected **930** units, and Pitesti (101) is ranked worse than Iasi (319). Fails.
- `kappa = 0.005`: ranking is right (Spearman 0.99) but times are ~1.7× the road cost.
- `kappa = 0.05`: the passer is almost perfect and `T` ≈ shortest path (the circular case).

## Files

- `method.py` — `expected_time`, `build`.
- `experiment.py` — beta/kappa sweep; writes `results.md`.
- Java port: `../../tools/java/OtherHeuristics.java` (`ExpectedTime`).
