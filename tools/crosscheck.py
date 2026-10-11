"""
Runs the Java ports (tools/java/CrossCheck.java) and checks that every integer
table equals the Python one, city by city.  This is what lets the backend trust
the Java version: the two implementations agree on every city and every goal.

    python tools/crosscheck.py      (needs `java` on PATH; Java 22+ for the multi-file launcher)
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, os.path.join(ROOT, "core"))


from romania_graph import CITIES, MEAN_EDGE     # noqa: E402
from xgt import build             # noqa: E402
import importlib.util                           # noqa: E402


def load(sub):
    """Import experiments/<sub>/method.py under a unique name (they all share the file name)."""
    spec = importlib.util.spec_from_file_location(sub + "_method", os.path.join(ROOT, "experiments", sub, "method.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


pps_m = load("02_progressive_passing")
pr_m = load("03_press_resistance")
pitch_m = load("06_pitch_control")
pr_rank_m = load("07_goal_centrality")
comb_m = load("08_combined_model")
et_m = load("09_expected_time_to_goal")
to_m = load("10_turnover_risk")

PY = {
    "xgt tau=0 b0.01 g0.01": build(0.01, 0.01, 0.0),
    "xgt tau=1 b0.01 g0.01": build(0.01, 0.01, 1.0),
    "xgt tau=1.5 b0.02 g0.01 (final)": build(0.02, 0.01, 1.5),
    "pps b0.01 g0.01": pps_m.build(0.01, 0.01, "log"),
    "pr_sum b0.01 g0.01": pr_m.build_pr_sum(0.01, 0.01, "log"),
    "pitch l0.02 a0.8": pitch_m.build(0.02, 0.8),
    "pagerank l0.01 d0.85": pr_rank_m.build(0.01, 0.85),
    "combined t1 a1 d1": comb_m.build_multiplicative(0.01, 0.01, 1.0, 1.0, 1.0),
    "expected_time b0.01 k0.005": et_m.build(0.01, 0.005),
    "turnover b0.01 g0.005 k0.005": to_m.build(0.01, 0.005, MEAN_EDGE, 0.005),
}

GOALS = ["Bucharest", "Sibiu", "Neamt", "Timisoara"]

if __name__ == "__main__":
    out = subprocess.run(["java", "CrossCheck.java"] + GOALS, cwd=os.path.join(HERE, "java"),
                         capture_output=True, text=True, check=True)
    java = json.loads(out.stdout.strip().splitlines()[-1])
    bad = 0
    for name, builder in PY.items():
        for goal in GOALS:
            py = builder(goal)
            py = py[0] if isinstance(py, tuple) else py
            jt = java[name][goal]
            diffs = [(c, py[c], jt[c]) for c in CITIES if py[c] != jt[c]]
            status = "OK " if not diffs else "DIFF"
            bad += len(diffs)
            print(f"{status} {name:40s} goal={goal:10s}" + ("" if not diffs else f"  {diffs}"))
    print("\nALL TABLES IDENTICAL" if bad == 0 else f"\n{bad} city values differ")
    sys.exit(0 if bad == 0 else 1)
