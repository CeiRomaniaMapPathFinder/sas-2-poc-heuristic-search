"""
The heuristic we kept: full evaluation against the baselines, plus export of the
20-goal integer table in the three formats the backend can consume.

    python experiment.py
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
sys.path.insert(0, HERE)

from run_method import evaluate, print_table            # noqa: E402
from export_table import export                          # noqa: E402
from romania_graph import GRAPH                          # noqa: E402
from football_math import pass_preference, completion_probs  # noqa: E402
from method import heuristic, values, BETA, GAMMA, TAU       # noqa: E402

if __name__ == "__main__":
    b = heuristic()
    evaluate(
        method_name="xGT, value-aware passer (beta=0.02, gamma=0.01, tau=1.5) - the heuristic we kept",
        variants={"xGT (final)": b},
        out_path=os.path.join(HERE, "results.md"),
        notes="h(u) = floor(-ln(xGT(u))/gamma + 0.5); the model is core/xgt.py, the parameters are pinned in final/method.py.",
        detail_goals=("Bucharest", "Sibiu", "Neamt"),
    )
    table = export(b, os.path.join(HERE, "exports"), "xGT with a value-aware passer, beta=0.02 gamma=0.01 tau=1.5",
                   "h(city) = floor(-ln(xGT(city))/0.01 + 0.5); integer road-cost units; h(goal)=0")
    print("exported exports/heuristic_table.json, exports/heuristicTable.ts, exports/HeuristicTable.java")

    # --- the worked example used in concept.md (goal = Bucharest) ---
    goal = "Bucharest"
    x = values(goal)
    q, C = pass_preference(BETA), completion_probs(GAMMA)
    print(f"\nWorked example, goal = {goal}")
    for u in ("Giurgiu", "Pitesti", "Urziceni"):
        print(f"  {u}:")
        pref = {v: q[u][v] * x[v] ** TAU for v in GRAPH[u]}
        s = sum(pref.values())
        for v in GRAPH[u]:
            print(f"    -> {v:15s} w={GRAPH[u][v]:3d}  exp(-beta w)={q[u][v]:.4f}  xGT(v)={x[v]:.4f}  "
                  f"P={pref[v]/s:.4f}  C={C[u][v]:.4f}  P*C*xGT(v)={pref[v]/s*C[u][v]*x[v]:.4f}")
        print(f"    xGT({u}) = {x[u]:.4f}   h = -ln({x[u]:.4f})/{GAMMA} = {-math.log(x[u])/GAMMA:.1f}  -> {table[goal][u]}")
    h, raw = b(goal)
    print_table(h, goal, raw)
