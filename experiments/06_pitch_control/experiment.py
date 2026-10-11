"""Method 5 -- Pitch Control / Goal Influence.  Run: python experiment.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "core"))
sys.path.insert(0, HERE)

from run_method import evaluate, print_table   # noqa: E402
from method import build                        # noqa: E402

if __name__ == "__main__":
    variants = {}
    for lam, alpha in [(0.01, 1.0), (0.01, 0.8), (0.01, 0.5), (0.02, 1.0), (0.02, 0.8), (0.005, 0.5)]:
        try:
            b = build(lam, alpha)
            b("Bucharest")
            variants[f"lambda={lam} alpha={alpha}"] = b
        except ValueError as e:
            print("skipped:", e)
    evaluate(
        method_name="Pitch Control / Goal Influence",
        variants=variants,
        out_path=os.path.join(HERE, "results.md"),
        main_variant="lambda=0.02 alpha=0.8",
        notes="I(goal)=1, I(u) = alpha * sum_v exp(-lambda*w) * I(v);  h = round(-log(I)/lambda).",
    )
    h, raw = build(0.02, 0.8)("Bucharest")
    print_table(h, "Bucharest", raw)
