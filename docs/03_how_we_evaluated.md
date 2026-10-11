# How every method was tested

The same battery runs for every heuristic, from `core/metrics.py`, driven by
`core/run_method.py`. No method was allowed a bespoke test, and no method was
tuned after seeing only its own numbers.

Ground truth is Dijkstra, `d*(city, goal)`, computed in `core/search.py`. It is used
for grading only — never inside a heuristic. (The one controlled exception, a single
scale factor for methods without a natural unit, is described in
`01_problem_and_design_rules.md` and flagged in the methods that use it.)

## Test 1 — does the goal win

`h(goal)` must be 0 and must be the unique minimum. Sounds trivial; it caught two
real bugs. Progressive passing scores the goal *worst* if you take the formula
literally, because the goal has nothing left to progress to. The combined model
produced values above 1 for cities next to the goal, which after the `-log` became
negative and clipped to 0, tying them with the goal.

## Test 2 — eight pairs where the answer is obvious

Hand-picked pairs where one city is plainly better placed than the other, so a
wrong answer is a wrong answer and not a matter of taste.

| goal | should be smaller | than | true costs |
|---|---|---|---|
| Bucharest | Giurgiu | Pitesti | 90 vs 101 |
| Bucharest | Urziceni | Fagaras | 85 vs 211 |
| Bucharest | Fagaras | Craiova | 211 vs 239 |
| Bucharest | Pitesti | Rimnicu Vilcea | 101 vs 198 |
| Sibiu | Arad | Oradea | 140 vs 151 |
| Sibiu | Rimnicu Vilcea | Zerind | 80 vs 215 |
| Sibiu | Fagaras | Pitesti | 99 vs 177 |
| Sibiu | Craiova | Timisoara | 226 vs 258 |

Arad vs Oradea is the interesting one. They are nearly the same distance from
Sibiu, so a method that is only roughly right gets it wrong — and the reason it
gets it wrong says something about the model. Several methods failed exactly here.

## Test 3 — the full table

Every city sorted by true remaining cost, next to its heuristic value and its rank
under each. A city more than three ranks out of place is flagged. This is the test
you read when a summary number looks fine but something is off; it is where you see
*which* cities a method misjudges rather than how many.

We also report **ring discrimination** here: for each hop-distance ring from the
goal, how many distinct heuristic values the cities in it receive. The old ring
method scores 1 distinct value per ring by construction — that is its whole
weakness — and anything that does the same is repeating the mistake.

## Test 4 — rank correlation

Spearman between `h` and `d*` over all 20 cities, then averaged over all 20 goals,
with the worst goal reported separately. A mean of 0.99 with a minimum of 0.70
would be a method that works except where it doesn't, and we wanted to see that.

## Test 5 — inversions, weighted

Count the pairs where `d*(A) < d*(B)` but `h(A) > h(B)`. Raw counts are misleading:
swapping two cities 11 apart is a rounding artefact, swapping two cities 300 apart
is nonsense. So each inversion is weighted by `|d*(A) - d*(B)|` and normalised by
the total over all pairs. The headline number, "weighted inversion penalty", is 0
for a perfect order and grows with how badly the mistakes are.

## Test 6 — what A\* actually does

Two parts.

*Fixed pairs.* Ten start/goal routes chosen to cover the map, including the awkward
ones: `Zerind → Bucharest` (two forks), `Eforie → Sibiu` (right across the map),
`Arad → Neamt` (the longest), `Bucharest → Arad` (the same route backwards).

*All 380 ordered pairs.* Every start with every goal. Three numbers come out: the
percentage where A\* returned the optimal-cost route, the mean overshoot when it
did not, and the mean number of cities expanded.

Expansions are the number that decides whether a heuristic is worth having. With
`h = 0` the search expands 11.0 cities on average; anything close to that is not
guiding. The A\* used for grading re-opens a closed node if a cheaper route to it is
found later, which is the safe implementation for a heuristic that may overestimate.

## Baselines in every table

Every `results.md` includes uniform-cost search, straight-line distance and the
ring method in the same table as the method's own variants, so no result is read in
isolation.

## Reproducibility

`python tools/run_all.py` runs the self-test, all ten experiments, the final model
and the Python–Java cross-check. Every `results.md` is overwritten from scratch, so
if a number in a hand-written page disagrees with a generated table, the generated
table is right and the page is stale.

`core/selftest.py` checks the harness itself before any of that: that the map has 20
cities and 23 roads, that Dijkstra agrees with the textbook (`Arad → Bucharest = 418`
via Sibiu, Rimnicu Vilcea, Pitesti), that A\* with `h = 0` matches Dijkstra on all 380
pairs, that Spearman returns 1 and −1 on constructed inputs, and that the ring
baseline really does give every city in a ring the same value.

`tools/crosscheck.py` goes further and runs the Java ports in `tools/java/` against
the Python for ten method/parameter combinations across four goals, asserting the
integer tables are identical. That is what makes it safe to say the backend computes
the same heuristic as the research.
