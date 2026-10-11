# Every idea we considered

Three groups: ideas thrown out before any code, the ten we built, and the three
baselines we kept around to compare against.

## Thrown out before writing code

**The earlier ring / "financial" method.** Our first attempt, before this repo
existed: BFS layers from the goal, then add up the cheapest edge crossing each
layer. It is valid and it is even a lower bound, but every city in the same ring
gets the same value, so it cannot tell apart a city with three good roads from one
stuck at the end of a corridor. It survives here as a baseline (`ring min-edge`)
precisely because it is the thing to beat. It is also the reason we went looking
for a different kind of model instead of patching this one.

**Renaming the road cost.** Call a road a "transaction fee", a "pass difficulty", a
"fuel burn" — if `h` still comes out as the road cost, nothing happened.

**Rescaling the road cost.** `1.07 × cost`, `sqrt(cost)`, `cost + tax`. Same
problem with extra steps.

**Inventing city attributes.** Giving Sibiu a "midfield rating" would have made the
model say whatever we wanted it to say. Everything had to be derived from the graph.

**A pure hop-count or ring variant with a football name.** Same mathematics as the
method we were trying to get away from.

## Built and measured

Numbers for all of these are in `04_results_scoreboard.md`; each has its own folder
with the concept, the code and a verdict.

| # | idea | the question it asks | outcome |
|---|---|---|---|
| 01 | Expected Goal Threat | if a possession starts here, how likely is it to reach the goal? | kept |
| 02 | Progressive passing | how much threat does the next pass typically gain? | works, but inherits 01's blind spot |
| 03 | Press resistance | how many usable outlets does this city have? | strong, nearly chosen |
| 04 | Route redundancy | how much independent channel reaches the goal from here? | rejected |
| 05 | Packing / line breaking | how many structural barriers still separate me from the goal? | rejected |
| 06 | Pitch control | how strongly does the goal's influence reach this city? | best numbers, not chosen |
| 07 | Goal-seeded centrality | if play restarts at the goal forever, how often is the ball here? | middling |
| 08 | Combined model | threat, support and progression multiplied together | no better than its first ingredient |
| 09 | Expected time to goal (ours) | how long until a possession starting here arrives? | ranks well, guides badly |
| 10 | Turnover risk (ours) | how much cost is paid before either scoring or losing the ball? | same, slightly better |

### Why the order

01 to 08 follow the football brief, which builds up in that order: value
propagation first, then the refinements, then the combination. 04 is the brief's
route-redundancy idea, which we pulled out of the press-resistance folder into its
own experiment because it is structurally different and because it fails in an
instructive way.

09 and 10 are ours. After seeing that xGT needed a `-log` to become a cost, we
wanted to know whether a model that is *already* in road-cost units would behave
better. Both are expectation-of-cost models: one counts time, one counts time plus
turnover penalties. Neither beat xGT, and `09_expected_time_to_goal` explains the
reason, which was the most useful negative result in the set.

## Ideas we wrote down and did not get to

Kept here so the shortlist is honest about its edges.

- **Shot-quality weighting.** In real xT a possession can end in a shot from
  distance. There is no analogue on a road map unless we invent one, and inventing
  one breaks our own rule about made-up attributes.
- **Off-ball runs / multi-step lookahead in the pass choice.** The passer here looks
  one pass ahead (at the receiver's value). Looking two ahead is a bigger model with
  no obvious football payoff on a 20-node graph.
- **Learning the parameters.** β, γ and τ could have been fitted against true
  distances. We deliberately did not: fitting to `d*` would make the heuristic a
  regression on the answer, which is the thing the brief warns against. They were
  chosen by sweeping and reading the behaviour instead.
- **A different map.** Everything here is tuned and tested on the 20-city Romania
  graph. Whether τ = 1.5 is right for another graph is untested, and we say so.

## Baselines

Not candidates — yardsticks. All three are in `core/baselines.py`.

- **Uniform-cost search** (`h = 0`). The floor for search effort: optimal by
  definition, 11.0 cities expanded on average. Any heuristic that cannot beat that
  number is doing nothing.
- **Straight-line distance** from the standard map coordinates. The textbook
  answer, and the thing we were told not to submit. Useful because it shows that
  being admissible does not make a heuristic *informative*: it expands 6.81 cities
  and gets only 6 of the 8 sanity pairs right, because geography and roads disagree.
- **Ring / minimum-edge**, our earlier attempt described above.
