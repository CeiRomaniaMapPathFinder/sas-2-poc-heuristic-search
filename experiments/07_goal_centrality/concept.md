# Goal-seeded passing-network centrality

_Where the idea came from: the football brief's passing-network centrality section._

## The football idea

In passing-network analysis a player is central if the ball flows through them a lot. Here we ask a goal-directed version: **if every attack restarts at the goal city and the ball is then passed around at random (preferring easy passes), which cities does the ball visit most?** Cities the ball visits often are "central to the goal"; cities it rarely reaches are far away in the network sense.

This is personalized PageRank with the goal as the restart node.

## How h(n) is calculated

Parameters: `lambda` (pass preference for cheap roads), `damping d` (probability of continuing to pass instead of restarting at the goal).

1. Pass choice: `P(u->v) = exp(-lambda*w(u,v)) / sum_k exp(-lambda*w(u,k))`.
2. Stationary visit shares `pi` (iterate until stable, start uniform):

       pi_new(c) = (1 - d) * [c == goal]  +  d * sum over u of  P(u->c) * pi(u)

   i.e. with probability `1-d` the ball is placed back at the goal; otherwise it moves one pass.
3. Heuristic:

       raw(u) = ln( pi(goal) / pi(u) )        0 at the goal, larger the rarer the visits
       h(u)   = road-scaled raw, rounded to int

### Worked example (goal = Bucharest, lambda = 0.01, d = 0.85)

`pi(Bucharest) = 0.291`, `pi(Urziceni) = 0.114`, `pi(Pitesti) = 0.095`, `pi(Giurgiu) = 0.076`.

- `raw(Giurgiu) = ln(0.291/0.076) = 1.34`
- `raw(Pitesti) = ln(0.291/0.095) = 1.12`

Road-scaled (≈ 130 per unit) → `h(Giurgiu) = 174`, `h(Pitesti) = 146`. **Wrong order** (true 90 vs 101): the ball arriving at Giurgiu can only bounce back to Bucharest, whereas Pitesti is also fed from Rimnicu Vilcea and Craiova, so Pitesti collects more visits. Centrality measures *how connected* a city is, which is only loosely related to *how far* it is.

## Files

- `method.py` — `personalized_pagerank`, `build`.
- `experiment.py` — lambda/damping sweep; writes `results.md`.
- Java port: `../../tools/java/OtherHeuristics.java` (`GoalCentrality`).
