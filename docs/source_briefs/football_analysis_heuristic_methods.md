# Football-analytics heuristics for the Romania map

A family of candidate `h(n)` functions built on football-analysis ideas. The aim is
not to reproduce football analytics faithfully — it is to borrow the parts that are
useful and read the Romania road network as a tactical progression network.

The requirement every candidate has to meet: cities genuinely better placed to reach
the goal should generally get smaller values. A candidate does not have to equal the
remaining road cost, be admissible, be consistent, or guarantee the optimal path. It
does have to guide A\* sensibly and make judgements that can be defended.

## 1. Why football analytics fits

Football analytics does not judge a player or a zone by distance to goal alone. It
also weighs the quality of the passing options available, whether the move makes
progress, how likely the action is to succeed, what alternative routes exist, how
much space the team controls, and whether a defensive line can be bypassed. That
extra structure is precisely what a plain distance heuristic on the Romania map is
missing.

| Romania graph | football reading |
|---|---|
| city | possession state / where the ball is |
| road | passing lane |
| road cost | pass difficulty, effort, risk |
| neighbouring cities | available passing options |
| cheap road | easy pass |
| expensive road | hard pass |
| goal city | the opponent's goal |
| route | passing sequence |
| branching | several passing options |
| bottleneck | defensive pressure, a narrow channel |
| alternative path | an alternative attacking move |

## 2. Expected Goal Threat — the core idea

Expected Threat (xT) values a position by the attacking outcomes reachable from it.
Translated here: `xGT(n)` is how promising city `n` is as a starting possession
state for eventually reaching the goal.

### Which pass the player chooses

Let `N(u)` be the neighbours of `u`. A cheap road should behave like an easy pass.
The simplest version is

```
q(u,v) = 1 / w(u,v)                   P(u->v) = q(u,v) / sum over k of q(u,k)
```

A smoother one, which is what we should actually use, is

```
q(u,v) = exp(-beta * w(u,v))          P(u->v) = q(u,v) / sum over k of q(u,k)
```

`beta > 0` controls how strongly road cost drives the choice. Small `beta`: cost
barely matters and the tactical network dominates. Large `beta`: cheap roads
dominate and the model becomes nearly greedy. The useful region is between the
extremes, and it should be found by testing rather than asserted.

Already at this point the model behaves differently from BFS rings: two cities at
the same hop distance can differ because one has several cheap useful neighbours
and the other does not.

### Whether the pass arrives

A football pass can fail, and that matters here, so model it:

```
C(u,v) = exp(-gamma * w(u,v))         gamma > 0
```

Cheap road, high completion probability; expensive road, lower. A failed pass is a
turnover and the possession is worth 0. The network now has two kinds of transition,
successful and failed, which is what stops every city from being equally good.

### The recursion

```
xGT(goal) = 1
xGT(u)    = sum over v of  P(u->v) * C(u,v) * xGT(v)
```

The value of a city depends on the quality of the next passes and on the value of
the states they lead to. Solve it by iterating until the values stop moving. This is
fundamentally unlike a ring method: the score propagates through the whole network.

### Turning threat into a heuristic

High `xGT` means promising, but A\* wants low to mean good, so

```
h(u) = -log( xGT(u) + epsilon )
```

with a small `epsilon` to avoid `log(0)`.

The chain is: graph → passing network → transition preference → pass completion →
future state value → expected threat → heuristic. The football mechanism drives the
mathematics at every step, which is the thing a renamed-distance heuristic cannot
claim.

### Sanity, and a warning

Even though this is not a shortest-path formula, it should still usually respect
better weighted position: `h(Giurgiu) < h(Pitesti)` for goal Bucharest, and
`h(Arad) < h(Oradea)` for goal Sibiu. Check it after computing, not before.

Raw xGT may overvalue a city with many mediocre options against one with a single
excellent route, because the expected-value model rewards branching. That is not
automatically wrong — football genuinely values branching. But if it repeatedly
makes clearly worse-placed cities look better, the model needs changing. **Do not
patch it with BFS rings.** Change the football model instead.

