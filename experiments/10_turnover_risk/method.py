"""
Method 9 (own idea) -- Turnover Risk / pressing chain.

Start a possession at city u.  The player picks a pass with
P(u->v) ~ exp(-beta*w) * exp(-kappa*K(v))   (easy passes preferred; with kappa > 0
also passes to team-mates with a cheaper expected finish).  The pass is completed with probability
C(u,v) = exp(-gamma*w); otherwise it is a TURNOVER.

Cost of a possession = road cost actually travelled + a penalty L for every
turnover (the team has to win the ball back and start again from u).

    K(goal) = 0
    K(u) = sum_v P(u->v) * [ w(u,v)                          the pass itself
                             + C(u,v) * K(v)                  completed: continue from v
                             + (1 - C(u,v)) * (L + K(u)) ]    turnover: pay L, restart at u

Solving the K(u) on both sides:

    K(u) = ( sum_v P [ w + C K(v) + (1-C) L ] ) / ( 1 - sum_v P (1-C) )

L is derived from the graph (mean road cost), not invented:  L = MEAN_EDGE.

K(u) is in road units, so  h(u) = round(K(u)).

Feel: cities that can only progress through long, risky roads (many turnovers
expected) get punished; cities with short safe outlets look good.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "core"))

from romania_graph import GRAPH, CITIES, MEAN_EDGE                                       # noqa: E402
from football_math import pass_preference, completion_probs, fixed_point, to_int_table  # noqa: E402
import math  # noqa: E402


def turnover_cost(goal, beta, gamma, L=None, kappa=0.0):
    L = MEAN_EDGE if L is None else L
    q = pass_preference(beta)
    C = completion_probs(gamma)

    def update(K):
        nK = {goal: 0.0}
        for u in CITIES:
            if u == goal:
                continue
            pref = {v: q[u][v] * math.exp(-kappa * K[v]) for v in GRAPH[u]}
            s = sum(pref.values())
            P = {v: pref[v] / s for v in GRAPH[u]}
            num = sum(P[v] * (GRAPH[u][v] + C[u][v] * K[v] + (1 - C[u][v]) * L) for v in GRAPH[u])
            den = 1.0 - sum(P[v] * (1 - C[u][v]) for v in GRAPH[u])
            nK[u] = num / den
        return nK

    init = {c: 0.0 for c in CITIES}
    K, _ = fixed_point(update, init, tol=1e-9, max_iter=200000)
    return K


def build(beta, gamma, L=None, kappa=0.0):
    def b(goal):
        K = turnover_cost(goal, beta, gamma, L, kappa)
        return to_int_table(K, goal), K
    return b
