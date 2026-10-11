# Implementation spec

This is the document the backend was built from: everything needed to reimplement
the heuristic in another language, plus the values an implementation has to
reproduce before it can be trusted. It is kept with the archive so the repo is
self-contained — someone can port xGT from this page alone.

Written for the handover in September 2026; the "as built" section at the end
records where it ended up.

## Inputs

### The graph

Undirected, 20 cities, 23 roads. City ids are these exact strings — note
`"Rimnicu Vilcea"` with a space, which is what both the API and the frontend use:

```
Arad, Bucharest, Craiova, Drobeta, Eforie, Fagaras, Giurgiu, Hirsova, Iasi, Lugoj,
Mehadia, Neamt, Oradea, Pitesti, Rimnicu Vilcea, Sibiu, Timisoara, Urziceni, Vaslui, Zerind
```

```
Arad-Zerind 75        Arad-Sibiu 140        Arad-Timisoara 118     Zerind-Oradea 71
Oradea-Sibiu 151      Timisoara-Lugoj 111   Lugoj-Mehadia 70       Mehadia-Drobeta 75
Drobeta-Craiova 120   Craiova-Rimnicu Vilcea 146   Craiova-Pitesti 138
Rimnicu Vilcea-Sibiu 80    Rimnicu Vilcea-Pitesti 97   Sibiu-Fagaras 99
Fagaras-Bucharest 211 Pitesti-Bucharest 101 Bucharest-Giurgiu 90   Bucharest-Urziceni 85
Urziceni-Hirsova 98   Hirsova-Eforie 86     Urziceni-Vaslui 142    Vaslui-Iasi 92   Iasi-Neamt 87
```

Reuse whatever graph the host project already has rather than adding a second copy.

### Constants

| | value | meaning |
|---|---|---|
| β | 0.02 | how strongly the passer prefers short roads |
| γ | 0.01 | how fast completion probability falls; also the unit of `h` |
| τ | 1.5 | how strongly the passer prefers threatening receivers |

Implementation details, not tunables: initial value 1e-3, clamp 1e-30, convergence
tolerance 1e-12, iteration cap 100 000 as an error guard. These are fixed; they
should not be exposed as request parameters.

## The computation

`u` is the city being evaluated, `v` one of its neighbours, `w(u,v)` the road cost.
Everything is per goal: the result is a table `h[city]` for all 20 cities, computed
once per goal and cached.

**1.** `C(u,v) = exp(-γ · w(u,v))` — pass completion, depends only on the road.

**2.** `q(u,v) = exp(-β · w(u,v))` — cost attractiveness, depends only on the road.

**3.** Initialise: `xGT[goal] = 1.0`, every other city `0.001`. The small positive
start matters — step 4 raises the value to the power τ, and zeros leave the pass
choice undefined.

**4.** One iteration, for every city `u` except the goal:

```
for each neighbour v:   preference(u,v) = q(u,v) * max(xGT_current[v], 1e-30) ^ τ
S = sum of preference over the neighbours
for each neighbour v:   P(u,v) = preference(u,v) / S
xGT_next[u] = sum over neighbours of  P(u,v) * C(u,v) * xGT_current[v]
xGT_next[goal] = 1.0
```

Read the right-hand side from the *current* table for every city and write into a
*new* table. Updating in place makes the result depend on iteration order.

**5.** Repeat step 4 until the largest change in any city is below 1e-12. That takes
34 to 40 rounds for every goal. The test has to be a tolerance — for most goals the
doubles never become exactly equal, the last bit keeps flipping. The 100 000 cap is
an error condition, not the stopping rule.

**6.** Convert:

```
h[c] = floor( -ln(xGT[c]) / γ + 0.5 )     clamped at 0
h[goal] = 0
```

`floor(x + 0.5)`, not the language's `round()`: Python rounds half to even, Java
half up, and the two would disagree on an exact `.5`.

### What must not appear

No Dijkstra or other shortest-path computation feeding `h`. No rescaling of the
table after step 6. No coordinates — the heuristic uses only the road list.

## Verification

An implementation is correct when it reproduces these integers exactly. A single
±1 difference means a different rounding or summation order; investigate rather than
accept it.