## 3. Progressive passing

Analysts separate ordinary passes from progressive ones: passes that move the ball
into a better attacking position. A road is progressive if it tends to lead to a
better goalward state.

Measure "better" with a graph-derived proxy rather than the true remaining cost —
lower local weighted burden, a stronger `xGT` at the destination, higher goal
influence, fewer difficult transitions left. Write `Prog(u,v)` for the goalward
progress a transition represents, then

```
PPS(u) = sum over v of  P(u->v) * Prog(u,v)
```

which reads as how much useful attacking progress the city's available passes are
expected to create. Convert with `h(u) = 1 / (PPS(u) + epsilon)`, or any other
decreasing transform.

## 4. Press resistance

A player with one usable passing option is easy to press; one with several strong
outlets is not. For a city, look at the number of useful outgoing routes, their
quality, how independent they are, and how varied.

```
simple:     PR(u) = number of neighbours whose transition quality is good enough
weighted:   PR(u) = sum over v of  C(u,v) * xGT(v)
```

This says how many realistic attacking options remain from this city. High press
resistance means hard to trap, several ways forward, robust progression. Convert
with `h(u) = 1 / (PR(u) + epsilon)`.

## 5. Route redundancy

A more structural version of the same intuition: count independent routes rather
than immediate outlets. Give each road a capacity derived from its cost and take the
maximum flow from the city to the goal:

```
capacity(u,v) = 1 / w(u,v)            R(u) = max-flow(u, goal)
```

`R(u)` reads as how many strong independent attacking channels exist from this
possession state. High redundancy is a better tactical state; low redundancy is easy
to trap. This one uses global graph structure, which makes it the most ambitious
idea in the set.

## 6. Packing and line breaking

"Packing" in football counts how many opponents an action bypasses. Here the
defensive lines are the structural weak points of the network: articulation points,
bridges, small cuts, bottlenecks, separator sets.

A city is in a better position if it has already moved past the important barriers
between it and the goal. So score the structural resistance still remaining:

```
PackingValue(n) = resistance already bypassed
h_pack(n)       = resistance still to come
```

This is not a ring method in disguise — the barriers come from the graph's
vulnerability structure, not from hop level.

## 7. Pitch control

Pitch-control models estimate how strongly a team controls each part of the field.
Translated: how strongly does the goal's influence reach each city through the
network? Set `Influence(goal) = 1` and propagate, with cheaper roads transmitting
more:

```
I(u) = sum over v of  exp(-lambda * w(u,v)) * I(v)          (with normalisation)
h(u) = -log( I(u) + epsilon )
```

A city sitting in a strong part of the goal's influence field is tactically close to
it. This resembles diffusion and random-walk models, and it should be presented that
way rather than as an electrical-network analogy, which would overlap with a
different family of heuristics.

## 8. Passing-network centrality toward the goal

Passing networks measure how important a player is in connecting possession. The
goal-oriented version asks whether a city is one that useful routes to the goal tend
to run through, whether it connects several progressive branches, and whether it
opens access to high-value downstream cities.

Candidate measures: goal-oriented betweenness, weighted PageRank seeded at the goal,
personalised PageRank, Katz-style influence, absorbing random-walk probability. Then
turn high strategic value into low `h`. This is the most promising way to separate
cities with similar raw distance but very different roles in the network.

## 9. Combining them

A combined score can carry more than one tactical idea. Multiplicative:

```
AttackValue(n) = xGT(n) * (1 + alpha * PressResistance(n)) * (1 + delta * ProgressiveScore(n))
h(n)           = -log( AttackValue(n) + epsilon )
```

A city is good when it has strong eventual goal threat, several usable options, and
next actions that tend to make progress. If the multiplicative form turns out to be
unstable, use a weighted sum of normalised components instead:

