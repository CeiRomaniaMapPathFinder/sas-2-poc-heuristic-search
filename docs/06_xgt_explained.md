# xGT, explained

The heuristic we kept, end to end. `xgt_explained.pdf` in this folder is the same
material at twice the length, written for someone who has not seen Expected Threat
before; this page is the working reference.

Parameters: β = 0.02, γ = 0.01, τ = 1.5. Code: `core/xgt.py` (model),
`final/method.py` (the parameters).

## Where the idea comes from

Expected Threat (xT) is a football-analytics model that asks: if my team has the
ball in this zone, how likely is this possession to end in a goal? It exists because
distance to goal is a poor measure of danger — a ball on the wing 20 m out is worth
less than a ball in the centre 25 m out, because of what the player can *do next*.
The value of a zone is defined in terms of the value of the zones you can reach from
it, which makes the definition circular, and it is solved by iterating until the
numbers settle.

We keep three things from that: value comes from the future actions available, it is
propagated backwards from the goal, and it is computed by repeating one formula.

| football | Romania map |
|---|---|
| a zone of the pitch | a city |
| a pass | driving one road |
| transition probabilities from match data | transition probabilities computed from road cost |
| a shot that scores | arriving at the goal city |
| losing the ball | a pass that fails; the possession is worth 0 |
| xT(zone) | xGT(city) |

Two things have to be modelled rather than measured, because a road map has no match
data: which road the player takes, and whether the pass arrives.

## The symbols

`(u, v)` always means one road: `u` is where the ball is (the passer), `v` is a
neighbouring city (the receiver). "Sum over v" means once per road leaving `u`.

| symbol | meaning | example |
|---|---|---|
| `w(u,v)` | road cost | w(Pitesti, Bucharest) = 101 |
| `C(u,v) = exp(−γw)` | the pass arrives | C = 0.364 on that road |
| `q(u,v) = exp(−βw)` | how attractive the road is by cost alone | q = 0.133 |
| `P(u→v)` | probability the passer picks that road; the P's of one city sum to 1 | 0.948 |
| `xGT(u)` | chance a possession starting at u reaches the goal, 0…1 | xGT(Pitesti) = 0.347 |
| `h(u)` | the heuristic: xGT as an integer in road-cost units | 106 |

## The calculation

**1. Completion probability of every road** (once, independent of the goal)

```
C(u,v) = exp(-0.01 * w(u,v))      85 -> 0.427   101 -> 0.364   140 -> 0.247   211 -> 0.121
```

**2. Cost-attractiveness of every road** (once)

```
q(u,v) = exp(-0.02 * w(u,v))
```

**3. Which road the passer picks** (recomputed each iteration, because it uses xGT)

```
preference(u,v) = q(u,v) * xGT(v)^1.5
P(u->v)         = preference(u,v) / sum of preference over all roads leaving u
```

The passer likes a road when it is short *and* leads somewhere threatening. τ = 1.5
sets how much the second half counts.

**4. The value of a city**

```
xGT(goal) = 1
xGT(u)    = sum over roads (u,v) of   P(u->v) * C(u,v) * xGT(v)
```

Per road: chance the passer picks it, times chance the pass arrives, times the value
of where it arrives.

**5. Iterate until the table stops moving.** Start every city at 0.001 and the goal
at 1. Apply steps 3–4 to all 20 cities into a *new* table (synchronous update), then
compare: stop when the largest change in any city is below 1e-12. That takes 34–40
rounds for every goal. The 100 000-iteration cap in the code is an error guard, not
the stopping rule — and the test has to be a tolerance, not exact equality, because
for most goals the last bit of the double keeps flipping forever.

Goal = Bucharest, watching it settle:

| round | Giurgiu | Pitesti | Rimnicu Vilcea | Craiova | Sibiu | Arad |
|---|---|---|---|---|---|---|
| 1 | 0.4066 | 0.3642 | 0.0004 | 0.0003 | 0.0004 | 0.0004 |
| 2 | 0.4066 | 0.3642 | 0.1381 | 0.0916 | 0.0450 | 0.0002 |
| 3 | 0.4066 | 0.3438 | 0.1266 | 0.0817 | 0.0559 | 0.0111 |
| 5 | 0.4066 | 0.3477 | 0.1196 | 0.0768 | 0.0477 | 0.0113 |
| 8 | 0.4066 | 0.3472 | 0.1202 | 0.0772 | 0.0489 | 0.0110 |
| settled | 0.4066 | 0.3472 | 0.1203 | 0.0772 | 0.0489 | 0.0108 |

Giurgiu is finished after one round — its only road goes straight to the goal.
Pitesti needs several, because its value depends on Rimnicu Vilcea and Craiova,
whose values depend on Sibiu and Drobeta, and so on outwards.

**6. Convert to an integer**

```
h(u) = floor( -ln(xGT(u)) / 0.01 + 0.5 )        h(goal) = 0
```

Along one chain of passes xGT is a product of `exp(−γw)` terms, so `−ln(xGT)` is
`γ × (sum of road costs)`; dividing by γ puts the number back in road-cost units, the
same units as `g(n)`. `floor(x + 0.5)` rather than the language's `round()`, because
Python rounds half to even and Java does not.

## Worked example, goal = Bucharest

