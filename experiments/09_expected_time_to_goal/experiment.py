"""Method 8 (own) -- Expected Time-to-Goal.  Run: python experiment.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "core"))
sys.path.insert(0, HERE)

from run_method import evaluate, print_table   # noqa: E402
from method import build                        # noqa: E402

if __name__ == "__main__":
    variants = {
        "beta=0.01 kappa=0 (random easy-pass player)": build(0.01, 0.0),
        "beta=0.01 kappa=0.002": build(0.01, 0.002),
        "beta=0.01 kappa=0.005": build(0.01, 0.005),
        "beta=0.01 kappa=0.01": build(0.01, 0.01),
        "beta=0.01 kappa=0.05 (almost shortest path)": build(0.01, 0.05),
        "beta=0.02 kappa=0.005": build(0.02, 0.005),
        "beta=0 kappa=0.005": build(0.0, 0.005),
    }
    evaluate(
        method_name="Expected Time-to-Goal (possession clock)",
        variants=variants,
        out_path=os.path.join(HERE, "results.md"),
        main_variant="beta=0.01 kappa=0.005",
        notes="T(u) = sum_v P(u->v) (w + T(v)),  P ~ exp(-beta w) exp(-kappa T(v)).  h = round(T).",
    )
    h, raw = build(0.01, 0.005)("Bucharest")
    print_table(h, "Bucharest", raw)
    h, raw = build(0.01, 0.0)("Bucharest")
    print("--- kappa = 0 (pure random passer) ---")
    print_table(h, "Bucharest", raw)