```
Score(n) = a * xGT_norm(n) + b * PR_norm(n) + c * PPS_norm(n)
h(n)     = 1 - Score(n)          (or -Score(n), depending on the scale wanted)
```

The numerical range does not matter. The ranking and the resulting A\* behaviour do.

## 10. Parameters

The model has several: `beta`, `gamma`, `alpha`, `delta`, `lambda`. None of them
should become arbitrary decoration. For each one, state its tactical meaning, test
several values, watch what happens to the ranking, and pick a value that balances
realism against useful search guidance.

`beta` is the clearest example. It controls how strongly players prefer easy passes.
Too small and road cost barely registers; too large and the model is greedy for the
cheapest edge. The useful setting is somewhere in between, and only testing will say
where.

## 11. Do not smuggle the shortest path in

The one thing that would invalidate all of this: computing the exact shortest
distance to the goal and dressing it up as a football score. For example

```
xGT(n) = 1 / trueShortestDistance(n)
```

is not football analysis, it is Dijkstra with a costume. Derive transition
probabilities from local road costs, propagate state values, use branching and route
redundancy and graph structure — and only then compare the result against the true
shortest distance.

## 12. How to evaluate

**Ground truth, for evaluation only.** Run Dijkstra for each goal to get
`d*(n, goal)`. It is the reference, never an input.

**Compute each candidate.** For every city: xGT, progressive score, press
resistance, optionally route redundancy and control score, and the combined score.

**Check the obvious pairs first.** `h(Giurgiu) < h(Pitesti)` for goal Bucharest;
`h(Arad) < h(Oradea)` for goal Sibiu.

**Then the full table**, and read it for correct ordering, strong inversions, odd
outliers, identical scores, and cities that look overvalued because they happen to
branch a lot.

| City | True remaining cost | xGT | Press resistance | Combined h |
|---|---:|---:|---:|---:|

**Rank quality.** Spearman correlation between `h` and `d*` — high positive is good,
perfect is not required. Pairwise inversions: count every pair where `d*(A) < d*(B)`
but `h(A) > h(B)`; lower is better. Not all inversions deserve equal weight, though.
Reversing 140 and 151 is a small mistake; reversing 90 and 500 is a serious one. So
weight each inversion by `|d*(A) − d*(B)|`, which comes much closer to what "makes
sense" actually means here.

**A\* behaviour.** For each heuristic record the path cost, whether it is optimal,
and the number of nodes expanded, against uniform-cost search, the straight-line
heuristic and the old ring heuristic.

| Method | Path cost | Optimal? | Nodes expanded |
|---|---:|---:|---:|

A non-optimal result does not by itself disqualify a candidate. The questions that
matter are whether it generally chose sensible states, whether it usually found a
cheap path, whether its mistakes were small and explainable, and whether it offered
a genuinely different perspective.

## 13. Suggested order of work

Build it in stages rather than all at once.

1. xGT alone, with `P(u->v)` as normalised `exp(-beta*w)` and `xGT(goal) = 1`. This
   is the baseline everything else is measured against.
2. Add pass completion probability, which makes expensive roads risky.
3. Add press resistance, which rewards having several usable options.
4. Add progressive passing, which rewards transitions that improve the position.
5. Optionally route redundancy, packing, pitch control, goal-oriented centrality.

Keep only the components that actually improve behaviour.

The strongest candidate on paper is Expected Goal Threat plus press resistance plus
progressive passing: city as possession state, road as passing lane, road cost as
pass difficulty, neighbour quality as attacking opportunity, multiple useful routes
as press resistance, future state propagation as expected threat, and the combined
attacking value as the heuristic.

Whatever comes out of it should answer one question — *if possession starts in this
city, how promising is the situation for eventually reaching the goal?* — rather
than "what is the exact shortest path cost?". The score should usually agree with
weighted goalward closeness, and controlled errors are acceptable as long as the
model stays sensible and genuinely different.
