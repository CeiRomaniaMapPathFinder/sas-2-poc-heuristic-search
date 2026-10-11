"""
Method 6 -- Passing-Network Centrality toward the goal (personalized PageRank).

Imagine the ball is always restarted at the goal city and then passed around
the network at random, preferring cheap roads.  Cities the ball visits often
are central "to the goal".

  P(u->v) = exp(-lambda*w) / sum_k exp(-lambda*w_k)     pass choice, cheap roads preferred
  pi      = (1 - d) * e_goal  +  d * P^T pi              d = damping (probability to keep passing)

pi(u) = long-run share of time the ball is at u.  High = central to the goal.

  raw(u) = ln( pi(goal) / pi(u) )      0 at the goal, larger for cities the ball rarely visits
  h(u)   = road-scaled raw, rounded to int

Different from xGT: xGT asks "starting at u, do I reach the goal before losing
the ball?"; PageRank asks "starting at the goal, how often do I pass through u?".
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "core"))

from romania_graph import GRAPH, CITIES                   # noqa: E402
from football_math import transition_probs, fixed_point   # noqa: E402
from scaling import to_int_road_scaled                    # noqa: E402


def personalized_pagerank(goal, lam, damping):
    P = transition_probs(lam)

    def update(pi):
        npi = {c: (1.0 - damping) if c == goal else 0.0 for c in CITIES}
        for u in CITIES:
            for v in GRAPH[u]:
                npi[v] += damping * P[u][v] * pi[u]
        return npi

    init = {c: 1.0 / len(CITIES) for c in CITIES}
    pi, _ = fixed_point(update, init, tol=1e-14)
    return pi


def build(lam, damping):
    def b(goal):
        pi = personalized_pagerank(goal, lam, damping)
        raw = {c: math.log(pi[goal] / pi[c]) for c in CITIES}   # 0 at goal, > 0 elsewhere
        return to_int_road_scaled(raw, goal)
    return b
