"""
Method 4 -- Packing / Line Breaking.

In football, "packing" counts how many defenders an action takes out of the
game.  Here the "defensive lines" are the structural weak points of the road
network:

  bridge             = a road whose removal splits the map in two
  articulation point = a city whose removal splits the map in two

A city n still has to "break" every line that separates it from the goal.

  lines(n)  = number of bridges that separate n from goal
            + number of articulation points that separate n from goal (n and goal excluded)

  h_count(n)    = lines(n)                                  (pure structure, many ties)
  h_weighted(n) = sum of w(bridge) over separating bridges
                + for each separating articulation point a: the cheapest road into a
                  from the side where n lives                (a "price" for breaking that line)

Both are road-scaled to int.  No shortest-path search is used; only
connectivity checks after removing a road / a city.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "core"))

from romania_graph import GRAPH, CITIES, EDGES      # noqa: E402
from scaling import to_int_road_scaled              # noqa: E402


def reachable(src, removed_edge=None, removed_node=None):
    """Set of cities reachable from src after removing one edge and/or one node."""
    seen = {src}
    stack = [src]
    while stack:
        u = stack.pop()
        for v in GRAPH[u]:
            if v == removed_node:
                continue
            if removed_edge and {u, v} == set(removed_edge):
                continue
            if v not in seen:
                seen.add(v)
                stack.append(v)
    return seen


def bridges():
    out = []
    for a, b, w in EDGES:
        if b not in reachable(a, removed_edge=(a, b)):
            out.append((a, b, w))
    return out


def articulation_points():
    out = []
    for c in CITIES:
        others = [x for x in CITIES if x != c]
        if len(reachable(others[0], removed_node=c)) < len(others):
            out.append(c)
    return out


BRIDGES = bridges()
ARTICULATION = articulation_points()


def lines_between(n, goal):
    """(separating bridges, separating articulation points) for city n."""
    sep_b = []
    for a, b, w in BRIDGES:
        if goal not in reachable(n, removed_edge=(a, b)):
            sep_b.append((a, b, w))
    sep_a = []
    for a in ARTICULATION:
        if a in (n, goal):
            continue
        if goal not in reachable(n, removed_node=a):
            sep_a.append(a)
    return sep_b, sep_a


def packing_count(goal):
    out = {}
    for n in CITIES:
        if n == goal:
            out[n] = 0
            continue
        sb, sa = lines_between(n, goal)
        out[n] = len(sb) + len(sa)
    return out


def packing_weighted(goal):
    out = {}
    for n in CITIES:
        if n == goal:
            out[n] = 0.0
            continue
        sb, sa = lines_between(n, goal)
        total = sum(w for _, _, w in sb)
        for a in sa:
            side = reachable(n, removed_node=a)               # n's side of the line
            total += min(GRAPH[a][v] for v in GRAPH[a] if v in side)
        out[n] = float(total)
    return out


def build_count():
    return lambda goal: to_int_road_scaled({c: float(v) for c, v in packing_count(goal).items()}, goal)


def build_weighted():
    return lambda goal: to_int_road_scaled(packing_weighted(goal), goal)
