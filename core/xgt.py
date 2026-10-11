"""
Expected Goal Threat (xGT).

The value a city has as a possession state: the probability that a possession
starting there eventually reaches the goal city.

  xGT(goal) = 1
  xGT(u)    = sum over neighbours v of  P(u->v) * C(u,v) * xGT(v)

  C(u,v) = exp(-gamma * w)                         pass completed, long road = risky
  P(u->v) ~ exp(-beta * w) * xGT(v)^tau            which pass the player picks

tau is the only structural dial:
  tau = 0    the passer looks at road cost alone (the model as first written)
  tau > 0    the passer also prefers receivers that are themselves threatening
  tau large  the passer is near-perfect and xGT collapses onto shortest path

Conversion to an A* heuristic (lower = better), in road-cost units:

  h(u) = -ln(xGT(u)) / gamma

Along one chain of passes xGT is a product of exp(-gamma*w) terms, so
-ln(xGT) = gamma * (sum of road costs); dividing by gamma puts h back into the
same units as g(n).  No shortest-path distance enters anywhere.

xgt_no_completion() keeps the first formulation (C = 1) that turned out to be
degenerate; it is here because the dead end is part of the record, not because
anything uses it.
"""
import math

from football_math import (completion_probs, fixed_point, pass_preference,
                           to_int_table, transition_probs)
from romania_graph import CITIES, GRAPH

# Every city starts at a small positive value: with tau > 0 the pass choice
# raises xGT(v) to a power, and all-zero values would leave it undefined.
INIT = 1e-3
FLOOR = 1e-30


def xgt(goal, beta, gamma, tau=0.0):
    """Converged xGT values in 0..1, goal = 1."""
    q = pass_preference(beta)
    C = completion_probs(gamma)

    def update(x):
        nx = {goal: 1.0}
        for u in CITIES:
            if u == goal:
                continue
            pref = {v: q[u][v] * (max(x[v], FLOOR) ** tau) for v in GRAPH[u]}
            s = sum(pref.values())
            nx[u] = sum((pref[v] / s) * C[u][v] * x[v] for v in GRAPH[u])
        return nx

    init = {c: INIT for c in CITIES}
    init[goal] = 1.0
    values, _ = fixed_point(update, init, tol=1e-12)
    return values


def xgt_no_completion(goal, beta, horizon=None):
    """
    The first formulation: no completion probability, so no way to lose the ball.
    On a connected map every possession eventually arrives and the fixed point is
    1 everywhere.  horizon=k stops after k passes, which is the only way this
    version says anything.
    """
    P = transition_probs(beta)

    def update(x):
        nx = {goal: 1.0}
        for u in CITIES:
            if u != goal:
                nx[u] = sum(P[u][v] * x[v] for v in GRAPH[u])
        return nx

    init = {c: 0.0 for c in CITIES}
    init[goal] = 1.0
    if horizon is None:
        values, _ = fixed_point(update, init)
        return values
    x = init
    for _ in range(horizon):
        x = update(x)
    return x


def h_from_xgt(values, goal, gamma):
    """(integer table, raw table) with raw = -ln(xGT)/gamma in road-cost units."""
    raw = {c: (-math.log(v) / gamma if v > 0 else float("inf")) for c, v in values.items()}
    raw[goal] = 0.0
    return to_int_table(raw, goal), raw


def build(beta, gamma, tau=0.0):
    """Heuristic builder: goal -> (integer table, raw table)."""
    return lambda goal: h_from_xgt(xgt(goal, beta, gamma, tau), goal, gamma)
