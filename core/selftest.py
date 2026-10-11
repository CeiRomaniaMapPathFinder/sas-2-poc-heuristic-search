"""Sanity checks for the shared code.  Run: python selftest.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from romania_graph import GRAPH, CITIES, EDGES
from search import dijkstra, astar, ucs
from baselines import h_sld, h_ring_min_edge, hop_rings
from metrics import spearman, inversions, ring_discrimination

assert len(CITIES) == 20 and len(EDGES) == 23
assert GRAPH["Rimnicu Vilcea"]["Sibiu"] == 80

d = dijkstra("Bucharest")
assert d["Arad"] == 418 and d["Giurgiu"] == 90 and d["Pitesti"] == 101 and d["Neamt"] == 406, d
r = ucs("Arad", "Bucharest")
assert r.cost == 418 and r.path == ["Arad", "Sibiu", "Rimnicu Vilcea", "Pitesti", "Bucharest"], r

# UCS equals Dijkstra on all pairs
for g in CITIES:
    dg = dijkstra(g)
    for s in CITIES:
        if s != g:
            assert ucs(s, g).cost == dg[s]

# SLD A* is optimal Arad->Bucharest and expands fewer nodes than UCS
r_sld = astar("Arad", "Bucharest", h_sld("Bucharest"))
assert r_sld.cost == 418 and r_sld.expanded < r.expanded, (r_sld, r)

# Spearman of d* with itself = 1, and with negative = -1
assert abs(spearman(d, d) - 1) < 1e-12
assert abs(spearman({c: -v for c, v in d.items()}, d) + 1) < 1e-12
assert inversions(d, d, "Bucharest")["inversions"] == 0

# ring baseline: all same-ring cities share a value (the known weakness)
hr = h_ring_min_edge("Bucharest")
for k, (n, distinct) in ring_discrimination(hr, "Bucharest").items():
    assert distinct == 1, (k, n, distinct)
print("hop rings from Bucharest:", hop_rings("Bucharest"))
print("ring-min-edge h(Bucharest goal):", hr)
print("SLD h(Bucharest goal):", h_sld("Bucharest"))
print("selftest OK")
