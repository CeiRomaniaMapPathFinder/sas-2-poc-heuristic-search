# Romania A\* — searching for a heuristic worth keeping

This repository is the record of how we picked the heuristic function used by the
Romania pathfinder. We were told to design a *creative* `h(n)` — not the usual
straight-line distance — so we borrowed ideas from football analytics, built ten
of them, measured all ten against the same tests, and kept one.

The one we kept is **xGT (Expected Goal Threat)**: a city is scored by how likely
a football-style possession starting there is to reach the goal city, and that
probability is converted into an integer in road-cost units.

```
h(city) = floor( -ln( xGT(city) ) / 0.01 + 0.5 )     h(goal) = 0
```

Nothing here uses coordinates or a shortest-path computation. The value comes out
of the road network and a passing model, and only afterwards is it compared
against true remaining cost to see whether it makes sense.

## Headline numbers

Every heuristic was run over all 380 ordered (start, goal) pairs of the 20-city map.

| heuristic | sanity pairs | rank agreement with true cost | A\* found the optimal route | cities expanded |
|---|---|---|---|---|
| xGT (kept) | 8/8 | 0.999 | 380/380 | 4.94 |
| uniform-cost search (h = 0) | 0/8 | – | 380/380 | 11.00 |
| straight-line distance | 6/8 | 0.848 | 380/380 | 6.81 |
| ring / minimum-edge (our earlier attempt) | 4/8 | 0.975 | 380/380 | 5.60 |

Fewer expansions is the point: the heuristic has to earn its place by cutting
search work without breaking the answer.

## What is in here

| path | what it holds |
|---|---|
| `docs/` | the write-up: the problem, every idea we considered, how we tested, the scoreboard, why xGT won, and the honest caveats |
| `experiments/` | ten numbered folders, one per idea, each with its concept, code, generated results and a verdict |
| `core/` | the shared harness: the map, Dijkstra and A\*, the metrics, the baselines, and the xGT model itself |
| `final/` | the heuristic we kept, its evaluation, and the exported tables handed to the backend |
| `tools/` | run everything, cross-check Python against Java, rebuild the explainer PDF |

Start with [`docs/04_results_scoreboard.md`](docs/04_results_scoreboard.md) if you
want the summary, or [`docs/05_why_xgt_won.md`](docs/05_why_xgt_won.md) if you want
the argument. [`docs/xgt_explained.pdf`](docs/xgt_explained.pdf) is the long-form
version with worked examples, written for someone who has never seen xT before.

## The ten ideas

In the order we tried them. Full table with numbers in `docs/04_results_scoreboard.md`.

1. [Expected Goal Threat](experiments/01_expected_goal_threat) — possession value propagated back from the goal. **Kept.**
2. [Progressive passing](experiments/02_progressive_passing) — reward passes that gain threat. Works, but inherits xGT's blind spot.
3. [Press resistance](experiments/03_press_resistance) — count the usable outlets. Strong; the closest runner-up after pitch control.
4. [Route redundancy](experiments/04_route_redundancy) — max-flow from city to goal. Fails: capacity says nothing about distance.
5. [Packing / line breaking](experiments/05_packing_line_breaking) — bridges and cut vertices as defensive lines. Blind over half the map.
6. [Pitch control](experiments/06_pitch_control) — influence spreading out from the goal. Best raw numbers; thinner story.
7. [Goal-seeded centrality](experiments/07_goal_centrality) — PageRank restarted at the goal. Middling; punishes dead ends unfairly.
8. [Combined model](experiments/08_combined_model) — threat × support × progression. The extras only inflate h.
9. [Expected time to goal](experiments/09_expected_time_to_goal) — our own: mean time for a possession to arrive. Ranks well, guides badly.
10. [Turnover risk](experiments/10_turnover_risk) — our own: cost paid before scoring or losing the ball. Same story, slightly better.

Two of these are ours rather than the brief's, and both lost. They are kept here
because a shortlist with nothing rejected in it is not a shortlist.

## Running it

Python 3.10+, standard library only — no pip install, no requirements file. Java
is needed only for the cross-check (compiles at `--release 17`).

```bash
python core/selftest.py        # map and search sanity checks
python tools/run_all.py        # self-test, all ten experiments, the final model, Java cross-check
python tools/make_pdf.py       # rebuild docs/xgt_explained.pdf (needs reportlab)

cd experiments/06_pitch_control && python experiment.py    # or any single experiment
```

Each `experiment.py` rewrites its own `results.md`, so the tables in this repo can
always be regenerated from scratch. `docs/` is written by hand; `results.md` files
are not.

## Where it ended up

The chosen heuristic is implemented in the backend as
`services/XgtHeuristic.java` in `ai-pathfinder-api`, with the same constants
(β 0.02, γ 0.01, τ 1.5, tolerance 1e-12, `floor(x + 0.5)` rounding) and the same
integer output. `tools/crosscheck.py` is what makes that claim checkable: it runs
the Java ports in `tools/java/` and compares every city of every goal against the
Python implementation here.

`final/implementation_spec.md` is the document that was handed over for that work.

## Two things we are not claiming

The heuristic is **not admissible** — on this map it sits 0–9 % above the true
remaining cost. A\* still returned the optimal route for all 380 pairs, but that is
an observation about this graph, not a guarantee.

And it is **not independent of distance**. Any heuristic that ranks cities by "how
well placed are you to reach the goal" will correlate with true remaining cost;
that is the job. What matters is that the number is produced by the passing model
rather than copied from a shortest-path computation, and that the model can be
pushed until it stops agreeing — see `docs/08_is_it_just_shortest_path.md`.
