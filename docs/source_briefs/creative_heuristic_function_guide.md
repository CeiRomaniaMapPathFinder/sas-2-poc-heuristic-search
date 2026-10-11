# Creative heuristic design for the Romania A\* assignment

A working brief: what the assignment is really asking for, which of our earlier
assumptions were too strict, how a candidate heuristic should behave, and how to
tell whether one is any good. It deliberately does not prescribe a formula — the
point is to leave room for ideas that are not another variation on BFS rings.

## 1. The problem

The classic Romania city graph: cities are nodes, roads are edges, road costs are
edge weights, and the goal is a chosen destination such as Bucharest or Sibiu. A\*
evaluates

```
f(n) = g(n) + h(n)
```

where `g(n)` is the cost already paid to reach `n` and `h(n)` estimates how
promising `n` is with respect to the goal. The assignment asks for `h(n)` to be
creative.

## 2. Admissibility is not the point here

Our earlier work assumed `h` had to satisfy the full optimality conditions,

```
0 <= h(n) <= h*(n)            admissible
h(n) <= c(n,n') + h(n')       consistent
```

and that assumption quietly decided everything that followed. Guaranteeing a lower
bound pushes every idea into the same few shapes: BFS rings, graph cuts,
minimum-edge barriers, additive bounds — in other words, shortest-path estimates
wearing different clothes. All correct, none interesting.

For this assignment the requirement is looser. What we are building is not a
provable lower bound on the remaining path. It is a **score from a different
conceptual system** that says how promising a city is as a place to continue from.
A good one will:

- usually give lower values to cities genuinely better placed to reach the goal;
- avoid rankings that are obviously nonsense;
- use the structure of the network rather than a single edge;
- reinterpret the graph through another domain, and let that domain affect the
  mathematics;
- guide A\* toward a cheap path, ideally the cheapest.

Optimality is desirable, not mandatory. Consider goal = Sibiu with

```
h(Arad) = 30        f(Arad)   = 75 + 30 = 105
h(Oradea) = 31      f(Oradea) = 71 + 31 = 102
```

A\* prefers Oradea even though the route through Arad is cheaper overall. That is
acceptable: the heuristic still says Arad is the better state, and the only problem
is that the gap between 30 and 31 is too small next to the gap between 71 and 75.
This is a scale error, not a conceptual one — but a better heuristic reduces how
often it happens.

## 3. What "closer" means

Not geographically closer, not fewer hops, not the cheapest road leaving the
current city, and not what looks close on a drawn map. A city is closer when it is
in a **better weighted position to reach the goal**.

```
Giurgiu -> Bucharest = 90
Pitesti -> Bucharest = 101
```

So a sensible heuristic has `h(Giurgiu) < h(Pitesti)`. The values need not be 90 and
101 — 12 and 20, or 0.18 and 0.22, or 8 and 50 all express the same thing. The scale
is free; the ordering is not.

## 4. Evaluate the state, not the route that reached it

Goal = Sibiu, starting from Zerind:

```
Zerind --75--> Arad   --140--> Sibiu      total 215
Zerind --71--> Oradea --151--> Sibiu      total 222
```

The first road toward Oradea is cheaper (71 < 75), but the route through Arad is
better. From the goal's point of view Arad is the stronger remaining state, so we
want `h(Arad) < h(Oradea)`. The cost already paid to get to either belongs to `g`.

The same rule stated generally: `h(Arad)` must depend only on how promising Arad is
from Arad onward. Whether the search arrived there from Zerind, Timisoara or
anywhere else is history, and history is `g`'s job.

## 5. What counts as creative

A heuristic is creative when the graph is reinterpreted as something else, and the
behaviour of that something else is what produces the score:

> graph → reinterpretation in another domain → that domain's mechanism → a value per
> node → `h(n)`

Domains worth considering: football analytics, epidemic spread, traffic congestion,
information diffusion, ecological networks, game strategy, market liquidity,
communication reliability, energy flow, risk propagation, social influence, swarm
behaviour, biological signalling.

The test is whether the mechanism does the work. If the domain is only mentioned in
the write-up, it is not doing any.

## 6. What does not count

**Renaming the edge weight.** Call road cost a "transaction fee" and then set
`h(n) = road cost`. Nothing has changed.

**Rescaling it.** `1.07 × cost`, `sqrt(cost)`, `cost / 100`, `cost + tax`,
`cost × fuel_price`. Still the same number.

**Decorative storytelling.** "Cities are banks, roads are transaction channels" —
and underneath, the mathematics is still BFS ring, minimum edge, sum. If deleting
the story leaves the method unchanged, the story was decoration.

