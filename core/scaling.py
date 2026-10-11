"""
Scale calibration for methods whose raw score has no natural road-cost unit.

    scale = mean(d*) / mean(raw)        over non-goal cities

d* (true remaining cost) is used ONLY to pick this single multiplier.
It does not change the ORDER of any city, so it cannot fix a bad ranking;
it only makes h comparable in size to g so that f = g + h is meaningful.
Methods with an intrinsic unit (xGT via -log/gamma, expected-time methods)
do not use this.
"""
from romania_graph import CITIES
from search import dijkstra
from football_math import to_int_table


def road_scale_factor(raw, goal):
    d = dijkstra(goal)
    cities = [c for c in CITIES if c != goal and raw[c] != float("inf")]
    m_raw = sum(raw[c] for c in cities) / len(cities)
    m_d = sum(d[c] for c in cities) / len(cities)
    return m_d / m_raw if m_raw > 0 else 1.0


def to_int_road_scaled(raw, goal):
    """raw (lower = better, any unit) -> int table in road-like units."""
    raw = dict(raw)
    finite = [v for c, v in raw.items() if v != float("inf")]
    cap = (max(finite) if finite else 0) * 2 + 1
    raw = {c: (v if v != float("inf") else cap) for c, v in raw.items()}
    s = road_scale_factor(raw, goal)
    return to_int_table(raw, goal, scale=s), raw
