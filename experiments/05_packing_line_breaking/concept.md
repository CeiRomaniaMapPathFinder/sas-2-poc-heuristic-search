# Packing / line breaking

_Where the idea came from: the football brief's packing / line-breaking section._

## The football idea

"Packing" counts how many defenders a pass takes out of the game. A team that has already broken the opponent's midfield line is in a better position than one that still has to. On the map, the "defensive lines" are the places where the road network is thin:

- a **bridge** = a road whose removal cuts the map in two (e.g. Bucharest–Urziceni, Iasi–Neamt);
- an **articulation point** = a city whose removal cuts the map in two (Bucharest, Urziceni, Vaslui, Iasi, Hirsova).

A city still has to break every line that separates it from the goal.

## How h(n) is calculated

1. Find all bridges and articulation points once (remove each road / each city and check whether the map stays connected — plain reachability, 20 cities).
2. For city `n` and goal `g`:

       lines(n) = number of bridges b such that removing b disconnects n from g
                + number of articulation points a (a != n, g) such that removing a disconnects n from g

3. Two versions:

       h_count(n)    = lines(n)
       h_weighted(n) = sum of w(bridge) over the separating bridges
                     + for each separating articulation point: the cheapest road into it from n's side

4. Road-scaled to int, `h(goal) = 0`.

### Example (goal = Bucharest)

Bridges: Bucharest–Giurgiu, Bucharest–Urziceni, Urziceni–Hirsova, Hirsova–Eforie, Urziceni–Vaslui, Vaslui–Iasi, Iasi–Neamt.
Articulation points: Bucharest, Hirsova, Iasi, Urziceni, Vaslui.

- Neamt must cross 4 bridges (Iasi–Neamt, Vaslui–Iasi, Urziceni–Vaslui, Bucharest–Urziceni) and 3 articulation points (Iasi, Vaslui, Urziceni) → `lines = 7`.
- Giurgiu: 1 bridge → `lines = 1`.
- **Every city in the west** (Arad, Sibiu, Pitesti, Craiova, …): the western half is 2-connected, so no single road or city separates it from Bucharest → `lines = 0`.

That last line is the whole story of this method: it can only see the eastern "corridors".

## Files

- `method.py` — `bridges`, `articulation_points`, `lines_between`, both builders.
- `experiment.py` — writes `results.md`.
- No Java port (the method is not usable standalone; see performance.md).
