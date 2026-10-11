"""
Method 5 -- Pitch Control / Goal Influence.

The goal radiates "control" into the network.  Every road passes on a share of
the influence it receives; cheap roads pass on more.

  a(u,v) = exp(-lambda * w(u,v))               how much influence a road transmits
  I(goal) = 1                                  the goal is the source
  I(u)    = alpha * sum_v a(u,v) * I(v)        for u != goal   (iterate to a fixed point)

alpha < 1 is an attenuation ("influence fades with every pass") that is needed
for the iteration to converge: without it the sum over roads can grow, because
a city with many roads collects influence from all of them.  Unlike xGT there
is NO normalisation per city, so hubs with many cheap roads collect more
influence than a city with one road -- that is the pitch-control flavour.

  h(u) = -log(I(u)) / lambda        (road-like unit, same trick as xGT)
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "core"))

from romania_graph import GRAPH, CITIES                  # noqa: E402
from football_math import fixed_point, to_int_table      # noqa: E402


def influence(goal, lam, alpha):
    a = {u: {v: math.exp(-lam * w) for v, w in GRAPH[u].items()} for u in CITIES}

    def update(x):
        nx = {goal: 1.0}
        for u in CITIES:
            if u != goal:
                nx[u] = alpha * sum(a[u][v] * x[v] for v in GRAPH[u])
        return nx

    init = {c: 0.0 for c in CITIES}
    init[goal] = 1.0
    x, it = fixed_point(update, init, tol=1e-12, max_iter=20000)
    if it >= 20000 or any(v > 1e6 for v in x.values()):
        raise ValueError(f"influence diverged for lambda={lam} alpha={alpha}")
    return x


def build(lam, alpha):
    def b(goal):
        x = influence(goal, lam, alpha)
        raw = {c: (-math.log(v) / lam if v > 0 else float("inf")) for c, v in x.items()}
        raw[goal] = 0.0
        return to_int_table(raw, goal), raw
    return b
