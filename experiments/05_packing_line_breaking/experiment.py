"""Method 4 -- Packing / Line Breaking.  Run: python experiment.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "core"))
sys.path.insert(0, HERE)

from run_method import evaluate, print_table                                  # noqa: E402
from method import build_count, build_weighted, BRIDGES, ARTICULATION, packing_count  # noqa: E402

if __name__ == "__main__":
    print("bridges:", BRIDGES)
    print("articulation points:", ARTICULATION)
    print("lines to break, goal=Bucharest:", packing_count("Bucharest"))
    evaluate(
        method_name="Packing / Line Breaking",
        variants={
            "lines count": build_count(),
            "lines weighted by road cost": build_weighted(),
        },
        out_path=os.path.join(HERE, "results.md"),
        main_variant="lines weighted by road cost",
        notes="h(n) = number (or road-cost weight) of bridges + articulation points that separate n from the goal; road-scaled.",
    )
    h, raw = build_weighted()("Bucharest")
    print_table(h, "Bucharest", raw)
