"""Route redundancy (max-flow).  Run: python experiment.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "core"))
sys.path.insert(0, HERE)

from method import build, route_redundancy  # noqa: E402
from run_method import evaluate, print_table  # noqa: E402

if __name__ == "__main__":
    print("max-flow to Bucharest:", {c: round(v, 4) for c, v in route_redundancy("Bucharest").items()})
    evaluate(
        method_name="Route redundancy (max-flow with capacity 1/w)",
        variants={"max-flow, capacity 1/w": build()},
        out_path=os.path.join(HERE, "results.md"),
        notes="R(u) = max-flow(u, goal) with capacity(u,v) = 1/w(u,v);  h = road-scaled 1/R(u).",
    )
    h, raw = build()("Bucharest")
    print_table(h, "Bucharest", raw)
