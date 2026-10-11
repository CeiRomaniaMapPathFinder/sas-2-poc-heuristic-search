# Expected Goal Threat (xGT)

_Where the idea came from: the football brief's Expected Goal Threat section._

The model that ended up being used. This folder is the experiment — the model is
in `../../core/xgt.py` because four other experiments build on it, and the chosen
parameters are pinned in `../../final/method.py`.

For the final version written out in full, with worked examples, see
[`../../docs/06_xgt_explained.md`](../../docs/06_xgt_explained.md).

## The football idea

Expected Threat asks what a position is worth in terms of what you can do next: a
zone is valuable because the zones reachable from it are valuable. The value is
defined circularly and solved by iteration, and it is propagated backwards from the
goal.

On the map a city is where the ball is, a road is a passing lane, the road cost is
how hard that pass is, and the destination city is the goal. `xGT(city)` is the
chance that a possession starting there reaches the goal.

## How h is computed

```
C(u,v) = exp(-gamma * w(u,v))                     the pass arrives
P(u->v) ~ exp(-beta * w(u,v)) * xGT(v)^tau        which road the passer picks

xGT(goal) = 1
xGT(u)    = sum over roads (u,v) of  P(u->v) * C(u,v) * xGT(v)     iterate to a fixed point

h(u) = floor( -ln(xGT(u)) / gamma + 0.5 )         integer, road-cost units, h(goal) = 0
```

Dividing by gamma is what puts `h` into road-cost units: along a chain of passes
xGT is a product of `exp(-gamma*w)` terms, so `-ln` of it is gamma times a sum of
road costs.

## The three stages this experiment covers

**No pass risk.** Drop `C` entirely, as the brief's first version does. On a
connected map the ball can never be lost, so every possession eventually arrives and
the fixed point is 1 everywhere — `h` is 0 for every city and A\* quietly becomes
uniform-cost search. Running it with a fixed horizon of 3 or 6 passes gives
something non-trivial, but cities the ball cannot reach in that many passes all
collapse to the same value.

**Cost-only passer (tau = 0).** Add the completion probability and the model works:
cheap roads are preferred, long roads lose the ball, values decay outward from the
goal. This is the brief's main formulation. It ranks well and overestimates badly —
see the performance notes.

**Value-aware passer (tau > 0).** The passer also prefers receivers that are
themselves threatening. This is our change to the model, and the reason for it is a
specific failure: with tau = 0, Arad (three roads) is ranked behind Oradea (two
roads) for goal Sibiu, even though Arad is genuinely closer. The brief predicted
this dilution effect and warned against patching it with hop counts, so the fix had
to come from inside the football model — a real player passes to a team-mate in a
good position, not just down the shortest lane.

## Parameters

| | meaning | effect of raising it |
|---|---|---|
| beta | preference for short roads | passer gets greedier about road length |
| gamma | how fast completion probability falls; also the unit of `h` | `h` shrinks toward the road cost |
| tau | preference for threatening receivers | fixes dilution; too high and the model becomes shortest path |

Sweeps and the reasoning behind the kept values are in
[`../../docs/07_parameter_study.md`](../../docs/07_parameter_study.md).

## Files

- `experiment.py` — runs all three stages and the parameter sweeps, writes `results.md`
- `../../core/xgt.py` — the model
- `../../tools/java/XgtHeuristic.java` — the Java port used for cross-checking