**Goal = Bucharest** (xGT shown for reference)

| city | xGT | h | | city | xGT | h |
|---|---|---|---|---|---|---|
| Bucharest | 1.0000 | 0 | | Sibiu | 0.0489 | 302 |
| Urziceni | 0.4088 | 89 | | Iasi | 0.0352 | 335 |
| Giurgiu | 0.4066 | 90 | | Drobeta | 0.0215 | 384 |
| Pitesti | 0.3472 | 106 | | Neamt | 0.0147 | 422 |
| Hirsova | 0.1447 | 193 | | Arad | 0.0108 | 453 |
| Rimnicu Vilcea | 0.1203 | 212 | | Oradea | 0.0097 | 464 |
| Fagaras | 0.1117 | 219 | | Mehadia | 0.0094 | 467 |
| Vaslui | 0.0934 | 237 | | Zerind | 0.0049 | 531 |
| Craiova | 0.0772 | 256 | | Lugoj | 0.0044 | 542 |
| Eforie | 0.0612 | 279 | | Timisoara | 0.0029 | 584 |

**Goal = Sibiu**

```
Sibiu 0, Rimnicu Vilcea 84, Fagaras 99, Arad 151, Oradea 162, Pitesti 188,
Zerind 229, Craiova 245, Timisoara 272, Bucharest 301, Drobeta 373, Giurgiu 391,
Urziceni 391, Lugoj 393, Mehadia 454, Hirsova 495, Vaslui 539, Eforie 581,
Iasi 636, Neamt 723
```

**Goal = Neamt**: Iasi 92, Vaslui 185, Urziceni 337, Bucharest 430, Hirsova 441,
Giurgiu 520, Eforie 527, Pitesti 536, Rimnicu Vilcea 642, Fagaras 649, Craiova 686,
Sibiu 732, Drobeta 814, Arad 882, Oradea 894, Mehadia 897, Zerind 961, Lugoj 972,
Timisoara 1014.

**Goal = Arad**: Zerind 82, Timisoara 121, Sibiu 156, Oradea 159, Rimnicu Vilcea 240,
Lugoj 241, Fagaras 255, Mehadia 317, Pitesti 343, Drobeta 399, Craiova 407,
Bucharest 457, Giurgiu 547, Urziceni 547, Hirsova 651, Vaslui 694, Eforie 737,
Iasi 792, Neamt 879.

All 20 goals are in `exports/heuristic_table.json` if a full comparison is wanted in
a test.

### A\* behaviour

With `f = g + h`, expanding the smallest `f` and breaking ties by insertion order.
"Expanded" counts cities popped from the frontier, including start and goal.

| route | cost | expanded |
|---|---|---|
| Arad → Bucharest | 418 | 5 |
| Zerind → Bucharest | 493 | 6 |
| Zerind → Sibiu | 215 | 3 |
| Timisoara → Bucharest | 536 | 6 |
| Oradea → Bucharest | 429 | 5 |
| Neamt → Bucharest | 406 | 5 |
| Eforie → Sibiu | 547 | 7 |
| Arad → Neamt | 824 | 9 |
| Craiova → Iasi | 558 | 6 |
| Lugoj → Fagaras | 468 | 5 |
| Bucharest → Arad | 418 | 5 |

`Zerind → Bucharest` is the one to debug against: at Zerind, `f(Arad) = 75 + 453 =
528` must beat `f(Oradea) = 71 + 464 = 535`, so Arad is expanded second and Oradea
never.

Because the heuristic can overestimate, the safe A\* implementation re-opens a closed
node when a cheaper route to it is found. On this map it never changes the outcome
(380/380 either way), but it is the correct general behaviour.

## As built

Implemented in `ai-pathfinder-api` as `services/XgtHeuristic.java`: the same six
steps and the same constants, with every goal's table computed once at class load
and cached. `services/AStarSearch.java` consumes `XgtHeuristic.table(goal)`.

The Java ports kept in this repo under `tools/java/` are what
`python tools/crosscheck.py` compares against the Python, so the claim that the two
implementations agree is checkable rather than asserted.
