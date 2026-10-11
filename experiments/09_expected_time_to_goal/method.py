"""
Method 8 (own idea) -- Expected Time-to-Goal, the "possession clock".

Every pass along road (u,v) takes w(u,v) seconds.  The passer at u chooses the
next pass with probability

    P(u->v) ~ exp(-beta * w(u,v)) * exp(-kappa * T(v))

i.e. easy passes are preferred (beta) and passes to team-mates who are closer
to scoring are preferred (kappa).  kappa = 0 is a pure "easy pass" player;
larger kappa is a smarter, more goal-directed player.

    T(goal) = 0
    T(u)    = sum_v P(u->v) * ( w(u,v) + T(v) )       expected seconds until the ball reaches the goal

T(u) is the mean first-passage time of this passing process.  It is already
in road units, so:

    h(u) = round(T(u))          (no calibration needed, h(goal) = 0 automatically)

Why it is not just shortest path: T averages over EVERY passing sequence the
player might realistically produce, including back-passes and dead-end trips.
A city whose neighbours are dead ends (Neamt, Eforie) is punished for the time
the ball wastes there.  As kappa -> infinity the player always picks the best
pass and T -> shortest path (that is the circular case to avoid).
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "core"))

from romania_graph import GRAPH, CITIES                              # noqa: E402
from football_math import pass_preference, fixed_point, to_int_table  # noqa: E402


def expected_time(goal, beta, kappa=0.0):
    q = pass_preference(beta)

    def update(T):
        nT = {goal: 0.0}
        for u in CITIES:
            if u == goal:
                continue
            pref = {v: q[u][v] * math.exp(-kappa * T[v]) for v in GRAPH[u]}
            s = sum(pref.values())
            nT[u] = sum((pref[v] / s) * (GRAPH[u][v] + T[v]) for v in GRAPH[u])
        return nT

    init = {c: 0.0 for c in CITIES}
    T, _ = fixed_point(update, init, tol=1e-9, max_iter=200000)
    return T


def build(beta, kappa=0.0):
    def b(goal):
        T = expected_time(goal, beta, kappa)
        return to_int_table(T, goal), T
    return b
