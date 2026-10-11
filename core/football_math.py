"""
Building blocks shared by the football heuristics.

Everything is plain Python so each formula is visible and can be ported to
Java line-by-line (see tools/java/FootballMath.java).
"""
import math
from romania_graph import GRAPH, CITIES


def pass_preference(beta):
    """
    q(u,v) = exp(-beta * w)   -> cheaper road = easier pass = bigger number.
    Returns q[u][v].
    """
    return {u: {v: math.exp(-beta * w) for v, w in GRAPH[u].items()} for u in CITIES}


def normalize_rows(q):
    """P(u->v) = q(u,v) / sum_k q(u,k).  Each row sums to 1."""
    P = {}
    for u, row in q.items():
        s = sum(row.values())
        P[u] = {v: x / s for v, x in row.items()}
    return P


def transition_probs(beta):
    """P(u->v) = softmax over neighbours of -beta*w."""
    return normalize_rows(pass_preference(beta))


def completion_probs(gamma):
    """C(u,v) = exp(-gamma * w): probability the pass along road (u,v) is completed."""
    return {u: {v: math.exp(-gamma * w) for v, w in GRAPH[u].items()} for u in CITIES}


def fixed_point(update, init, tol=1e-12, max_iter=100000):
    """
    Iterate x <- update(x) until max |change| < tol.
    update(x) must return a NEW dict.  Returns (x, iterations).
    """
    x = dict(init)
    for it in range(1, max_iter + 1):
        nx = update(x)
        delta = max(abs(nx[c] - x[c]) for c in nx)
        x = nx
        if delta < tol:
            return x, it
    return x, max_iter


def neg_log(value_table, eps=1e-12):
    """h = -log(value + eps); high value -> low h."""
    return {c: -math.log(v + eps) for c, v in value_table.items()}


def to_int_table(raw, goal, scale=1.0):
    """
    Final step for every heuristic:
      int h(n) = floor(scale * raw(n) + 0.5), then force h(goal) = 0 and h >= 0.
    raw must already be 'lower is better'.
    floor(x + 0.5) instead of round() so Python and Java give identical ints
    (Python's round() is banker's rounding, Java's Math.round is not).
    """
    out = {}
    for c, v in raw.items():
        out[c] = max(0, int(math.floor(scale * v + 0.5)))
    out[goal] = 0
    return out


def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs)
