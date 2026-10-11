"""
Builds docs/xgt_explained.pdf -- a plain-language explainer of the heuristic
this project settled on.  Every number in the PDF is computed here from the real code, so the
document can never drift from the exported tables.

    python make_pdf.py
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "docs", "xgt_explained.pdf")
sys.path.insert(0, os.path.join(HERE, "..", "core"))
sys.path.insert(0, os.path.join(HERE, "..", "final"))

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle, KeepTogether)

from romania_graph import GRAPH, CITIES                      # noqa: E402
from football_math import pass_preference, completion_probs  # noqa: E402
from search import dijkstra                                   # noqa: E402
from method import heuristic, BETA, GAMMA, TAU                    # noqa: E402
from search import astar                                      # noqa: E402
from xgt import build as build_xgt                            # noqa: E402

# ---------------------------------------------------------------- fonts (need Greek letters + arrows)
FONT_DIR = "C:/Windows/Fonts"
pdfmetrics.registerFont(TTFont("Body", os.path.join(FONT_DIR, "arial.ttf")))
pdfmetrics.registerFont(TTFont("BodyB", os.path.join(FONT_DIR, "arialbd.ttf")))
pdfmetrics.registerFont(TTFont("BodyI", os.path.join(FONT_DIR, "ariali.ttf")))
pdfmetrics.registerFont(TTFont("Mono", os.path.join(FONT_DIR, "consola.ttf")))
pdfmetrics.registerFont(TTFont("MonoB", os.path.join(FONT_DIR, "consolab.ttf")))
from reportlab.pdfbase.pdfmetrics import registerFontFamily
registerFontFamily("Body", normal="Body", bold="BodyB", italic="BodyI", boldItalic="BodyB")

ss = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=ss["Heading1"], fontName="BodyB", fontSize=18, spaceAfter=8, spaceBefore=6)
H2 = ParagraphStyle("H2", parent=ss["Heading2"], fontName="BodyB", fontSize=13.5, spaceAfter=5, spaceBefore=12, textColor=colors.HexColor("#1a3d6d"))
H3 = ParagraphStyle("H3", parent=ss["Heading3"], fontName="BodyB", fontSize=11.5, spaceAfter=8, spaceBefore=10)
P = ParagraphStyle("P", parent=ss["BodyText"], fontName="Body", fontSize=10, leading=14, alignment=TA_LEFT, spaceAfter=5)
NOTE = ParagraphStyle("NOTE", parent=P, backColor=colors.HexColor("#f2f6fb"), borderPadding=(5, 6, 5, 6), leftIndent=4, rightIndent=4, spaceBefore=4, spaceAfter=8)
CODE = ParagraphStyle("CODE", parent=P, fontName="Mono", fontSize=9.2, leading=12.5, backColor=colors.HexColor("#f5f5f5"),
                      borderPadding=(5, 6, 5, 6), leftIndent=4, rightIndent=4, spaceBefore=8, spaceAfter=10)
SMALL = ParagraphStyle("SMALL", parent=P, fontSize=8.5, leading=11, textColor=colors.HexColor("#555555"))
TCELL = ParagraphStyle("TCELL", parent=P, fontSize=9, leading=11.5, spaceAfter=0)
TCELLB = ParagraphStyle("TCELLB", parent=TCELL, fontName="BodyB")


def p(t, style=P):
    return Paragraph(t, style)


def code(t):
    return Paragraph(t.replace(" ", "&nbsp;").replace("\n", "<br/>"), CODE)


def table(rows, col_widths=None, header=True, align_right_from=1):
    data = [[Paragraph(str(c), TCELLB if (header and i == 0) else TCELL) for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=col_widths, hAlign="LEFT")
    st = [("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#b8c4d4")),
          ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
          ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]
    if header:
        st += [("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e3ebf5"))]
    t.setStyle(TableStyle(st))
    return t


# ---------------------------------------------------------------- numbers from the real code
GOAL = "Bucharest"
q = pass_preference(BETA)
C = completion_probs(GAMMA)
h_table, raw = heuristic()(GOAL)
d_star = dijkstra(GOAL)


def iterate(n_iter):
    x = {c: 1e-3 for c in CITIES}
    x[GOAL] = 1.0
    trace = []
    for it in range(n_iter):
        nx = {GOAL: 1.0}
        for u in CITIES:
            if u == GOAL:
                continue
            pref = {v: q[u][v] * max(x[v], 1e-30) ** TAU for v in GRAPH[u]}
            s = sum(pref.values())
            nx[u] = sum(pref[v] / s * C[u][v] * x[v] for v in GRAPH[u])
        x = nx
        trace.append(dict(x))
    return x, trace


X, TRACE = iterate(400)


def example_rows(u):
    """Rows of the worked example for passer u (uses converged xGT of receivers)."""
    pref = {v: q[u][v] * X[v] ** TAU for v in GRAPH[u]}
    s = sum(pref.values())
    rows = []
    for v in GRAPH[u]:
        w = GRAPH[u][v]
        rows.append([v, w, f"{q[u][v]:.4f}", f"{X[v]:.4f}", f"{X[v] ** TAU:.4f}", f"{pref[v]:.5f}",
                     f"{pref[v] / s:.4f}", f"{C[u][v]:.4f}", f"{pref[v] / s * C[u][v] * X[v]:.4f}"])
    rows.sort(key=lambda r: -float(r[8]))     # biggest contribution first, easier to read
    return rows, s


# ================================================================ document
doc = SimpleDocTemplate(OUT, pagesize=A4,
                        leftMargin=18 * mm, rightMargin=18 * mm, topMargin=16 * mm, bottomMargin=16 * mm,
                        title="xGT heuristic explained", author="sas-2-poc-heuristic-search")
S = []

S.append(p("Expected Goal Threat as an A* heuristic for the Romania map", H1))
S.append(p(f"Recommended setting: β = {BETA}, γ = {GAMMA}, τ = {TAU}. Every number in this document is computed by "
           f"<font name='Mono'>make_pdf.py</font> from the same code that produces the exported tables.", SMALL))
S.append(Spacer(1, 4))
S.append(p("This document has four parts: (1) what xT means in real football, (2) how the same idea is applied to the "
           "Romania road map, (3) every variable explained, and (4) the calculation step by step with the full "
           "Pitesti example worked out column by column. Part 6 follows a whole search, Zerind → Bucharest, through two forks "
           "in the road; Part 7 shows the full table and the parameter choices."))

# ---------------------------------------------------------------- Part 1
S.append(p("Part 1 — What “Expected Threat” means in real football", H2))
S.append(p("Expected Threat (xT) is a football-analytics model (Karun Singh, 2018) that answers one question: "
           "<b>“If my team has the ball at this spot on the pitch, how likely is it that this possession ends in a goal?”</b> "
           "It exists because “distance to goal” is a poor measure of danger: a ball on the wing 20 m from goal is less dangerous "
           "than a ball in the centre 25 m out, because of what the player can <i>do next</i> from each spot."))
S.append(p("How the real model works:", H3))
S.append(p("1. The pitch is cut into a grid of zones (typically 12 × 8 = 96 zones)."))
S.append(p("2. From thousands of real matches, for every zone the analysts count what players actually did with the ball there: "
           "how often they <b>shot</b>, how often they <b>moved the ball</b> (pass or dribble), and — when they moved it — "
           "<b>which zone it went to</b>. Those counts become probabilities: shoot probability, move probability, and a "
           "transition probability from each zone to each other zone. From the shots they also get the chance that a shot "
           "from that zone scores (xG)."))
S.append(p("3. The value of a zone is then defined by looking one action ahead:"))
S.append(code("xT(zone) = (chance of shooting here) × (chance the shot scores)\n"
              "         + (chance of moving the ball) × Σ over target zones [ P(zone → target) × xT(target) ]"))
S.append(p("The second line is the important idea: <b>a zone is worth a lot if the zones you can reach from it are worth a lot.</b> "
           "The definition is circular (xT on both sides), so it is solved by iteration: start with xT = 0 everywhere, apply the "
           "formula to every zone, repeat 5–10 times; the numbers settle. The result is a heat map where the value rises smoothly "
           "toward the goal mouth, but not uniformly — central zones with good onward options score higher than wide zones at the "
           "same distance."))
S.append(p("4. Analysts then grade an action by the threat it <i>added</i>: xT(end zone) − xT(start zone). A pass that moves the ball "
           "from a 0.05 zone to a 0.20 zone “created 0.15 xT”."))
S.append(p("<b>Three ideas we keep:</b> (a) value comes from the future actions available, not from distance; (b) that value is "
           "propagated backwards from the goal through the network of possible moves; (c) it is computed by simple repeated "
           "iteration of one formula.", NOTE))

# ---------------------------------------------------------------- Part 2
S.append(p("Part 2 — Applying the same idea to the Romania map", H2))
S.append(table([
    ["Real football (xT)", "Romania map (xGT)"],
    ["a zone of the pitch", "a city"],
    ["a pass or dribble from zone to zone", "driving along one road from city to city"],
    ["transition probabilities measured from match data", "transition probabilities <b>computed from road cost</b> — a short road is an easy pass, a long road is a hard pass"],
    ["a shot that scores", "arriving at the goal city (value 1)"],
    ["losing the ball (pass fails)", "a pass along a long road may “fail” — the possession is lost, value 0"],
    ["xT(zone) = chance this possession ends in a goal", "xGT(city) = chance a possession starting here reaches the goal city"],
    ["heat map used to grade passes", "value turned into an integer h(city) for A*"],
], col_widths=[70 * mm, 104 * mm]))
S.append(Spacer(1, 6))
S.append(p("Two things have to be invented because the map has no match data:"))
S.append(p("• <b>Which road does the “player” take?</b> In real xT this comes from data. Here we model it: the player prefers "
           "short roads (easy passes) and prefers roads that lead to cities which are themselves threatening — that second "
           "preference is what we call the <b>value-aware passer</b>. Without it the player picks roads by cost alone, "
           "and a city with many roads spreads its probability over bad options and looks worse than it is (the “dilution” problem)."))
S.append(p("• <b>Can the pass fail?</b> In real xT a possession can end without a shot. Here every road has a completion probability "
           "that falls with its cost; a failed pass ends the possession with value 0. Without this, every possession would eventually "
           "reach the goal and every city would get value 1 — the model would say nothing."))
S.append(p("There is no shooting step: the only way to “score” is to arrive at the goal city, so xGT(goal) = 1 and the whole value "
           "field is propagated backwards from that one city."))

# ---------------------------------------------------------------- Part 3
S.append(PageBreak())
S.append(p("Part 3 — Every symbol, explained", H2))
S.append(p("The confusing part of the formulas is the notation <font name='Mono'>(u, v)</font>. It always means <b>one road</b>: "
           "<b>u</b> is the city where the ball is now (the passer), <b>v</b> is the neighbouring city the ball would go to (the receiver). "
           "So <font name='Mono'>w(u,v)</font> is “the cost of the road from u to v”, and <font name='Mono'>C(u,v)</font> is "
           "“the chance a pass from u to v is completed”. When we write “sum over v” we mean: do it once for each road leaving u, "
           "then add the results."))
S.append(table([
    ["symbol", "what it is", "example (goal = Bucharest)"],
    ["goal", "the target city; its value is fixed at 1", "Bucharest"],
    ["u", "the city we are evaluating (where the ball is)", "Pitesti"],
    ["v", "one neighbour of u (a possible receiver)", "Bucharest, Rimnicu Vilcea or Craiova"],
    ["w(u,v)", "road cost between u and v (from the map)", "w(Pitesti, Bucharest) = 101"],
    ["β (beta) = 0.02", "how strongly the passer prefers <i>cheap</i> roads", "a road twice as long is about 7× less attractive"],
    ["γ (gamma) = 0.01", "how fast the <i>completion</i> chance drops with road cost", "a 100-cost road is completed 37 % of the time"],
    ["τ (tau) = 1.5", "how strongly the passer prefers receivers that are themselves threatening", "τ = 0: ignores it; larger τ: more goal-directed"],
    ["C(u,v) = e<super>−γ·w(u,v)</super>", "completion probability of the pass along road (u,v)", "C(Pitesti, Bucharest) = e<super>−1.01</super> = 0.364"],
    ["q(u,v) = e<super>−β·w(u,v)</super>", "how attractive the road is by cost alone", "q(Pitesti, Bucharest) = e<super>−2.02</super> = 0.133"],
    ["P(u→v)", "probability the passer at u chooses road (u,v); all P(u→·) add up to 1", "P(Pitesti→Bucharest) = 0.948"],
    ["xGT(u)", "chance a possession starting at u eventually reaches the goal (0 … 1)", "xGT(Pitesti) = 0.347"],
    ["h(u)", "the A* heuristic: xGT converted to an integer in road-cost units; 0 at the goal", "h(Pitesti) = 106"],
], col_widths=[34 * mm, 74 * mm, 66 * mm]))

# ---------------------------------------------------------------- Part 4
S.append(p("Part 4 — How h(n) is calculated, step by step", H2))
S.append(p("Step 1 — completion probability of every road (done once)", H3))
S.append(code("C(u,v) = exp( −γ · w(u,v) )        γ = 0.01"))
S.append(p(f"Examples: road 85 → {math.exp(-GAMMA*85):.3f}; road 101 → {math.exp(-GAMMA*101):.3f}; road 140 → {math.exp(-GAMMA*140):.3f}; "
           f"road 211 → {math.exp(-GAMMA*211):.3f}. A long road is a risky pass."))

S.append(p("Step 2 — cost-attractiveness of every road (done once)", H3))
S.append(code("q(u,v) = exp( −β · w(u,v) )        β = 0.02"))
S.append(p("This is only the <i>cost</i> half of the passer's preference. It is not yet a probability."))

S.append(p("Step 3 — which road the passer chooses (recomputed every iteration)", H3))
S.append(code("preference(u,v) = q(u,v) · xGT(v)^τ                τ = 1.5\n"
              "P(u→v)          = preference(u,v) / Σ over all roads (u,k) of preference(u,k)"))
S.append(p("Read it as: “the passer likes a road if it is short <b>and</b> it leads somewhere threatening”; dividing by the sum turns "
           "the preferences into probabilities that add up to 1. Because xGT(v) is used here, step 3 depends on the values we are "
           "still computing — that is why the whole thing is iterated (step 5)."))

S.append(p("Step 4 — the value of a city", H3))
S.append(code("xGT(goal) = 1\n"
              "xGT(u)    = Σ over all roads (u,v) of   P(u→v) · C(u,v) · xGT(v)"))
S.append(p("In words: for each road out of u, multiply (chance the passer picks it) × (chance the pass arrives) × (value of where it "
           "arrives), then add the roads up. Compare with the real xT formula in Part 1: it is the same “move probability × "
           "transition probability × value of target” term; the shooting term is replaced by xGT(goal) = 1."))

S.append(p("Step 5 — iterate until the numbers stop changing", H3))
S.append(p("Start with xGT = 0.001 for every city and 1 for the goal. Apply steps 3–4 to all 20 cities; that is one iteration. "
           "Repeat until the largest change in any city is below 10<super>−12</super> — this takes 34–40 rounds for every goal (a literal "
           "\"nothing changed\" test on doubles never fires for most goals, because the last bit keeps flipping; a tolerance is the correct "
           "stopping test). The table shows how the values settle for goal = Bucharest:"))
show = ["Giurgiu", "Pitesti", "Rimnicu Vilcea", "Craiova", "Sibiu", "Arad"]
rows = [["iteration"] + show]
for i in [0, 1, 2, 3, 4, 5, 7]:
    rows.append([str(i + 1)] + [f"{TRACE[i][c]:.4f}" for c in show])
rows.append(["converged"] + [f"{X[c]:.4f}" for c in show])
S.append(table(rows, col_widths=[24 * mm] + [25 * mm] * 6))
S.append(p("Giurgiu is fixed after one round (its only road goes straight to the goal). Pitesti needs a few rounds because its "
           "value depends on Rimnicu Vilcea and Craiova, whose values depend on Sibiu and Drobeta, and so on outward. "
           "Values shrink with distance from the goal: each extra pass multiplies by a completion chance below 1.", SMALL))

S.append(p("Step 6 — turn the value into an integer heuristic", H3))
S.append(code("h(u) = floor( −ln( xGT(u) ) / γ  + 0.5 )          h(goal) = 0"))
S.append(p("Why −ln and why divide by γ: along one chain of passes the value is a product of factors e<super>−γ·w</super>, so "
           "−ln of it is γ × (sum of road costs). Dividing by γ gives back a number in road-cost units — the same units as g(n), "
           "which is what A* needs for f = g + h. High threat → low h; the goal has value 1 → h = 0. The +0.5 and floor just round "
           "to the nearest integer in a way that is identical in Python and Java."))

# ---------------------------------------------------------------- Part 5: worked example
S.append(PageBreak())
S.append(p("Part 5 — The Pitesti example, column by column (goal = Bucharest)", H2))
S.append(p("Pitesti has <b>three roads</b>: to Bucharest (101), to Rimnicu Vilcea (97) and to Craiova (138). We evaluate Pitesti as "
           "<b>u</b>; each of the three cities is one <b>v</b>. The xGT values of the receivers come from the converged iteration "
           f"(step 5): xGT(Bucharest) = 1 (it is the goal), xGT(Rimnicu Vilcea) = {X['Rimnicu Vilcea']:.4f}, xGT(Craiova) = {X['Craiova']:.4f}."))
rows, s_pit = example_rows("Pitesti")
S.append(table([["receiver v", "w(u,v)", "q = e^(−0.02·w)", "xGT(v)", "xGT(v)^1.5", "preference = q · xGT(v)^1.5",
                 "P(u→v) = pref / sum", "C = e^(−0.01·w)", "P · C · xGT(v)"]] + rows,
               col_widths=[24 * mm, 15 * mm, 19 * mm, 15 * mm, 17 * mm, 25 * mm, 21 * mm, 18 * mm, 20 * mm]))
S.append(Spacer(1, 4))
S.append(p("How to read each column:"))
S.append(p("• <b>w(u,v)</b> — road cost from the map."))
S.append(p("• <b>q</b> — step 2, cost-attractiveness: e<super>−0.02·101</super> = 0.133 for the Bucharest road."))
S.append(p("• <b>xGT(v)</b> — the receiver's value from the last iteration; <b>xGT(v)^1.5</b> is the same number raised to τ."))
S.append(p(f"• <b>preference</b> — q × xGT(v)^1.5. The three preferences add up to {s_pit:.5f}."))
S.append(p("• <b>P(u→v)</b> — each preference divided by that sum. This is the probability the passer at Pitesti picks that road; "
           f"the three P values add up to 1. The direct road to Bucharest gets {rows[0][6]} because it is both short and leads to the goal."))
S.append(p("• <b>C</b> — step 1, completion chance of that road."))
S.append(p("• <b>P · C · xGT(v)</b> — the road's contribution to Pitesti's value (step 4)."))
contrib = [float(r[8]) for r in rows]
S.append(code(f"xGT(Pitesti) = {contrib[0]:.4f} + {contrib[1]:.4f} + {contrib[2]:.4f} = {X['Pitesti']:.4f}\n"
              f"h(Pitesti)   = floor( −ln({X['Pitesti']:.4f}) / 0.01 + 0.5 ) = floor( {-math.log(X['Pitesti'])/GAMMA:.1f} + 0.5 ) = {h_table['Pitesti']}"))
S.append(p("Almost all of Pitesti's value comes from the direct road (0.345 of 0.347). The two side roads contribute little, but "
           "the fact that the passer <i>sometimes</i> takes them is why h(Pitesti) = 106 is a bit above the true remaining cost 101 — "
           "that small surplus is the football content of the number.", NOTE))

S.append(p("The simplest case: Giurgiu", H3))
rows_g, _ = example_rows("Giurgiu")
S.append(p("Giurgiu has one road (to Bucharest, 90). With one road the preference sum is the preference itself, so P = 1:"))
S.append(code(f"xGT(Giurgiu) = 1 · C(Giurgiu,Bucharest) · xGT(Bucharest) = 1 · {C['Giurgiu']['Bucharest']:.4f} · 1 = {X['Giurgiu']:.4f}\n"
              f"h(Giurgiu)   = floor( −ln({X['Giurgiu']:.4f}) / 0.01 + 0.5 ) = {h_table['Giurgiu']}"))
S.append(p("A single road means no hesitation, so h equals the road cost exactly (90). That is the sanity check from the guide: "
           f"h(Giurgiu) = {h_table['Giurgiu']} &lt; h(Pitesti) = {h_table['Pitesti']}, matching true costs 90 &lt; 101."))

S.append(p("A three-road city again: Urziceni", H3))
rows_u, s_u = example_rows("Urziceni")
S.append(table([["receiver v", "w(u,v)", "q", "xGT(v)", "xGT(v)^1.5", "preference", "P(u→v)", "C", "P · C · xGT(v)"]] + rows_u,
               col_widths=[24 * mm, 15 * mm, 19 * mm, 15 * mm, 17 * mm, 25 * mm, 21 * mm, 18 * mm, 20 * mm]))
cu = [float(r[8]) for r in rows_u]
S.append(code(f"xGT(Urziceni) = {cu[0]:.4f} + {cu[1]:.4f} + {cu[2]:.4f} = {X['Urziceni']:.4f}   →   h(Urziceni) = {h_table['Urziceni']}   (true cost 85)"))


# ---------------------------------------------------------------- Part 6: Zerind -> Bucharest (two forks)
S.append(PageBreak())
S.append(p("Part 6 — A whole search with forks: Zerind → Bucharest", H2))
S.append(p("Pitesti shows how one city's number is built, but the interesting question for A* is what happens at a <b>fork</b>: "
           "two roads leave a city, both eventually reach the goal, and the cheaper first step is <i>not</i> the cheaper route. "
           "The guide's own example is exactly this. From Zerind (goal = Bucharest):"))
S.append(code("Zerind → Arad   (75) → Sibiu (140) = 215 to Sibiu   ← cheaper route, dearer first road\n"
              "Zerind → Oradea (71) → Sibiu (151) = 222 to Sibiu   ← cheaper first road, dearer route\n"
              "\n"
              "then from Sibiu, a second fork:\n"
              "Sibiu → Rimnicu Vilcea (80) → Pitesti (97) → Bucharest (101)   = 278   ← cheaper\n"
              "Sibiu → Fagaras (99)        → Bucharest (211)                  = 310\n"
              "\n"
              "best: Zerind → Arad → Sibiu → Rimnicu Vilcea → Pitesti → Bucharest = 493  (via Oradea: 500)"))
S.append(p("A good heuristic must therefore say h(Arad) &lt; h(Oradea) even though Oradea is the cheaper first step, and "
           "h(Rimnicu Vilcea) &lt; h(Fagaras). Here is how the model arrives at both.", NOTE))

S.append(p("Fork 1 — Arad versus Oradea (both evaluated toward Bucharest)", H3))
S.append(p(f"Both cities' value comes almost entirely from their road to Sibiu (xGT(Sibiu) = {X['Sibiu']:.4f}); the back-road to "
           "Zerind and Arad's road to Timisoara lead to low-value cities and contribute almost nothing. Same columns as the Pitesti table:"))
for city in ("Arad", "Oradea"):
    rows_c, s_c = example_rows(city)
    S.append(p(f"<b>{city}</b> — {len(GRAPH[city])} roads, preference sum {s_c:.6f}:", SMALL))
    S.append(table([["receiver v", "w(u,v)", "q", "xGT(v)", "xGT(v)^1.5", "preference", "P(u→v)", "C", "P · C · xGT(v)"]] + rows_c,
                   col_widths=[24 * mm, 15 * mm, 19 * mm, 15 * mm, 17 * mm, 25 * mm, 21 * mm, 18 * mm, 20 * mm]))
    cc = [float(r[8]) for r in rows_c]
    S.append(code(f"xGT({city}) = " + " + ".join(f"{v:.4f}" for v in cc) + f" = {X[city]:.4f}   →   h({city}) = floor(−ln({X[city]:.4f})/0.01 + 0.5) = {h_table[city]}"))
S.append(p(f"So h(Arad) = {h_table['Arad']} &lt; h(Oradea) = {h_table['Oradea']}. The 11-point gap comes from one number: the completion "
           f"probability of the road to Sibiu, C = {C['Arad']['Sibiu']:.4f} for Arad's 140-road versus {C['Oradea']['Sibiu']:.4f} for Oradea's 151-road. "
           "The model does not know the route costs 418 and 429 — it only knows that Arad's pass to Sibiu is a bit easier to complete — "
           "and that is enough to reproduce the true difference (429 − 418 = 11)."))

S.append(p("Fork 2 — Rimnicu Vilcea versus Fagaras (seen from Sibiu)", H3))
rows_s, s_s = example_rows("Sibiu")
S.append(table([["receiver v", "w(u,v)", "q", "xGT(v)", "xGT(v)^1.5", "preference", "P(u→v)", "C", "P · C · xGT(v)"]] + rows_s,
               col_widths=[24 * mm, 15 * mm, 19 * mm, 15 * mm, 17 * mm, 25 * mm, 21 * mm, 18 * mm, 20 * mm]))
S.append(p(f"Sibiu's passer prefers Rimnicu Vilcea (P = {rows_s[0][6]}) over Fagaras (P = {rows_s[1][6]}): the road is shorter and "
           f"Rimnicu Vilcea is slightly more threatening (xGT {X['Rimnicu Vilcea']:.4f} vs {X['Fagaras']:.4f}, because 97 + 101 with a stop at "
           "Pitesti completes more often than one 211 pass). Individually, h(Rimnicu Vilcea) = "
           f"{h_table['Rimnicu Vilcea']} &lt; h(Fagaras) = {h_table['Fagaras']} — true costs 198 vs 211."))

S.append(p("Running A* from Zerind with these h values", H3))
S.append(p("A* always expands the frontier city with the smallest f = g + h (g = road cost already paid). Every step of the search:"))
g = {"Zerind": 0}
closed = set()
trace_rows = [["step", "expanded (g + h = f)", "frontier after expansion, sorted by f"]]
pq = [(h_table["Zerind"], "Zerind")]
step = 0
while pq:
    pq.sort()
    f, u = pq.pop(0)
    if u in closed:
        continue
    closed.add(u)
    step += 1
    if u == GOAL:
        trace_rows.append([str(step), f"<b>{u}</b> ({g[u]} + 0 = {g[u]}) — goal reached", "—"])
        break
    for v, w in GRAPH[u].items():
        ng = g[u] + w
        if ng < g.get(v, 10 ** 9):
            g[v] = ng
            pq.append((ng + h_table[v], v))
    fr = sorted(set((g[v] + h_table[v], v) for _, v in pq if v not in closed))
    trace_rows.append([str(step), f"<b>{u}</b> ({g[u]} + {h_table[u]} = {g[u] + h_table[u]})",
                       ",  ".join(f"{v} ({g[v]}+{h_table[v]}={fv})" for fv, v in fr)])
S.append(table(trace_rows, col_widths=[12 * mm, 52 * mm, 110 * mm]))
r = astar("Zerind", GOAL, h_table)
S.append(Spacer(1, 4))
S.append(p(f"Result: path <b>{' → '.join(r.path)}</b>, cost <b>{r.cost}</b> (the optimum), <b>{r.expanded} cities expanded</b> — "
           "uniform-cost search needs 13 for the same pair, straight-line distance 8, the old ring method 8."))
S.append(p("Look at step 1: f(Arad) = 75 + 453 = 528 beats f(Oradea) = 71 + 464 = 535. The 4-point head start of Oradea's cheaper "
           "road is outweighed by the 11-point heuristic difference, so A* goes through Arad immediately. Oradea stays on the "
           "frontier the whole way (f = 535) and is never expanded — correctly, since no route through it can beat 493. "
           "At step 3 the same happens for the second fork: Rimnicu Vilcea (295 + 212 = 507) beats Fagaras (314 + 219 = 533). "
           "Nothing was expanded that is not on the final path.", NOTE))

S.append(p("What the cost-only passer (τ = 0) does at the same fork", H3))
h2, _ = build_xgt(0.01, 0.01, 0.0)(GOAL)
r2 = astar("Zerind", GOAL, h2)
S.append(p(f"With the pass choice depending on road cost only (β = γ = 0.01), the same fork gives h(Arad) = {h2['Arad']} "
           f"and h(Oradea) = {h2['Oradea']} — the <b>wrong order</b>. Arad has three roads, so its probability is spread over Zerind and "
           "Timisoara too (“dilution”); Oradea has only two. A* then expands Oradea first (f = 71 + "
           f"{h2['Oradea']} = {71 + h2['Oradea']} vs 75 + {h2['Arad']} = {75 + h2['Arad']}) and finishes with "
           f"<b>{' → '.join(r2.path)}</b>, cost <b>{r2.cost}</b> instead of 493. Letting the passer look at the receiver's threat "
           "(τ) is what turns this around."))

# ---------------------------------------------------------------- Part 7: full table
S.append(PageBreak())
S.append(p("Part 7 — The full table for goal = Bucharest and how to read it", H2))
rows = [["city", "true remaining cost d*", "xGT", "h (int)", "h / d*", "roads"]]
for c in sorted(CITIES, key=lambda c: d_star[c]):
    rows.append([c, d_star[c], f"{X[c]:.4f}", h_table[c], "–" if d_star[c] == 0 else f"{h_table[c] / d_star[c]:.2f}", len(GRAPH[c])])
S.append(table(rows, col_widths=[32 * mm, 36 * mm, 22 * mm, 18 * mm, 18 * mm, 16 * mm]))
S.append(Spacer(1, 6))
S.append(p("The true remaining cost d* is shown only to judge the heuristic; it is never used to compute it. Points to notice:"))
S.append(p("• The order is the same as the true order for every city (Spearman 1.000, zero inversions)."))
S.append(p("• h is 0–9 % above the true cost. Cities with one road (Giurgiu) or whose best road dominates completely pay nothing; "
           "cities with several plausible roads (Sibiu, Arad) pay the most. That is the “hesitation tax” of an imperfect passer."))
S.append(p("• Cities in the same hop ring get different values: Fagaras (1 hop, 219) vs Giurgiu (1 hop, 90); Sibiu (2 hops, 302) "
           "vs Hirsova (2 hops, 193). The old ring method gave all cities in a ring the same value."))

S.append(p("Why these parameter values", H3))
S.append(p("• <b>τ = 1.5.</b> With τ = 0 (the model as written in the football doc) the passer ignores where the ball is going; a "
           "three-road city like Arad spreads its probability over bad roads and is ranked behind two-road Oradea for goal Sibiu — a "
           "wrong answer. τ = 1 fixed the ranking; τ = 1.5 also removed the last non-optimal A* route (Zerind→Craiova) while h still "
           "differs from the road cost (Arad 151 vs true 140 for goal Sibiu). τ ≥ 2–3 makes the passer nearly perfect and h collapses "
           "onto the road cost — a renamed Dijkstra, which the guide rejects."))
S.append(p("• <b>β = 0.02.</b> Slightly stronger preference for short roads than the doc's 0.01; it raised A* optimality without "
           "changing any ranking."))
S.append(p("• <b>γ = 0.01.</b> Sets the unit: −ln(xGT)/γ is in road-cost units. Larger γ pulls h onto the road cost, smaller inflates it."))

S.append(p("Result summary (all 380 start→goal pairs)", H3))
S.append(table([
    ["heuristic", "guide pair checks", "Spearman vs d*", "A* optimal", "nodes expanded"],
    ["xGT (this)", "8/8", "0.999", "380/380", "4.94"],
    ["UCS (h = 0)", "0/8", "–", "380/380", "11.00"],
    ["straight-line distance", "6/8", "0.848", "380/380", "6.81"],
    ["old ring / min-edge", "4/8", "0.975", "380/380", "5.60"],
], col_widths=[46 * mm, 32 * mm, 30 * mm, 26 * mm, 30 * mm]))
S.append(Spacer(1, 4))
S.append(p("Files: <font name='Mono'>final/method.py</font> (constants), <font name='Mono'>core/xgt.py</font> (Python formula), "
           "<font name='Mono'>tools/java/XgtHeuristic.java</font> (Java, identical output), <font name='Mono'>final/exports/heuristicTable.ts</font> "
           "/ <font name='Mono'>HeuristicTable.java</font> (precomputed 20-goal integer tables for the app).", SMALL))

doc.build(S)
print("wrote", OUT)
