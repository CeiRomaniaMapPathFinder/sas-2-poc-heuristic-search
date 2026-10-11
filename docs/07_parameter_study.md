# What the three parameters actually do

xGT has three dials. The brief was explicit that parameters must not be arbitrary
decoration: each one has to mean something, and the value has to come from looking
at behaviour rather than from taste. This page is that look.

Shorthand used below: **deviation** is `mean |h − d*| / d*` over all 380 city/goal
values — how far the heuristic sits from true remaining cost. It is not a quality
score. A deviation near zero means the model has stopped being a model and started
being a shortest-path calculation.

## τ — how much the passer cares where the ball is going

`preference(u,v) = exp(−βw) · xGT(v)^τ`

At τ = 0 the modelled player chooses purely by road length. As τ grows the player
increasingly favours receivers that are themselves well placed.

β = 0.02, γ = 0.01 throughout:

| τ | sanity pairs | mean Spearman | deviation | A\* optimal | values equal to d\* |
|---|---|---|---|---|---|
| 0 | 7/8 | 0.986 | 0.87 | 318/380 | 3 |
| 0.5 | 8/8 | 0.994 | 0.33 | 333/380 | 3 |
| 1 | 8/8 | 0.997 | 0.15 | 379/380 | 4 |
| **1.5** | **8/8** | **0.999** | **0.07** | **380/380** | **4** |
| 2 | 8/8 | 0.999 | 0.03 | 380/380 | 6 |
| 3 | 8/8 | 0.999 | 0.01 | 380/380 | 34 |

τ is the only dial that changes the *structure* of the model rather than its scale,
and it is the one that fixes the dilution problem: at τ = 0 a city with three roads
spreads its pass probability over bad options and is ranked behind a two-road city
that is genuinely farther away. One step of τ removes that.

It is also the dial that can destroy the whole point. Every row from τ = 1.5 down to
τ = 3 guides A\* perfectly, but by τ = 3 the heuristic agrees with the shortest path
on 34 values and sits within 1 % everywhere. We stopped at the last setting that
guides perfectly while still visibly disagreeing.

## γ — how quickly a pass becomes risky, and the unit of h

`C(u,v) = exp(−γw)`, and `h = −ln(xGT)/γ`. γ appears twice, which is why it is the
awkward one: it sets both how much risk a long road carries and the scale the answer
comes out in.

β = 0.02, τ = 1.5:

| γ | sanity pairs | mean Spearman | deviation | A\* optimal | h(Timisoara), true 536 |
|---|---|---|---|---|---|
| 0.005 | 8/8 | 0.994 | 0.30 | 332/380 | 703 |
| **0.01** | **8/8** | **0.999** | **0.07** | **380/380** | **584** |
| 0.02 | 8/8 | 0.999 | 0.01 | 380/380 | 549 |
| 0.05 | 8/8 | 0.988 | 0.02 | 380/380 | 540 |

Small γ makes passes safe, so possessions survive long detours, threat values stay
high far from the goal and `h` inflates — at γ = 0.005 the far corner of the map is
30 % over and A\* gets greedy. Large γ squeezes `h` onto the road cost. γ = 0.01 was
kept for the same reason τ = 1.5 was: it is the loosest setting that still guides
perfectly.

## β — how strongly short roads are preferred

`q(u,v) = exp(−βw)`. The cost half of the pass choice.

γ = 0.01, τ = 1.5:

| β | sanity pairs | mean Spearman | deviation | A\* optimal |
|---|---|---|---|---|
| 0 (ignores road length) | 8/8 | 0.997 | 0.068 | 372/380 |
| 0.01 | 8/8 | 0.998 | 0.065 | 380/380 |
| **0.02** | **8/8** | **0.999** | **0.069** | **380/380** |
| 0.05 | 7/8 | 0.990 | 0.120 | 377/380 |

β is the least sensitive of the three — anything between 0.01 and 0.02 behaves the
same, and even β = 0 (a passer who ignores road length entirely and picks purely by
receiver value) only loses eight routes, because τ is already doing most of the
work. Pushing it to 0.05 makes the passer greedy for short roads and costs a sanity
pair. 0.02 was chosen while τ was still 1, where it lifted A\* from 358 to 379
routes; it was left there when τ moved to 1.5.

## Reading the three together

They are not independent. β and τ both shape the same pass choice, and γ both
creates risk and sets the unit. The honest summary of the search is:

- τ fixes a real modelling error (dilution) and is worth tuning carefully;
- γ sets the scale, and the scale is what decides whether A\* behaves or turns greedy;
- β is nearly free within a wide band.

There is a comfortable region rather than a knife edge — β in 0.01–0.02, γ in
0.01–0.02, τ in 1.5–2 all give 380/380 — and β 0.02 / γ 0.01 / τ 1.5 is the corner
of that region that stays furthest from the shortest path.

## What we did not do

We did not fit the parameters to the true distances. A least-squares fit of β, γ, τ
against `d*` would have produced better-looking numbers and a worse project: the
heuristic would then be a regression on the answer, which is the failure the brief
spends two sections warning about. Every value here was chosen by running a sweep
and reading the behaviour.
