"""Method 9 (own) -- Turnover Risk.  Run: python experiment.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "core"))
sys.path.insert(0, HERE)

from run_method import evaluate, print_table   # noqa: E402
from method import build                        # noqa: E402

if __name__ == "__main__":
    variants = {
        "beta=0.01 gamma=0.005 L=mean edge": build(0.01, 0.005),
        "beta=0.01 gamma=0.01 L=mean edge": build(0.01, 0.01),
        "beta=0.02 gamma=0.005 L=mean edge": build(0.02, 0.005),
        "beta=0.01 gamma=0.002 L=mean edge": build(0.01, 0.002),
        "beta=0.01 gamma=0.005 L=0 (no penalty)": build(0.01, 0.005, L=0.0),
        "goal-aware passer kappa=0.002": build(0.01, 0.005, kappa=0.002),
        "goal-aware passer kappa=0.005": build(0.01, 0.005, kappa=0.005),
        "goal-aware passer kappa=0.01": build(0.01, 0.005, kappa=0.01),
    }
    evaluate(
        method_name="Turnover Risk (pressing chain)",
        variants=variants,
        out_path=os.path.join(HERE, "results.md"),
        main_variant="goal-aware passer kappa=0.005",
        notes="K(u) = expected road cost + turnover penalties before the ball reaches the goal, h = round(K).",
    )
    h, raw = build(0.01, 0.005, kappa=0.005)("Bucharest")
    print_table(h, "Bucharest", raw)
