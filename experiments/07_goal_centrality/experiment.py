"""Method 6 -- Goal-seeded PageRank centrality.  Run: python experiment.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "core"))
sys.path.insert(0, HERE)

from run_method import evaluate, print_table   # noqa: E402
from method import build                        # noqa: E402

if __name__ == "__main__":
    variants = {f"lambda={lam} damping={d}": build(lam, d)
                for lam, d in [(0.01, 0.85), (0.01, 0.5), (0.01, 0.95), (0.02, 0.85), (0.0, 0.85)]}
    evaluate(
        method_name="Goal-seeded PageRank centrality",
        variants=variants,
        out_path=os.path.join(HERE, "results.md"),
        main_variant="lambda=0.01 damping=0.85",
        notes="pi = (1-d) e_goal + d P^T pi with P ~ exp(-lambda*w);  h = road-scaled ln(pi(goal)/pi(u)).",
    )
    h, raw = build(0.01, 0.85)("Bucharest")
    print_table(h, "Bucharest", raw)
