"""
Method 7 -- Combined football model (doc sections 18 and 19).

Three tactical ingredients, all derived from the graph:

  xGT(n)  -- expected goal threat: chance a possession starting at n scores      (core/xgt.py)
  PR(n)   -- press resistance: sum of pass quality over all outlets              (press_resistance/method.py)
  PPS(n)  -- progressive passing: expected threat gained by the next pass        (progressive_passing/method.py)

Section 18 (multiplicative):
  AttackValue(n) = xGT(n) * (1 + alpha * PR_norm(n)) / (1 + alpha)
                          * (1 + delta * PPS_norm(n)) / (1 + delta)
  h(n) = -log(AttackValue(n)) / gamma            road units, like xGT

The division by (1 + alpha) and (1 + delta) keeps every multiplier <= 1, so
AttackValue <= xGT <= 1 and the goal (value 1) stays the unique best state.
Read it as: "a city keeps its full threat only if it also has the best
support and the best progression; otherwise it is marked down".

Section 19 (weighted sum):
  Score(n) = a * xGT_norm(n) + b * PR_norm(n) + c * PPS_norm(n)
  h(n) = 1 - Score(n)                            then road-scaled

*_norm = divided by the largest value among non-goal cities, so each ingredient
is in 0..1 before mixing.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "core"))

from romania_graph import GRAPH, CITIES                        # noqa: E402
from football_math import transition_probs, completion_probs, to_int_table  # noqa: E402
from xgt import xgt                                # noqa: E402
from scaling import to_int_road_scaled                         # noqa: E402


def ingredients(goal, beta, gamma, tau):
    """Returns (xGT, PR_sum, PPS) tables computed from ONE xGT run."""
    x = xgt(goal, beta, gamma, tau)
    P = transition_probs(beta)
    C = completion_probs(gamma)
    pr = {u: sum(C[u][v] * x[v] for v in GRAPH[u]) for u in CITIES}
    pps = {u: sum(P[u][v] * max(0.0, x[v] - x[u]) for v in GRAPH[u]) for u in CITIES}
    return x, pr, pps


def _norm(t, goal):
    m = max(v for c, v in t.items() if c != goal)
    return {c: (v / m if m > 0 else 0.0) for c, v in t.items()}


def build_multiplicative(beta, gamma, tau, alpha, delta):
    def b(goal):
        x, pr, pps = ingredients(goal, beta, gamma, tau)
        prn, ppsn = _norm(pr, goal), _norm(pps, goal)
        av = {c: x[c] * (1 + alpha * prn[c]) / (1 + alpha) * (1 + delta * ppsn[c]) / (1 + delta) for c in CITIES}
        raw = {c: -math.log(av[c]) / gamma for c in CITIES}
        raw[goal] = 0.0
        return to_int_table(raw, goal), raw
    return b


def build_weighted_sum(beta, gamma, tau, a, bw, c):
    def b(goal):
        x, pr, pps = ingredients(goal, beta, gamma, tau)
        xn, prn, ppsn = _norm(x, goal), _norm(pr, goal), _norm(pps, goal)
        score = {n: a * xn[n] + bw * prn[n] + c * ppsn[n] for n in CITIES}
        raw = {n: (1.0 - score[n]) for n in CITIES}
        raw[goal] = 0.0
        return to_int_road_scaled(raw, goal)
    return b
