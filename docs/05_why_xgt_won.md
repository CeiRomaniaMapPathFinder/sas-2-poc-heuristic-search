# Why we kept xGT

Three methods finished level on the measurements: xGT with a value-aware passer,
press resistance, and pitch control. All three pass 8/8 sanity pairs, all three let
A\* find the optimal route on all 380 pairs, and all three expand about five cities
where uniform-cost search expands eleven.

| | xGT | pitch control | press resistance |
|---|---|---|---|
| sanity pairs | 8/8 | 8/8 | 8/8 |
| mean Spearman | 0.999 | 0.997 | 0.993 |
| A\* optimal | 380/380 | 380/380 | 380/380 |
| expanded | 4.94 | 4.95 | 5.36 |

So the choice was not made on the numbers. It was made on what the brief actually
asked for — a heuristic whose *mechanism* comes from another domain — and the
tie-break was this question: if you delete the football story, is there still a
distinctive model underneath, or just a familiar formula with a new name?

## Pitch control, and why it did not win

Influence starts at 1 in the goal city and spreads: `I(u) = α · Σ exp(−λw) · I(v)`.
Unroll that and `I(u)` is a sum over every walk from `u` to the goal of
`α^(number of hops) × exp(−λ × total road cost)`. Taking `−ln(I)/λ` turns it into a
soft minimum over all walks of "road cost plus about 11 units per hop".

That is a smoothed shortest path. It is a good one, and it is legitimately not the
same as Dijkstra — but it has one mechanism (influence fades), and both of its
parameters are decay constants rather than decisions a player makes. The brief
itself flags this family as resembling diffusion and random-walk models and warns
about the overlap with electrical-network heuristics. It stays in the repo as the
runner-up, fully implemented, and if the grading had weighted search performance
above the analogy it would have been the right pick.

## Press resistance, and why it did not win

Press resistance is genuinely good, and its one-line difference from xGT — add over
the outlets instead of averaging over them — is the single most instructive result
in this project. But it is not an independent model: `PR(u) = Σ C(u,v) · xGT(v)`
needs xGT to exist first. It is a one-hop aggregate layered on top of the method it
was competing with. As a component it earned its place in the combined model; as
*the* answer it would have meant shipping a derivative of xGT and calling it
something else.

## What xGT has that the other two do not

Two separate football mechanisms, each of which changes the mathematics:

- a **pass-selection policy** — which road the modelled player takes, and the fact
  that the player looks at the receiver's position and not only at the road;
- a **completion probability** — the ball can be lost, and longer roads lose it more
  often, which is what stops every city from scoring 1.

Remove the football framing and there is still an absorbing random walk with a
value-dependent transition policy, solved by fixed-point iteration. That survives
the deletion test.

It also fails in ways that can be explained in one sentence. A striker with a single
lane never hesitates, so Giurgiu's heuristic equals its road cost exactly. A
midfielder with three lanes sometimes picks the wrong one, so Pitesti's sits five
above. That is the kind of error you can defend in a viva; "the diffusion constant
is 0.8" is not.

And it is the brief's own preferred candidate, which matters for a project that was
handed a brief.

## How τ got to 1.5

The parameter τ controls how strongly the modelled passer prefers receivers that
are already threatening. It is the only structural dial in the model, and the
journey through it is most of the story.

**τ = 0** — the passer looks at road cost alone. This is the model as first written,
and it fails: for goal Sibiu it ranks Arad behind Oradea (`h` 770 vs 753) although
Arad is genuinely closer (418 vs 429). The cause is dilution — Arad has three roads,
so its pass probability is spread across Zerind and Timisoara as well, while Oradea
has only two. The same dilution inflates `h` to roughly 1.8× true cost, A\* turns
greedy, and only 287 of 380 routes come out optimal.

The brief anticipated exactly this failure and warned against fixing it with BFS
rings. We did not want a patch bolted on from outside the model, so the fix had to
be a football statement: *a real player passes to a team-mate in a good position,
not just to the nearest one.*

**τ = 1** — Arad/Oradea flips the right way (159 vs 166), all eight sanity pairs
pass, and A\* reaches 94.2 %. Raising β to 0.02 at the same time takes it to 99.7 %
without changing any ranking.

**The one route that was left.** `Zerind → Craiova` came out at 448 instead of 441.
At Zerind the heuristic ranks Arad ahead of Oradea correctly, but by only 2 points
(452 vs 454) where the true gap is 11. Oradea's road is 4 cheaper, so `f` puts
Oradea first, Oradea reaches Sibiu, and Arad is never expanded. A ranking that is
right but too flat.

**τ = 1.5** — the passer concentrates a little harder, the gap widens, and that last
route comes out optimal. 380/380.

**τ = 2 and beyond** — still 380/380, and no longer interesting. At τ = 3 the
heuristic for Arad and Oradea toward Sibiu is 140 and 151: the exact road costs. The
model has become Dijkstra with extra steps, which is the failure mode the brief
explicitly rejects.

## What τ = 1.5 costs

Pushing τ up buys A\* performance by making the model a better passer, and a better
passer means a heuristic closer to the true shortest path:

All rows at β = 0.02, γ = 0.01, so only τ moves:

| τ | mean \|h − d\*\| / d\* | A\* optimal | values equal to d\* |
|---|---|---|---|
| 0 | 0.87 | 318/380 | 3 |
| 0.5 | 0.33 | 333/380 | 3 |
| 1 | 0.15 | 379/380 | 4 |
| **1.5** | **0.07** | **380/380** | **4** |
| 2 | 0.03 | 380/380 | 6 |
| 3 | 0.01 | 380/380 | 34 |

At τ = 1.5 the heuristic still differs from true remaining cost on 376 of 380
city/goal values, and the differences are structured rather than noisy — they grow
with the number of multi-road cities on the route. At τ = 3 that is gone. We stopped
at the last value that both guides perfectly and still visibly disagrees with the
shortest path. `08_is_it_just_shortest_path.md` works through how much of the number
is model and how much is distance.

β was set to 0.02 for the same reason τ was raised: it improved A\* without moving
any ranking. γ was left at 0.01 because it sets the unit of `h`, and larger values
pull the whole table toward road cost.

## What would have changed the decision

- If pitch control had beaten xGT on expansions by a clear margin rather than 0.01
  of a city, performance would have outweighed the analogy.
- If the value-aware fix had needed information from outside the football model —
  hop counts, coordinates, true distances — we would have dropped xGT and taken
  press resistance, which passes 8/8 without any such help.
- If τ had needed to go to 2 or 3 to make A\* work, the method would have been a
  renamed shortest path and none of the three finalists would have been a good
  answer to the brief.
