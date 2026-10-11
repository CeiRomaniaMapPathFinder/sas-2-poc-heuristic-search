"""Method 2 -- Progressive Passing.  Run: python experiment.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "core"))
sys.path.insert(0, HERE)

from run_method import evaluate, print_table   # noqa: E402
from method import build                        # noqa: E402

if __name__ == "__main__":
    variants = {
        "PPS -log, beta=0.01 gamma=0.01": build(0.01, 0.01, "log"),
        "PPS 1/x, beta=0.01 gamma=0.01": build(0.01, 0.01, "inv"),
        "PPS -log, beta=0.02 gamma=0.01": build(0.02, 0.01, "log"),
        "PPS -log, beta=0.01 gamma=0.02": build(0.01, 0.02, "log"),
        "PPS -log on value-aware xGT (tau=1)": build(0.01, 0.01, "log", tau=1.0),
    }
    evaluate(
        method_name="Progressive Passing Score (PPS)",
        variants=variants,
        out_path=os.path.join(HERE, "results.md"),
        main_variant="PPS -log, beta=0.01 gamma=0.01",
        notes="PPS(u) = sum_v P(u->v) * max(0, xGT(v) - xGT(u)); h = road-scaled -log(PPS) or 1/PPS; h(goal) forced to 0.",
    )
    h, raw = build(0.01, 0.01, "log")("Bucharest")
    print_table(h, "Bucharest", raw)
