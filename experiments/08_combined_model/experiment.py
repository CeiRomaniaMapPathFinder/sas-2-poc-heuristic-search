"""Method 7 -- Combined football model.  Run: python experiment.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "core"))
sys.path.insert(0, HERE)

from run_method import evaluate, print_table                    # noqa: E402
from method import build_multiplicative, build_weighted_sum     # noqa: E402

B, G = 0.01, 0.01

if __name__ == "__main__":
    variants = {
        "mult: cost-only xGT, alpha=0 delta=0 (= xGT alone)": build_multiplicative(B, G, 0.0, 0.0, 0.0),
        "mult: cost-only xGT, alpha=1 delta=1": build_multiplicative(B, G, 0.0, 1.0, 1.0),
        "mult: cost-only xGT, alpha=3 delta=1": build_multiplicative(B, G, 0.0, 3.0, 1.0),
        "mult: value-aware xGT (tau=1), alpha=0 delta=0 (= xGT alone)": build_multiplicative(B, G, 1.0, 0.0, 0.0),
        "mult: value-aware xGT (tau=1), alpha=1 delta=1": build_multiplicative(B, G, 1.0, 1.0, 1.0),
        "mult: value-aware xGT (tau=1), alpha=2 delta=0.5": build_multiplicative(B, G, 1.0, 2.0, 0.5),
        "mult: value-aware xGT (tau=1), alpha=0.5 delta=2": build_multiplicative(B, G, 1.0, 0.5, 2.0),
        "sum: tau=1, a=0.6 b=0.2 c=0.2": build_weighted_sum(B, G, 1.0, 0.6, 0.2, 0.2),
        "sum: tau=1, a=1/3 b=1/3 c=1/3": build_weighted_sum(B, G, 1.0, 1 / 3, 1 / 3, 1 / 3),
    }
    evaluate(
        method_name="Combined football model (xGT x press resistance x progressive passing)",
        variants=variants,
        out_path=os.path.join(HERE, "results.md"),
        main_variant="mult: value-aware xGT (tau=1), alpha=1 delta=1",
        notes="AttackValue = xGT * (1 + alpha*PR_norm)/(1+alpha) * (1 + delta*PPS_norm)/(1+delta);  h = round(-log(AttackValue)/gamma).",
    )
    h, raw = build_multiplicative(B, G, 1.0, 1.0, 1.0)("Bucharest")
    print_table(h, "Bucharest", raw)