Pitesti has three roads. Receiver values come from the settled table above.

| receiver | w | q | xGT(v) | xGT(v)^1.5 | preference | P | C | P·C·xGT(v) |
|---|---|---|---|---|---|---|---|---|
| Bucharest | 101 | 0.1327 | 1.0000 | 1.0000 | 0.13266 | 0.9475 | 0.3642 | 0.3451 |
| Rimnicu Vilcea | 97 | 0.1437 | 0.1203 | 0.0417 | 0.00600 | 0.0428 | 0.3791 | 0.0020 |
| Craiova | 138 | 0.0633 | 0.0772 | 0.0215 | 0.00136 | 0.0097 | 0.2516 | 0.0002 |

Preferences sum to 0.14001, which is what turns the preference column into the P
column. Then

```
xGT(Pitesti) = 0.3451 + 0.0020 + 0.0002 = 0.3472      h = floor(105.8 + 0.5) = 106
```

Giurgiu, one road: `xGT = 1 × exp(−0.9) × 1 = 0.4066`, `h = 90`.
Urziceni, three roads: contributions 0.4065 + 0.0022 + 0.0002 = 0.4088, `h = 89`.

True remaining costs are 101, 90 and 85. Giurgiu's heuristic is exactly its road
cost — one lane, no hesitation. Pitesti pays five extra because the modelled passer
sometimes takes a side road. That surplus is the football content of the number.

## The fork: Zerind → Bucharest

The case the brief cares about, where the cheaper first road is not the cheaper
route.

```
Zerind -> Arad   (75) -> Sibiu (140) = 215 to Sibiu     cheaper route, dearer first road
Zerind -> Oradea (71) -> Sibiu (151) = 222 to Sibiu     cheaper first road, dearer route
best overall: Zerind -> Arad -> Sibiu -> Rimnicu Vilcea -> Pitesti -> Bucharest = 493
```

Both Arad and Oradea get nearly all their value from their road to Sibiu
(xGT(Sibiu) = 0.0489), so the difference comes down to one number: the completion
probability of that road, 0.2466 for Arad's 140 against 0.2209 for Oradea's 151.
Result: `h(Arad) = 453`, `h(Oradea) = 464`. The model never sees the route costs 418
and 429, but it reproduces their difference of 11 almost exactly.

What A\* then does:

| step | expands | frontier after, by f |
|---|---|---|
| 1 | Zerind (0 + 531) | Arad 75+453=**528**, Oradea 71+464=535 |
| 2 | Arad (528) | Sibiu 215+302=**517**, Oradea 535, Timisoara 777 |
| 3 | Sibiu (517) | Rimnicu Vilcea 295+212=**507**, Fagaras 533, Oradea 535, … |
| 4 | Rimnicu Vilcea (507) | Pitesti 392+106=**498**, Fagaras 533, Oradea 535, … |
| 5 | Pitesti (498) | Bucharest 493+0=**493**, … |
| 6 | Bucharest — done | |

Cost 493, six cities expanded, nothing expanded that is not on the final route.
Oradea's 4-point cheaper road loses to the 11-point heuristic gap, and it sits on
the frontier at 535 forever. With the cost-only passer (τ = 0) the same fork gives
`h(Arad) = 770 > h(Oradea) = 753`, A\* goes through Oradea and finishes at 532.

## The table for goal = Bucharest

| city | true remaining | xGT | h | h / true | roads |
|---|---|---|---|---|---|
| Bucharest | 0 | 1.0000 | 0 | – | 4 |
| Urziceni | 85 | 0.4088 | 89 | 1.05 | 3 |
| Giurgiu | 90 | 0.4066 | 90 | 1.00 | 1 |
| Pitesti | 101 | 0.3472 | 106 | 1.05 | 3 |
| Hirsova | 183 | 0.1447 | 193 | 1.05 | 2 |
| Rimnicu Vilcea | 198 | 0.1203 | 212 | 1.07 | 3 |
| Fagaras | 211 | 0.1117 | 219 | 1.04 | 2 |
| Vaslui | 227 | 0.0934 | 237 | 1.04 | 2 |
| Craiova | 239 | 0.0772 | 256 | 1.07 | 3 |
| Eforie | 269 | 0.0612 | 279 | 1.04 | 1 |
| Sibiu | 278 | 0.0489 | 302 | 1.09 | 4 |
| Iasi | 319 | 0.0352 | 335 | 1.05 | 2 |
| Drobeta | 359 | 0.0215 | 384 | 1.07 | 2 |
| Neamt | 406 | 0.0147 | 422 | 1.04 | 1 |
| Arad | 418 | 0.0108 | 453 | 1.08 | 3 |
| Oradea | 429 | 0.0097 | 464 | 1.08 | 2 |
| Mehadia | 434 | 0.0094 | 467 | 1.08 | 2 |
| Zerind | 493 | 0.0049 | 531 | 1.08 | 2 |
| Lugoj | 504 | 0.0044 | 542 | 1.08 | 2 |
| Timisoara | 536 | 0.0029 | 584 | 1.09 | 2 |

Same order as the true order, every hop ring given distinct values, and `h` sits
0–9 % high with the surplus concentrated on cities that have several plausible roads.
The true-cost column is here to judge the result; it is not an input.
