"""
Search algorithms used by every experiment.

- dijkstra(goal): true remaining cost d*(n, goal) for every n. EVALUATION ONLY.
  No heuristic in this archive may read it as an input.
- astar(start, goal, h): standard A* with re-opening of closed nodes when a cheaper g
  is found (so a non-consistent heuristic can still recover the optimal path if it
  gets the chance). UCS = astar with h = 0.
"""
import heapq
from romania_graph import GRAPH


def dijkstra(goal):
    dist = {goal: 0}
    pq = [(0, goal)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v, w in GRAPH[u].items():
            nd = d + w
            if nd < dist.get(v, float("inf")):
                dist[v] = nd
                heapq.heappush(pq, (nd, v))
    return dist


class SearchResult:
    def __init__(self, path, cost, expanded, order):
        self.path = path            # list of city ids
        self.cost = cost            # sum of edge weights along path
        self.expanded = expanded    # number of nodes popped from the frontier
        self.order = order          # expansion order (list of city ids)

    def __repr__(self):
        return f"SearchResult(cost={self.cost}, expanded={self.expanded}, path={'->'.join(self.path)})"


def astar(start, goal, h):
    """
    h: dict city -> number (a per-goal table) OR a callable h(city).
    Ties on f are broken by insertion order (deterministic).
    """
    hf = h if callable(h) else (lambda n: h[n])
    g = {start: 0}
    parent = {start: None}
    closed = set()
    order = []
    counter = 0
    pq = [(hf(start), counter, start)]
    while pq:
        f, _, u = heapq.heappop(pq)
        if u in closed:
            continue
        closed.add(u)
        order.append(u)
        if u == goal:
            path = []
            while u is not None:
                path.append(u)
                u = parent[u]
            path.reverse()
            return SearchResult(path, g[goal], len(order), order)
        for v, w in GRAPH[u].items():
            ng = g[u] + w
            if ng < g.get(v, float("inf")):
                g[v] = ng
                parent[v] = u
                closed.discard(v)   # re-open if we found a cheaper way in
                counter += 1
                heapq.heappush(pq, (ng + hf(v), counter, v))
    return None


def ucs(start, goal):
    return astar(start, goal, lambda n: 0)
