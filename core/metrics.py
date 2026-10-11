"""
The tests from creative_heuristic_function_guide.md section 14.

h tables are {city: int}; d* comes from search.dijkstra(goal) and is used for
EVALUATION ONLY.
"""
from itertools import combinations
from romania_graph import CITIES
from search import dijkstra, astar
from baselines import hop_rings


# ---------- Test 1: goal sanity ----------
def goal_sanity(h, goal):
    hg = h[goal]
    return {"h_goal": hg, "is_min": hg == min(h.values()), "is_zero": hg == 0}


# ---------- Test 2: obvious pairwise comparisons ----------
# (goal, better city, worse city) -- 'better' has the smaller true remaining cost.
PAIR_CHECKS = [
    ("Bucharest", "Giurgiu", "Pitesti"),          # 90 vs 101
    ("Bucharest", "Urziceni", "Fagaras"),         # 85 vs 211
    ("Bucharest", "Fagaras", "Craiova"),          # 211 vs 239
    ("Bucharest", "Pitesti", "Rimnicu Vilcea"),   # 101 vs 198
    ("Sibiu", "Arad", "Oradea"),                  # 140 vs 151
    ("Sibiu", "Rimnicu Vilcea", "Zerind"),        # 80 vs 215
    ("Sibiu", "Fagaras", "Pitesti"),              # 99 vs 177
    ("Sibiu", "Craiova", "Timisoara"),            # 226 vs 258
]


def pair_checks(builder):
    """builder(goal) -> int table.  Returns list of dict rows."""
    rows = []
    cache = {}
    for goal, a, b in PAIR_CHECKS:
        if goal not in cache:
            cache[goal] = builder(goal)
        h = cache[goal]
        d = dijkstra(goal)
        rows.append({
            "goal": goal, "better": a, "worse": b,
            "d_better": d[a], "d_worse": d[b],
            "h_better": h[a], "h_worse": h[b],
            "pass": h[a] < h[b], "tie": h[a] == h[b],
        })
    return rows


# ---------- Test 4: Spearman ----------
def _ranks(values):
    """Average ranks (ties share the mean rank)."""
    idx = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(idx):
        j = i
        while j + 1 < len(idx) and values[idx[j + 1]] == values[idx[i]]:
            j += 1
        r = (i + j) / 2 + 1
        for k in range(i, j + 1):
            ranks[idx[k]] = r
        i = j + 1
    return ranks


def spearman(h, dstar, cities=None):
    cities = cities or list(CITIES)
    x = _ranks([h[c] for c in cities])
    y = _ranks([dstar[c] for c in cities])
    n = len(cities)
    mx, my = sum(x) / n, sum(y) / n
    num = sum((a - mx) * (b - my) for a, b in zip(x, y))
    den = (sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y)) ** 0.5
    return num / den if den else 0.0


# ---------- Test 5: inversions ----------
def inversions(h, dstar, goal):
    """
    Over all unordered pairs of non-goal cities:
      inversion  = d*(A) < d*(B) but h(A) > h(B)
      weighted   = sum |d*(A) - d*(B)| over inverted pairs / sum over all pairs
    Ties in h are counted separately (not inversions, but not discriminating).
    """
    cities = [c for c in CITIES if c != goal]
    count = ties = 0
    pen = pen_total = 0.0
    worst = []
    total = 0
    for a, b in combinations(cities, 2):
        total += 1
        if dstar[a] == dstar[b]:
            continue
        if dstar[a] > dstar[b]:
            a, b = b, a           # now a is truly closer
        gap = dstar[b] - dstar[a]
        pen_total += gap
        if h[a] > h[b]:
            count += 1
            pen += gap
            worst.append((gap, a, b, dstar[a], dstar[b], h[a], h[b]))
        elif h[a] == h[b]:
            ties += 1
    worst.sort(reverse=True)
    return {
        "inversions": count, "ties": ties, "pairs": total,
        "weighted_penalty": pen / pen_total if pen_total else 0.0,
        "worst": worst[:5],
    }


# ---------- Ring discrimination (guide section 12) ----------
def ring_discrimination(h, goal):
    ring = hop_rings(goal)
    out = {}
    for c in CITIES:
        out.setdefault(ring[c], []).append(h[c])
    return {k: (len(v), len(set(v))) for k, v in sorted(out.items())}


# ---------- Test 3: full table ----------
def full_table(h, raw, dstar, goal):
    cities = sorted(CITIES, key=lambda c: dstar[c])
    rd = _ranks([dstar[c] for c in cities])
    rh = _ranks([h[c] for c in cities])
    rows = []
    for i, c in enumerate(cities):
        diff = abs(rd[i] - rh[i])
        rows.append({
            "city": c, "d_star": dstar[c], "raw": raw.get(c) if raw else None, "h": h[c],
            "rank_d": rd[i], "rank_h": rh[i], "sensible": diff <= 3,
        })
    return rows


# ---------- Test 6: A* behaviour ----------
ASTAR_PAIRS = [
    ("Arad", "Bucharest"), ("Zerind", "Sibiu"), ("Timisoara", "Bucharest"), ("Oradea", "Bucharest"),
    ("Neamt", "Bucharest"), ("Eforie", "Sibiu"), ("Arad", "Neamt"), ("Craiova", "Iasi"),
    ("Lugoj", "Fagaras"), ("Bucharest", "Arad"),
]


def astar_fixed(builder):
    rows = []
    cache = {}
    for s, g in ASTAR_PAIRS:
        if g not in cache:
            cache[g] = builder(g)
        r = astar(s, g, cache[g])
        opt = dijkstra(g)[s]
        rows.append({"start": s, "goal": g, "cost": r.cost, "optimal_cost": opt,
                     "optimal": r.cost == opt, "expanded": r.expanded, "path": r.path})
    return rows


def astar_all_pairs(builder):
    """Aggregate over all 380 ordered (start, goal) pairs."""
    n = opt_n = 0
    overshoot = 0.0
    expanded = 0
    worst = []
    for g in CITIES:
        h = builder(g)
        d = dijkstra(g)
        for s in CITIES:
            if s == g:
                continue
            r = astar(s, g, h)
            n += 1
            expanded += r.expanded
            if r.cost == d[s]:
                opt_n += 1
            else:
                overshoot += r.cost - d[s]
                worst.append((r.cost - d[s], s, g, r.cost, d[s]))
    worst.sort(reverse=True)
    return {"pairs": n, "optimal": opt_n, "optimal_pct": 100.0 * opt_n / n,
            "mean_overshoot_when_wrong": (overshoot / (n - opt_n)) if n > opt_n else 0.0,
            "mean_expanded": expanded / n, "worst": worst[:5]}


def all_goal_rank_summary(builder):
    """Mean Spearman and mean weighted inversion penalty over all 20 goals."""
    sp, wp, inv = [], [], []
    for g in CITIES:
        h = builder(g)
        d = dijkstra(g)
        sp.append(spearman(h, d))
        r = inversions(h, d, g)
        wp.append(r["weighted_penalty"])
        inv.append(r["inversions"])
    return {"mean_spearman": sum(sp) / len(sp), "min_spearman": min(sp),
            "mean_weighted_penalty": sum(wp) / len(wp), "mean_inversions": sum(inv) / len(inv)}
