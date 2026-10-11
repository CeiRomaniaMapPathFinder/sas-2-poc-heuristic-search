# Performance — Pitch control (goal influence)

Full tables: `results.md`.

| variant | pair checks | mean Spearman (20 goals) | weighted inversion penalty | A* optimal (380 pairs) | mean nodes expanded |
|---|---|---|---|---|---|
| lambda=0.01 alpha=1.0 | 5/8 | 0.902 | 0.050 | 100 % | 7.56 |
| lambda=0.01 alpha=0.8 | 7/8 | 0.985 | 0.006 | 100 % | 5.02 |
| lambda=0.01 alpha=0.5 | 8/8 | 0.992 | 0.003 | 80.5 % | 4.74 |
| lambda=0.02 alpha=1.0 | 8/8 | 0.997 | 0.000 | 100 % | 4.99 |
| **lambda=0.02 alpha=0.8** | **8/8** | **0.997** | **0.000** | **100 %** | **4.94** |
| lambda=0.005 alpha=0.5 | 7/8 | 0.972 | 0.013 | 97.6 % | 4.93 |
| baseline: straight-line | 6/8 | 0.848 | 0.083 | 100 % | 6.81 |

**Test 1.** `h(goal) = 0`, unique minimum.

**Test 2.** With `lambda = 0.01` the hub bonus is too strong: Pitesti (three roads) gets h = 100 < Giurgiu 112 (one road) although Giurgiu is closer (fails Giurgiu < Pitesti). At `lambda = 0.02` the roads fade faster, side roads matter less, and all 8 checks pass (Giurgiu 101 < Pitesti 111; Arad 148 < Oradea 158).

**Test 3–5.** `lambda=0.02 alpha=0.8`: Spearman 0.994 (Bucharest), 1.000 (Sibiu — zero inversions); 3 small inversions for Bucharest (worst: Neamt 448 vs Arad 431, gap 12). Every city is within 3 ranks of its true rank.

**Test 6.** 380/380 optimal, 4.94 nodes expanded — the best A* numbers of any method in the archive (UCS 11, straight-line 6.8, ring 5.6). h sits between 0.98× and 1.12× of the true remaining cost, so it guides strongly without becoming greedy.

**Sensitivity.** `alpha` is the knob that trades guidance for optimality: at `alpha = 0.5` (lambda 0.01) h inflates by the per-pass penalty (−ln 0.5 / 0.01 = 69 per hop) and A* drops to 80 % optimal; at `alpha = 1` the hub bonus dominates and ranking degrades. `lambda = 0.02, alpha = 0.8` is the sweet spot on this map.

## Verdict

**Runner-up, and the best raw numbers in the whole set.** Two parameters, a five-line iteration, perfect A* behaviour. It lost on the model rather than the measurements: there is no pass choice and no completion probability here, only influence that fades, and the brief itself notes this family "resembles diffusion / random-walk ideas". Unrolled, `-ln(I)/lambda` is a soft minimum over walks of (road cost + a per-hop penalty) — a smoothed shortest path. The full argument is in `../../docs/05_why_xgt_won.md`. If search performance mattered more than the analogy this would be the pick, and the Java port is ready for it.
