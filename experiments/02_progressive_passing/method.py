"""
Method 2 -- Progressive Passing Score (PPS).

A pass u -> v is "progressive" if the receiver v is in a more threatening
position than the passer u.  Threat is measured with xGT (core/xgt.py),
NOT with the true shortest distance.

    Prog(u,v) = max(0, xGT(v) - xGT(u))          how much threat the pass adds
    PPS(u)    = sum_v P(u->v) * Prog(u,v)         expected progress of one pass from u

    h_inv(u)  = 1 / (PPS(u) + eps)                doc's transform
    h_log(u)  = -log(PPS(u) + eps)                gentler transform

Both are 'lower = better'.  Neither has a road-cost unit, so the int table is
road-scaled (core/scaling.py).  h(goal) is forced to 0 because the goal
has nothing left to progress to (PPS(goal) = 0 -> would be the WORST value).
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "core"))

from romania_graph import GRAPH, CITIES          # noqa: E402
from football_math import transition_probs       # noqa: E402
from xgt import xgt                  # noqa: E402
from scaling import to_int_road_scaled           # noqa: E402

EPS = 1e-9


def pps(goal, beta, gamma, tau=0.0):
    x = xgt(goal, beta, gamma, tau)
    P = transition_probs(beta)
    out = {}
    for u in CITIES:
        out[u] = sum(P[u][v] * max(0.0, x[v] - x[u]) for v in GRAPH[u])
    return out, x


def build(beta, gamma, transform="log", tau=0.0):
    def b(goal):
        s, _ = pps(goal, beta, gamma, tau)
        if transform == "inv":
            raw = {c: 1.0 / (v + EPS) for c, v in s.items()}
        else:
            raw = {c: -math.log(v + EPS) for c, v in s.items()}
        raw[goal] = 0.0
        # -log can be negative when PPS > 1 (never here, PPS <= 1) ; shift so min non-goal >= 0
        m = min(v for c, v in raw.items() if c != goal)
        if m < 0:
            raw = {c: (v - m if c != goal else 0.0) for c, v in raw.items()}
        return to_int_road_scaled(raw, goal)
    return b
