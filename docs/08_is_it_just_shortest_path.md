# "Isn't this just the shortest path with extra steps?"

The fair version of the question, asked of our own work, because it is the first
thing a reader should ask about any heuristic that ranks cities almost exactly in
order of their true remaining cost.

Short answer: the mechanism is not a shortest-path computation, the output is
deliberately close to one, and there is a dial that turns it into one — we stopped
before that point on purpose.

## The mechanism does not use distance

`core/xgt.py`, `core/football_math.py` and `final/method.py` contain no call to
Dijkstra or any other search. The inputs are the road list and three constants.
Dijkstra lives in `core/search.py` and is used by `core/metrics.py` to grade
results after the fact.

The strongest evidence is a failure rather than an argument: with τ = 0 the model
ranks Arad *behind* Oradea for goal Sibiu and sends A\* down a route costing 532
instead of 493. A formula computed from true distances could not make that mistake.
The model makes it because a three-road city spreads its pass probability over bad
options — a property of the passing model, not of the map's distances.

## The output is a smoothed shortest path, and that is on purpose

Unrolled, `−ln(xGT(u))/γ` is a soft minimum over all walks from `u` to the goal of
(road cost + a hesitation penalty at every fork). As τ grows the soft minimum
sharpens into a hard one, the pass choice becomes deterministic, and the recursion
becomes Bellman's equation. At that point xGT *is* the shortest path.

So τ is a slider between "random football" and "Dijkstra":

| τ | mean \|h − d\*\| / d\* | values exactly equal to d\* (of 380) |
|---|---|---|
| 0 | 0.87 | 3 |
| 0.5 | 0.33 | 3 |
| 1 | 0.15 | 4 |
| **1.5 (kept)** | **0.07** | **4** |
| 2 | 0.03 | 6 |
| 3 | 0.01 | 34 |
| 5 | 0.008 | 233 |

At τ = 5 the heuristic reproduces the exact true remaining cost for 233 of 380
city/goal values. That is the version of this method that would deserve the
accusation. At τ = 1.5 it reproduces 4.

This is not special to xGT. Every propagation method in this repo has the same
property, because the thing we were asked to rank cities by — "better weighted
position toward the goal" — is close to what `d*` measures. Correlating with `d*`
is the job. Being *derived from* `d*` would be the cheat.

## What the difference is made of

The surplus is not noise. Goal = Bucharest, at the kept settings:

| city | d\* | h | h − d\* | roads | multi-road cities on its best route |
|---|---|---|---|---|---|
| Giurgiu | 90 | 90 | 0 | 1 | 0 |
| Pitesti | 101 | 106 | 5 | 3 | 1 |
| Hirsova | 183 | 193 | 10 | 2 | 1 |
| Rimnicu Vilcea | 198 | 212 | 14 | 3 | 2 |
| Sibiu | 278 | 302 | 24 | 4 | 3 |
| Arad | 418 | 453 | 35 | 3 | 4 |
| Timisoara | 536 | 584 | 48 | 2 | 4 |

`h − d*` tracks the number of forks the possession has to pass through, not the
distance. It is a hesitation tax: each junction where the modelled passer might take
the wrong road adds a few units. A city at the end of a single lane pays nothing —
Giurgiu's heuristic is exactly 90, its road cost, because a player with one option
never hesitates.

That is also precisely why the heuristic is not admissible: `d*` assumes a perfect
chooser, and this model does not have one.

## How we would phrase it if challenged

xGT is a value-propagation model on the road network: a city's value is the
probability that a modelled passing process starting there reaches the goal. It
never computes a shortest path. Because a sensible passer prefers good roads, its
ordering agrees with true remaining cost — Spearman 0.999 — while its magnitude
carries a fork-dependent penalty that shortest-path cost does not have. τ
interpolates continuously between a random passer (87 % away from `d*`) and a
perfect one (which *is* `d*`); we stopped at 7 % so the heuristic remains a model
rather than a renamed distance.
