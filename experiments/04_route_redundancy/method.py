"""
Route redundancy (the structural version of press resistance).

Instead of counting outlets one hop away, ask how much independent attacking
channel exists from a city all the way to the goal.  Give every road a capacity
that falls with its cost and take the maximum flow:

  capacity(u,v) = 1 / w(u,v)
  R(u)          = max-flow(u -> goal)
  h(u)          = road-scaled 1 / R(u)

Max-flow is Edmonds-Karp written out longhand; with 20 cities speed is
irrelevant and the explicit version is easier to check.

This is the most "global structure" idea in the set.  It is also the one that
fails hardest, for a reason worth keeping: capacity says how wide the corridors
are and nothing at all about how long they are.
"""
import os
import sys
from collections import deque

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "core"))

from romania_graph import CITIES, GRAPH  # noqa: E402
from scaling import to_int_road_scaled  # noqa: E402


def max_flow(source, sink, capacity_fn):
    cap = {u: {v: capacity_fn(w) for v, w in GRAPH[u].items()} for u in CITIES}
    flow = 0.0
    while True:
        parent = {source: None}
        q = deque([source])
        while q and sink not in parent:
            u = q.popleft()
            for v in cap[u]:
                if v not in parent and cap[u][v] > 1e-15:
                    parent[v] = u
                    q.append(v)
        if sink not in parent:
            return flow
        b = float("inf")
        v = sink
        while parent[v] is not None:
            u = parent[v]
            b = min(b, cap[u][v])
            v = u
        v = sink
        while parent[v] is not None:
            u = parent[v]
            cap[u][v] -= b
            cap[v][u] = cap[v].get(u, 0.0) + b
            v = u
        flow += b


def route_redundancy(goal):
    return {u: (float("inf") if u == goal else max_flow(u, goal, lambda w: 1.0 / w)) for u in CITIES}


def build():
    def b(goal):
        r = route_redundancy(goal)
        raw = {c: (0.0 if c == goal else 1.0 / r[c]) for c in CITIES}
        return to_int_road_scaled(raw, goal)
    return b
