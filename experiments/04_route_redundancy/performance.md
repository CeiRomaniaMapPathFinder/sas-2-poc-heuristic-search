# Performance — Route redundancy

Full tables: `results.md`.

| variant | sanity pairs | mean Spearman | weighted inversions | A\* optimal | expanded |
|---|---|---|---|---|---|
| max-flow, capacity 1/w | 3/8 | 0.584 | 0.116 | 360/380 | 7.52 |
| baseline: straight-line | 6/8 | 0.848 | 0.083 | 380/380 | 6.81 |
| baseline: uniform-cost | 0/8 | – | – | 380/380 | 11.00 |

## It fails the first sanity pair

With capacity `1/w`, `R(Giurgiu) = 1/90 = 0.0111` — one road — while
`R(Pitesti) = 0.0146`, because three roads' bottleneck widths add up. So
`h(Giurgiu) = 322` against `h(Pitesti) = 244`, although Giurgiu is 90 from
Bucharest and Pitesti is 101.

Of the eight obvious comparisons it gets three right, two tie at the same value and
three are backwards. Spearman for goal Bucharest is −0.13: for that goal the method
is very slightly *anti*-correlated with the truth.

## Why, specifically

Max-flow measures how much can get through, not how far it has to go. Every city in
the western half of the map is limited by the same bottleneck — the two roads into
Bucharest from Pitesti and Fagaras — so Timisoara, 536 away, and Rimnicu Vilcea, 198
away, receive the same score. The eastern tail separates nicely (Vaslui, Iasi and
Neamt are behind narrower roads), which is exactly why the mean Spearman of 0.584
looks better than the method deserves: it is carried by the one part of the map
where corridor width happens to correlate with distance.

A\* still finds 360 of 380 optimal routes, but that is damning rather than
reassuring: with twelve cities sharing a value the heuristic barely orders
anything, so the search falls back toward uniform-cost behaviour — 7.52 cities
expanded against 4.94 for the method we kept.

## Would a different capacity help?

We did not try other capacity functions, and the reason is structural rather than
lazy: max-flow is invariant to path length. It depends only on the narrowest cut
between city and goal, so a longer route through equally wide roads scores exactly
the same as a short one. `1/w` is already the only cost-sensitive choice on offer,
and a constant capacity would remove road cost from the model altogether. No
capacity function recovers distance from a flow.

## Verdict

Drop. Interesting as graph theory, wrong instrument for the question. It stays in
the archive as the cleanest example of the failure mode the brief calls "systematic
nonsense" — not a few bad rankings, but a measurement that is orthogonal to what is
being asked.
