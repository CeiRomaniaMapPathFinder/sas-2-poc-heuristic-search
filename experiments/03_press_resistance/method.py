"""
Press resistance.

A player with one passing option is easy to press; a player with several good
outlets is not.  On the map: a city is strong if several of its roads lead
somewhere threatening.

  quality(u,v) = C(u,v) * xGT(v)        a completed pass to v, times how threatening v is

  PR_sum(u)   = sum over neighbours of quality(u,v)      the weighted version
  PR_count(u) = how many neighbours clear a quality threshold

  h = road-scaled -log(PR_sum)   (or 1/PR_sum, which the brief suggested)

Note the difference to xGT itself: xGT *averages* the outlets with the pass
probabilities, so extra weak outlets dilute the value; PR *adds* them, so extra
outlets can only help.  That one change flips the heuristic from over- to
under-estimating, which turns out to matter more than it sounds.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "core"))

from football_math import completion_probs  # noqa: E402
from romania_graph import CITIES, GRAPH  # noqa: E402
from scaling import to_int_road_scaled  # noqa: E402
from xgt import xgt  # noqa: E402

EPS = 1e-9


def pass_quality(goal, beta, gamma, tau=0.0):
    x = xgt(goal, beta, gamma, tau)
    C = completion_probs(gamma)
    return {u: {v: C[u][v] * x[v] for v in GRAPH[u]} for u in CITIES}, x


def pr_sum(goal, beta, gamma, tau=0.0):
    q, _ = pass_quality(goal, beta, gamma, tau)
    return {u: sum(q[u].values()) for u in CITIES}


def pr_count(goal, beta, gamma, theta=0.5):
    q, _ = pass_quality(goal, beta, gamma)
    out = {}
    for u in CITIES:
        best = max(q[u].values())
        out[u] = sum(1 for v in GRAPH[u] if q[u][v] >= theta * best)
    return out


def build_pr_sum(beta, gamma, transform="log", tau=0.0):
    def b(goal):
        s = pr_sum(goal, beta, gamma, tau)
        raw = {c: (-math.log(v + EPS) if transform == "log" else 1.0 / (v + EPS)) for c, v in s.items()}
        raw[goal] = 0.0
        m = min(v for c, v in raw.items() if c != goal)
        if m < 0:
            raw = {c: (v - m if c != goal else 0.0) for c, v in raw.items()}
        return to_int_road_scaled(raw, goal)
    return b


def build_pr_count(beta, gamma, theta=0.5):
    def b(goal):
        s = pr_count(goal, beta, gamma)
        raw = {c: 1.0 / s[c] for c in CITIES}
        raw[goal] = 0.0
        return to_int_road_scaled(raw, goal)
    return b
