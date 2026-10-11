"""Press resistance.  Run: python experiment.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "core"))
sys.path.insert(0, HERE)

from method import build_pr_count, build_pr_sum  # noqa: E402
from run_method import evaluate, print_table  # noqa: E402

if __name__ == "__main__":
    variants = {
        "PR_sum -log, beta=0.01 gamma=0.01": build_pr_sum(0.01, 0.01, "log"),
        "PR_sum 1/x, beta=0.01 gamma=0.01": build_pr_sum(0.01, 0.01, "inv"),
        "PR_sum -log, beta=0.01 gamma=0.02": build_pr_sum(0.01, 0.02, "log"),
        "PR_sum -log on value-aware xGT (tau=1)": build_pr_sum(0.01, 0.01, "log", tau=1.0),
        "PR_count theta=0.5": build_pr_count(0.01, 0.01, 0.5),
    }
    evaluate(
        method_name="Press resistance",
        variants=variants,
        out_path=os.path.join(HERE, "results.md"),
        main_variant="PR_sum -log, beta=0.01 gamma=0.01",
        notes="PR_sum(u) = sum_v C(u,v)*xGT(v); h = road-scaled -log(PR_sum) or 1/PR_sum.",
    )
    h, raw = build_pr_sum(0.01, 0.01, "log")("Bucharest")
    print_table(h, "Bucharest", raw)
