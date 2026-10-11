# Things that bit us

Written down because every one of these cost time, and most of them are not
specific to football heuristics.

## A model with no way to fail says nothing

The first version of xGT had no pass-completion probability. On a connected graph
every possession eventually reaches the goal, so the fixed point is 1 for every
city and `h` is 0 everywhere — A\* silently degenerates into uniform-cost search and
still returns correct answers, so nothing looks broken. The giveaway was the
expansion count sitting at exactly 11.0, the uniform-cost baseline.

Lesson: when a value model comes out constant, look for the missing absorbing
state before looking for a bug.

## Ranking and scale are different problems

Several methods ranked cities almost perfectly and still made A\* behave badly. The
cost-only passer reaches Spearman 0.99 and only 287 of 380 optimal routes, because
its `h` sits 1.8× above true cost; `f = g + h` is then dominated by `h` and A\*
becomes greedy best-first.

A heuristic needs the right *order* and a magnitude comparable to `g`. Two separate
tests, two separate fixes. Checking only correlation hides half the problem — which
is why the scoreboard carries both.

## Averaging over outlets dilutes; adding over them does not

xGT averages over a city's roads weighted by pass probability, so extra weak roads
pull the value down and a well-connected city can rank behind a worse-placed one
with fewer options. Press resistance sums over the same roads and the effect
disappears. One word of difference in the formula, opposite failure modes.

## Float equality never arrives

Our convergence loop originally wanted the table to stop changing. For 12 of the 20
goals the last bit of the double keeps flipping between two neighbouring values
forever, so an exact `next == current` test never fires. A tolerance is the right
test for floating point; `1e-12` here, reached in 34–40 iterations, while the
integer table is already final after at most 22.

The iteration cap in the code is an error guard, not the stopping condition. If it
is ever hit, something is wrong with the update, not with the limit.

## Python and Java round differently

Python's `round()` is half-to-even, Java's `Math.round` is half-up. A heuristic
value landing exactly on `.5` then differs between the research code and the
backend, which is the sort of thing that surfaces as one failing test months later.
Both sides use `floor(x + 0.5)`, and `tools/crosscheck.py` compares every city of
every goal between the two implementations to prove it.

## Update into a new table, not in place

The iteration has to read the previous round's values for every city (a synchronous
or Jacobi update). Updating in place means a city's new value depends on whether its
neighbour happened to be processed first, which makes the result depend on
dictionary order — stable enough to pass tests, wrong enough to differ between
languages.

## Using the true distance "just for scale" needs a rule

Methods whose score has no natural unit — press resistance, progressive passing,
centrality — have to be scaled before `f = g + h` means anything. We allowed exactly
one number per goal: `mean(d*) / mean(raw)`. It cannot reorder any city, and it is
stated in every method that uses it. The alternative, picking a scale by eye until
A\* looks good, is fitting to the answer with extra steps.

xGT does not need this: `−ln(xGT)/γ` is already in road-cost units.

## A structurally interesting measure can still be useless

Max-flow from city to goal is a real property of the network and says nothing about
distance; it ranks a dead-end city one road from the goal below a hub three roads
away. Bridges and cut vertices are real too, and on this map twelve cities have none
between them and Bucharest. Both ideas are defensible as graph theory and both fail
the first sanity pair.

Lesson: test the obvious comparisons first. Two minutes of Giurgiu-versus-Pitesti
would have saved an afternoon of max-flow.

## Combining good components can make things worse

Threat × support × progression scores well on ranking and worse on search than
threat alone, because both extra factors are ≤ 1 and push `h` further above the true
cost. On a 20-city graph the three ingredients are so strongly correlated that
multiplying them mostly changes the scale — in the wrong direction.

## The map is small, and small maps flatter

Twenty cities, twenty-three roads, one 2-connected western block and a tree-like
eastern tail. Several conclusions here are about this graph: that τ = 1.5 is enough,
that packing has nothing to measure, that re-opening closed nodes never matters in
practice. A larger or differently shaped map could change any of them, and nothing
in this repo has been tested against one.
