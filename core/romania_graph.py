"""
Romania road graph (AIMA edition).

City ids are EXACTLY the strings used in the friend's app
(ai-pathfinder-web/lib/routePath.ts and ai-pathfinder-api RomaniaMap.java),
including "Rimnicu Vilcea" with a space.

COORDS are the AIMA map coordinates. They are used ONLY for the straight-line
baseline heuristic, never inside any football method.
"""

EDGES = [
    ("Arad", "Zerind", 75), ("Zerind", "Oradea", 71), ("Oradea", "Sibiu", 151), ("Arad", "Sibiu", 140),
    ("Arad", "Timisoara", 118), ("Timisoara", "Lugoj", 111), ("Lugoj", "Mehadia", 70), ("Mehadia", "Drobeta", 75),
    ("Drobeta", "Craiova", 120), ("Craiova", "Rimnicu Vilcea", 146), ("Craiova", "Pitesti", 138),
    ("Rimnicu Vilcea", "Sibiu", 80), ("Rimnicu Vilcea", "Pitesti", 97), ("Sibiu", "Fagaras", 99),
    ("Fagaras", "Bucharest", 211), ("Pitesti", "Bucharest", 101), ("Bucharest", "Giurgiu", 90),
    ("Bucharest", "Urziceni", 85), ("Urziceni", "Hirsova", 98), ("Hirsova", "Eforie", 86),
    ("Urziceni", "Vaslui", 142), ("Vaslui", "Iasi", 92), ("Iasi", "Neamt", 87),
]

# GRAPH[u][v] = road cost. Same shape as the friend's Java Map<String, Map<String,Integer>>.
GRAPH = {}
for a, b, w in EDGES:
    GRAPH.setdefault(a, {})[b] = w
    GRAPH.setdefault(b, {})[a] = w

CITIES = sorted(GRAPH)

COORDS = {
    "Arad": (91, 492), "Bucharest": (400, 327), "Craiova": (253, 288), "Drobeta": (165, 299),
    "Eforie": (562, 293), "Fagaras": (305, 449), "Giurgiu": (375, 270), "Hirsova": (534, 350),
    "Iasi": (473, 506), "Lugoj": (165, 379), "Mehadia": (168, 339), "Neamt": (406, 537),
    "Oradea": (131, 571), "Pitesti": (320, 368), "Rimnicu Vilcea": (233, 410), "Sibiu": (207, 457),
    "Timisoara": (94, 410), "Urziceni": (456, 350), "Vaslui": (509, 444), "Zerind": (108, 531),
}

ALL_WEIGHTS = [w for _, _, w in EDGES]
MEAN_EDGE = sum(ALL_WEIGHTS) / len(ALL_WEIGHTS)      # ~ 106.9
MIN_EDGE = min(ALL_WEIGHTS)                          # 70
MAX_EDGE = max(ALL_WEIGHTS)                          # 211


def neighbors(u):
    """List of (v, w) for city u."""
    return list(GRAPH[u].items())
