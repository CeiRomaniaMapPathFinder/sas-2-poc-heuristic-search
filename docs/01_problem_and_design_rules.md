# The problem, and the rules we set ourselves

## What was asked

A\* on the Romania map evaluates `f(n) = g(n) + h(n)`. `g(n)` is the road cost already
paid; `h(n)` is an estimate of what is left. The assignment asked for a *creative*
`h(n)` — the textbook straight-line distance was explicitly not what was wanted.

The brief that framed it is
[`source_briefs/creative_heuristic_function_guide.md`](source_briefs/creative_heuristic_function_guide.md);
the football ideas we then worked from are in
[`source_briefs/football_analysis_heuristic_methods.md`](source_briefs/football_analysis_heuristic_methods.md).
Everything in this repository is downstream of those two documents. Both were edited
for readability when this archive was put together — same rules, same methods,
tighter prose.

## What "closer to the goal" was taken to mean

Not geographically closer, not fewer hops, not the cheapest single road out. A city
is closer when it is in a **better weighted position to reach the goal**. The brief's
own example:

```
Giurgiu -> Bucharest = 90        so we want   h(Giurgiu) < h(Pitesti)
Pitesti -> Bucharest = 101
```

The values do not have to be 90 and 101. The *order* is what has to be right.

A second example mattered more than it first looked:

```
Zerind -> Arad   (75) -> Sibiu (140) = 215      cheaper route, dearer first road
Zerind -> Oradea (71) -> Sibiu (151) = 222      cheaper first road, dearer route
```

A heuristic that only looks at the next road prefers Oradea. A heuristic that
evaluates the *state* prefers Arad. This single pair ended up driving one of our
parameter choices; see `05_why_xgt_won.md`.

## Admissibility: deliberately not a hard constraint

The usual requirement is `0 <= h(n) <= h*(n)`, plus consistency if you want A\* to
never re-expand. The brief relaxed this on purpose, because insisting on a provable
lower bound pushes every idea back into the same shape: BFS rings, minimum-edge
sums, graph cuts — all correct, none interesting.

So we allowed ourselves heuristics that can overestimate, and treated optimality as
something to *measure* rather than something to guarantee. It turned out we could
have both, but we did not design for it.

## Rules we imposed on ourselves

These were decided before any code and are what the experiments are judged against.

**The true remaining cost may never enter a heuristic.** Dijkstra runs in this repo
only to grade results. A heuristic that reads `d*` and transforms it is not a
heuristic, it is a disguise. The one exception, used by a few methods and flagged
every time it happens, is a single scalar: a method whose score has no natural unit
is multiplied by `mean(d*) / mean(raw)` so that `h` is comparable in size to `g`.
One number, applied to the whole table, cannot change the order of any city — and
the methods that mattered in the end did not need it.

**No coordinates.** Straight-line distance is in here as a baseline to beat, not as
an ingredient. The heuristic has to come out of the road list.

**No invented city attributes.** No wealth, population, "attack rating" or anything
else we could have made up. Everything is derived from the graph: road costs,
degree, which roads lead where.

**`h(goal) = 0`**, and integers. The integer part was a practical decision: the
backend works in integer road costs, and a float heuristic invites rounding
disagreements between languages. It also forces the scale question into the open
rather than hiding it in decimals.

**The story has to drive the mathematics.** If you can delete the football framing
and the formula is unchanged, the framing was decoration. The test we used: would
removing the analogy leave a distinctive mechanism behind? Renaming road cost to
"transaction fee" fails that test. A pass-completion probability that changes which
neighbour the model prefers passes it.

## What this repository is not

It is not a proof that xGT is the best possible creative heuristic for this map.
Two other methods here score as well on the numbers. It is a record of what we
tried, what the measurements said, and the reasoning behind the choice — including
the parts where the reasoning was a judgement call rather than a result.