**Invented node attributes.** Wealth, income, population, traffic, player rating,
attack strength, risk appetite. Anything assigned to a city by hand can be tuned
until the heuristic says whatever we want. Values must be derived from the graph.

## 7. What may be used

Node connectivity, edge weights, the set of neighbours, alternative routes,
branching, bottlenecks, centrality, path redundancy, flow, transition probabilities,
weighted progression, diffusion, and local or global network structure. Anything
else — external data in particular — should be cleared first.

## 8. Required behaviour

**H1 — the goal wins.** `h(goal) = 0`, or at minimum the smallest value in the table.

**H2 — better weighted position means lower h.** If city A is clearly better placed
than city B, then `h(A) < h(B)`. Giurgiu versus Pitesti, above, is the simplest case.

**H3 — judge the node, not the path to it.** See section 4.

**H4 — small mistakes are tolerated, systematic nonsense is not.** A creative
heuristic may misjudge two similar states. With true remaining costs of 140 and 151,
producing 30 and 31 is fine — the order is right and only the scale is weak.
Producing 95 and 10 is not: that asserts B is far better than A with nothing behind
the claim.

## 9. Why the ring method was not enough

Our earlier "financial" heuristic took `L(v)`, the hop distance from the goal, and
accumulated the minimum edge weight crossing each layer. It is valid, and it has one
fatal property: **cities in the same ring usually get the same value**. The
heuristic then cannot tell apart a city with several good onward options, a city at
the end of one narrow corridor, a city whose alternatives are all expensive, and a
city with real route redundancy.

Anything new should distinguish cities by more than their hop level. A stronger
pattern combines several graph-derived signals — weighted progress, the quality of
the next options, route redundancy, the difficulty of future transitions, network
position — into something that answers "how promising is this state?" rather than
"how far away is it?".

## 10. How to test a candidate

Do not reject a heuristic simply because it is not admissible. Test the separate
properties separately.

**Test 1 — goal sanity.** Is `h(goal)` zero, and is it the minimum?

**Test 2 — obvious pairs.** Hand-pick comparisons where the answer is not a matter
of opinion: `h(Giurgiu) < h(Pitesti)` for goal Bucharest, `h(Arad) < h(Oradea)` for
goal Sibiu.

**Test 3 — the full ordering.** For every city, put the true best remaining cost
next to the heuristic value and judge each row.

| City | True remaining cost | h | Sensible? |
|---|---:|---:|---|

The true cost is for evaluation only. It must not be an input to the heuristic
unless that has been agreed deliberately.

**Test 4 — rank correlation.** Spearman between `h` and the true remaining cost. A
high positive value means the ordering generally makes sense. Perfect correlation is
not the target — a heuristic that correlates perfectly is a shortest-path
calculation.

**Test 5 — inversions.** Count the pairs where `trueCost(A) < trueCost(B)` but
`h(A) > h(B)`. A few are acceptable. Many, or a few very large ones, are not.

**Test 6 — A\* behaviour.** Run the search and record the path, its total cost and
the number of nodes expanded, against uniform-cost search (`h = 0`), the
straight-line heuristic and the old ring heuristic. Optimality is desirable but not
mandatory; expansions are what show whether the heuristic is doing anything.

## 11. Checklist before accepting a heuristic

*Concept* — Does it reinterpret the graph as another system? Is that system
meaningfully different from shortest-path distance? Does the choice of domain change
the mathematics?

*Mathematics* — Does the score use network behaviour rather than a single edge? Does
it involve several neighbours, paths, transitions, flow or structure? Can two cities
in the same hop ring get different values?

*Sanity* — Does the goal get the best value? Do obviously closer cities get lower
`h`? Are there any absurd reversals?

*Search* — Does A\* generally move toward useful cities? Does it usually find a good
path? Are its mistakes understandable rather than random?

*Explanation* — Can the analogy and the formula be explained together without one
contradicting the other? If the story is removed, is there still a distinctive
mechanism?

## 12. The direction we are taking: football analytics

Football analytics is a good fit because it already evaluates **states** rather than
distances. Being near the goal is not the only thing that matters: the available
passing options matter, progressive actions matter, network support matters,
alternative routes matter, and the probability of completing an action matters. The
resulting value can differ from literal distance and still rank states sensibly —
which is exactly what this assignment is asking for.

Concepts worth adapting: Expected Threat (xT), progressive passing, press
resistance, passing-network centrality, pitch control, line breaking and packing,
transition probability, possession value. A companion document works these out in
detail.

The heuristic should end up answering "how promising is this city for eventually
reaching the goal?" — not "how many rings away is it?" and not "what is the road
distance multiplied by something?". The goal is a new evaluation system, not a
renamed shortest path.
