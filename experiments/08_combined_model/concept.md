# Combined model (threat x support x progression)

_Where the idea came from: the football brief's section on combining the ideas._

## The football idea

The doc's preferred final candidate: a city is a good possession state when it
1. has strong **eventual goal threat** (xGT, Method 1),
2. has several **usable outlets** (press resistance PR, Method 3),
3. its next passes tend to **make progress** (progressive passing PPS, Method 2).

## How h(n) is calculated

All three ingredients come out of one xGT run (`beta`, `gamma`, `tau`):

    xGT(u)  = sum_v P(u->v) C(u,v) xGT(v)           (Method 1)
    PR(u)   = sum_v C(u,v) xGT(v)                    (Method 3)
    PPS(u)  = sum_v P(u->v) max(0, xGT(v) - xGT(u))  (Method 2)

Normalise PR and PPS by their largest non-goal value so both are in 0..1: `PR_n`, `PPS_n`.

### Multiplicative version

    AttackValue(u) = xGT(u) * (1 + alpha*PR_n(u)) / (1 + alpha) * (1 + delta*PPS_n(u)) / (1 + delta)
    h(u) = floor( -ln(AttackValue(u)) / gamma + 0.5 )

The divisions by `(1+alpha)` and `(1+delta)` are our addition: they keep every multiplier ≤ 1, so `AttackValue ≤ xGT ≤ 1` and the goal stays the unique best state. Without them, cities next to the goal got `AttackValue > 1`, negative h, and were clipped to 0 — tied with the goal. Read it as "a city keeps its full threat only if it also has the best support and the best progression; otherwise it is marked down".

### Weighted-sum version

    Score(u) = a * xGT_n(u) + b * PR_n(u) + c * PPS_n(u)
    h(u)     = road-scaled (1 - Score(u)), rounded

### Worked example (goal = Bucharest, beta = gamma = 0.01, tau = 1, alpha = delta = 1)

For Pitesti: `xGT = 0.321`, `PR_n = 0.85`, `PPS_n = 0.42` (Urziceni has the largest PR, Giurgiu the largest PPS; those define 1.0).

    AttackValue = 0.321 * (1 + 0.85)/2 * (1 + 0.42)/2 = 0.321 * 0.925 * 0.71 = 0.210
    h(Pitesti)  = -ln(0.210)/0.01 = 156   (xGT alone would give 114)

For Giurgiu: `xGT = 0.407`, `PR_n = 0.82`, `PPS_n = 1.0`:

    AttackValue = 0.407 * 0.91 * 1.0 = 0.371  ->  h(Giurgiu) = 99   (xGT alone: 90)

Ordering kept (99 < 156), but both values moved further above the true remaining cost (90, 101). That mark-down is what hurts A* in performance.md.

## Files

- `method.py` — `ingredients`, `build_multiplicative`, `build_weighted_sum`.
- `experiment.py` — alpha/delta grid on both the doc's xGT (tau=0) and the value-aware xGT (tau=1); writes `results.md`.
- Java port: `../../tools/java/OtherHeuristics.java` (`Combined`).
