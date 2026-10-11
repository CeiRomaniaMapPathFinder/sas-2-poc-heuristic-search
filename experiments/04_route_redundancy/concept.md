# Route redundancy

_Where the idea came from: the football brief's route-redundancy section._

The structural version of press resistance. Instead of counting good outlets one
hop away, ask how much independent attacking channel exists from a city all the way
to the goal. In football terms: a player who can only be reached through one narrow
corridor is trappable; a player with several separate routes into them is not.

## How h is calculated

1. Give every road a capacity that falls with its cost:

       capacity(u,v) = 1 / w(u,v)

2. `R(u)` = maximum flow from `u` to the goal city, computed with Edmonds–Karp
   (written out longhand in `method.py` — with 20 cities, clarity beats speed).

3. More channel is better, so invert and scale into road-cost units:

       h(u) = road-scaled  1 / R(u)

   This method has no natural unit, so it uses the single-scalar calibration
   described in `../../docs/01_problem_and_design_rules.md`: one multiplier per
   goal, which cannot change the order of any city.

## What the numbers look like (goal = Bucharest)

| city | max-flow to Bucharest |
|---|---|
| Giurgiu | 0.0111 |
| Urziceni | 0.0118 |
| Pitesti, Craiova, Sibiu, Arad, Oradea, Zerind, Timisoara, Lugoj, Mehadia, Drobeta, Fagaras, Rimnicu Vilcea | 0.0146 |
| Hirsova, Eforie | 0.0102 |
| Vaslui, Iasi, Neamt | 0.0070 |

Twelve cities share one value. The 0.0146 is the capacity of Bucharest's two
western doors (Pitesti and Fagaras), and nothing west of them can do better than
that no matter how far away it is. Giurgiu scores *worse* than all of them on one
road of 90.

## Why it is in the archive

Because it is the clearest demonstration in the set of a structurally real
measurement that cannot do this job. Max-flow describes how wide the corridors are;
a heuristic needs to know how long they are. See `performance.md`.

## Files

- `method.py` — `max_flow`, `route_redundancy`, builder
- `experiment.py` — writes `results.md`
- No Java port: it never became a candidate.
