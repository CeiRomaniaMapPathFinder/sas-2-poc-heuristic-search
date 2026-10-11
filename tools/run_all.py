"""Re-run the self-test, every experiment, the final model and the Java cross-check.

    python tools/run_all.py
"""
import os
import subprocess
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
EXPERIMENTS = ["01_expected_goal_threat", "02_progressive_passing", "03_press_resistance", "04_route_redundancy",
               "05_packing_line_breaking", "06_pitch_control", "07_goal_centrality", "08_combined_model",
               "09_expected_time_to_goal", "10_turnover_risk"]

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    subprocess.run([sys.executable, "selftest.py"], cwd=os.path.join(ROOT, "core"), check=True)
    for f in EXPERIMENTS:
        print(f"=== experiments/{f}")
        subprocess.run([sys.executable, "experiment.py"], cwd=os.path.join(ROOT, "experiments", f),
                       check=True, stdout=subprocess.DEVNULL)
    print("=== final")
    subprocess.run([sys.executable, "experiment.py"], cwd=os.path.join(ROOT, "final"),
                   check=True, stdout=subprocess.DEVNULL)
    subprocess.run([sys.executable, "crosscheck.py"], cwd=here, check=True)
    print("all done")
