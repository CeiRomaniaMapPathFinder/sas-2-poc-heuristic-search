"""
Expected Goal Threat.  Run: python experiment.py

Everything xGT can be, in one table: the first formulation without pass risk,
the cost-only passer under several beta/gamma, and the value-aware passer as
tau is raised.  The model itself lives in core/xgt.py because later experiments
build on it.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "core"))

from football_math import to_int_table  # noqa: E402
from run_method import evaluate, print_table  # noqa: E402
from xgt import build, xgt_no_completion  # noqa: E402


def build_no_completion(beta, horizon=None):
    """
    No gamma here, so -ln(xGT) is scaled by 1/beta instead to land in road-like
    units.  Cities the ball cannot reach within `horizon` passes have xGT = 0;
    they are parked above the largest finite value rather than at infinity.
    """
    def b(goal):
        x = xgt_no_completion(goal, beta, horizon)
        raw = {c: (-math.log(v) / beta if v > 0 else float("inf")) for c, v in x.items()}
        finite = [v for v in raw.values() if v != float("inf")]
        cap = (max(finite) if finite else 0) + 100
        raw = {c: (v if v != float("inf") else cap) for c, v in raw.items()}
        return to_int_table(raw, goal), raw
    return b


if __name__ == "__main__":
    variants = {
        # the dead end: no way to lose the ball
        "no pass risk, run to convergence": build_no_completion(0.01),
        "no pass risk, stop after 3 passes": build_no_completion(0.01, horizon=3),
        "no pass risk, stop after 6 passes": build_no_completion(0.01, horizon=6),
        # cost-only passer
        "cost-only passer, beta=0.01 gamma=0.01": build(0.01, 0.01, 0.0),
        "cost-only passer, beta=0.02 gamma=0.01": build(0.02, 0.01, 0.0),
        "cost-only passer, beta=0.05 gamma=0.01": build(0.05, 0.01, 0.0),
        "cost-only passer, beta=0.01 gamma=0.005": build(0.01, 0.005, 0.0),
        "cost-only passer, beta=0.01 gamma=0.02": build(0.01, 0.02, 0.0),
        # value-aware passer: tau is the dial
        "value-aware passer, tau=0.5": build(0.01, 0.01, 0.5),
        "value-aware passer, tau=1": build(0.01, 0.01, 1.0),
        "value-aware passer, tau=2": build(0.01, 0.01, 2.0),
        "value-aware passer, tau=3 (nearly shortest path)": build(0.01, 0.01, 3.0),
        "value-aware passer, tau=1 beta=0.02": build(0.02, 0.01, 1.0),
        "value-aware passer, tau=1.5 beta=0.02 (the one we kept)": build(0.02, 0.01, 1.5),
    }
    evaluate(
        method_name="Expected Goal Threat",
        variants=variants,
        out_path=os.path.join(HERE, "results.md"),
        main_variant="value-aware passer, tau=1.5 beta=0.02 (the one we kept)",
        notes="h(u) = floor(-ln(xGT(u))/gamma + 0.5). The no-pass-risk rows have no gamma and are scaled by 1/beta instead.",
    )
    h, raw = build(0.02, 0.01, 1.5)("Bucharest")
    print_table(h, "Bucharest", raw)
