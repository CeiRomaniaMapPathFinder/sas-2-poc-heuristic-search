"""
The heuristic this project settled on: xGT with a value-aware passer.

    beta  = 0.02   how strongly the passer prefers short roads
    gamma = 0.01   how fast pass-completion probability falls with road cost
    tau   = 1.5    how strongly the passer prefers receivers already in a threatening spot

    C(u,v)    = exp(-gamma * w(u,v))                       pass completed
    P(u->v)   ~ exp(-beta * w(u,v)) * xGT(v)^tau            pass chosen
    xGT(goal) = 1
    xGT(u)    = sum over v of  P(u->v) * C(u,v) * xGT(v)    iterate until it stops moving

    h(u) = floor( -ln(xGT(u)) / gamma + 0.5 )               integer, road-cost units, h(goal) = 0

The formula itself lives in core/xgt.py; this file only pins the parameters, so
there is exactly one place where the chosen settings are written down.
See ../docs/06_xgt_explained.md for the walk-through and ../docs/05_why_xgt_won.md
for why these three numbers and not others.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "core"))

from xgt import build, xgt  # noqa: E402

BETA, GAMMA, TAU = 0.02, 0.01, 1.5


def heuristic():
    """goal -> (integer h table, raw -ln(xGT)/gamma table)."""
    return build(BETA, GAMMA, TAU)


def values(goal):
    """Raw xGT values in 0..1 (goal = 1), for the explanation tables."""
    return xgt(goal, BETA, GAMMA, TAU)
