"""
Baseline heuristics used for comparison in every experiment.
All return a per-goal table {city: int}.
"""
import math
from collections import deque
from romania_graph import GRAPH, CITIES, COORDS


def h_zero(goal):
    return {c: 0 for c in CITIES}


def h_sld(goal):
    """Straight-line distance from AIMA coordinates (integer)."""
    gx, gy = COORDS[goal]
    return {c: int(round(math.hypot(COORDS[c][0] - gx, COORDS[c][1] - gy))) for c in CITIES}


def hop_rings(goal):
    """BFS hop distance from goal for every city."""
    ring = {goal: 0}
    q = deque([goal])
    while q:
        u = q.popleft()
        for v in GRAPH[u]:
            if v not in ring:
                ring[v] = ring[u] + 1
                q.append(v)
    return ring


def h_ring_min_edge(goal):
    """
    The old 'financial rings' idea from the guide (section 12):
    L(v) = hop distance from goal; h(v) = sum over layers k = 1..L(v) of the
    minimum edge weight connecting layer k to layer k-1.
    Every city in the same ring gets the same value.
    """
    ring = hop_rings(goal)
    max_ring = max(ring.values())
    layer_min = {}
    for k in range(1, max_ring + 1):
        m = float("inf")
        for u in CITIES:
            if ring[u] != k:
                continue
            for v, w in GRAPH[u].items():
                if ring[v] == k - 1:
                    m = min(m, w)
        layer_min[k] = m
    h = {}
    for c in CITIES:
        h[c] = int(sum(layer_min[k] for k in range(1, ring[c] + 1)))
    return h


BASELINES = {
    "UCS (h=0)": h_zero,
    "Straight-line": h_sld,
    "Ring min-edge (old)": h_ring_min_edge,
}
