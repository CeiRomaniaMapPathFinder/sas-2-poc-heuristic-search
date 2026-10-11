# Performance — Combined model (threat x support x progression)

Full tables: `results.md`.

| variant | pair checks | mean Spearman (20 goals) | weighted inversion penalty | A* optimal (380 pairs) | mean nodes expanded |
|---|---|---|---|---|---|
| mult, doc xGT (tau=0), alpha=delta=0 (= xGT with the cost-only passer) | 7/8 | 0.990 | 0.002 | 75.5 % | 4.72 |
| mult, doc xGT (tau=0), alpha=1 delta=1 | 7/8 | 0.990 | 0.002 | 75.5 % | 4.72 |
| mult, doc xGT (tau=0), alpha=3 delta=1 | 7/8 | 0.990 | 0.002 | 75.5 % | 4.72 |
| mult, value-aware xGT (tau=1), alpha=delta=0 (= xGT alone) | 8/8 | 0.997 | 0.000 | 94.2 % | 4.92 |
| mult, value-aware xGT (tau=1), alpha=1 delta=1 | 8/8 | 0.996 | 0.000 | 83.2 % | 4.79 |
| mult, value-aware xGT (tau=1), alpha=2 delta=0.5 | 8/8 | 0.997 | 0.000 | 87.6 % | 4.83 |
| mult, value-aware xGT (tau=1), alpha=0.5 delta=2 | 7/8 | 0.995 | 0.001 | 82.9 % | 4.79 |
| sum, tau=1, a=0.6 b=0.2 c=0.2 | 8/8 | 0.991 | 0.001 | 93.2 % | 6.19 |
| sum, tau=1, a=b=c=1/3 | 7/8 | 0.988 | 0.001 | 90.5 % | 6.16 |

**Tests 1–5.** All fine: `h(goal) = 0` unique (after the `(1+alpha)` normalisation fix — see concept.md), 8/8 pair checks with the value-aware xGT, Spearman 0.994–0.997, 2–3 tiny inversions per goal.

**Test 6 — the important finding.** Adding press resistance and progressive passing on top of xGT does **not** improve A* and in the multiplicative form makes it worse (94.2 % → 83–88 %). Reason: both extra factors are ≤ 1, so they can only push AttackValue *down* and h *up*. xGT already sits 10–20 % above the true remaining cost; the mark-down adds another 10–30 %, and A* gets greedier (it prefers Sibiu→Fagaras→Bucharest over Rimnicu→Pitesti on long routes, overshoot ≈ 30). The ranking stays excellent — this is purely the scale-versus-concept error the design guide describes.

On the doc's own xGT (tau=0) the extra factors change nothing measurable: PR and PPS are so strongly correlated with xGT that the product just rescales it.

The weighted-sum version is better calibrated (93 % optimal with a=0.6) but expands 6.2 nodes instead of 4.8 — it is closer to UCS because the road-scaled `1 − Score` is flat across most of the map.

## Verdict

**Conceptually the richest model, but on this map the extras do not pay.** The three ingredients agree with each other so strongly on a 20-city graph that combining them only changes the scale, and the scale change is in the wrong direction for A*. Recommendation: keep the combined model as the *explanation* of what the heuristic measures (threat, support, progression are all in xGT implicitly), but ship xGT alone (`../../final/`). If a combined form is required for the write-up, use `alpha=2, delta=0.5` on the value-aware xGT (8/8, 87.6 % optimal).
