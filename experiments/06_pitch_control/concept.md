# Pitch control (goal influence)

_Where the idea came from: the football brief's pitch-control section._

## The football idea

Pitch-control models estimate how much of the pitch each team "owns": influence spreads out from players and fades with distance. Here the **goal city is the only source of influence**; it spreads along the roads, and every road passes on a share that shrinks with road cost. A city under strong goal influence is tactically close to the goal.

## How h(n) is calculated

Parameters: `lambda` (how fast influence fades along a road), `alpha` (how much influence survives each hand-over, i.e. per pass).

1. Road transmission factor:

       a(u,v) = exp(-lambda * w(u,v))

2. Influence field (iterate until stable; start with 0 everywhere, 1 at the goal):

       I(goal) = 1
       I(u)    = alpha * sum over neighbours v of  a(u,v) * I(v)

   Unlike xGT there is **no normalisation** per city: a city with three cheap roads collects influence from all three. That is the pitch-control flavour — hubs are "well covered".

3. Heuristic in road units:

       h(u) = floor( -ln(I(u)) / lambda + 0.5 )      h(goal) = 0

Why `alpha` is needed: without it, a city with several roads could collect *more* than 1 influence and the iteration may not settle. `alpha < 1` is the football reading "some control is lost every time the ball changes feet".

### What the formula amounts to

Unrolling the iteration, `I(u)` is a sum over **every walk** from `u` to the goal of `alpha^(number of passes) * exp(-lambda * total road cost)`. So `-ln(I)/lambda` is a *soft minimum* over all walks of `(road cost + passes * (-ln alpha)/lambda)`. With `lambda = 0.02, alpha = 0.8` each pass costs about 11 road units of "control". A city with several short walks to the goal gets a lower h than one with a single walk of the same cost.

### Worked example (goal = Bucharest, lambda = 0.02, alpha = 0.8)

`a(90) = exp(-1.8) = 0.165`, `a(101) = 0.133`, `a(97) = 0.144`, `a(138) = 0.063`. After convergence `I(Rimnicu Vilcea) = 0.0132`, `I(Craiova) = 0.0061`.

- Giurgiu: `I = 0.8 * 0.165 * 1 = 0.132` → `h = -ln(0.132)/0.02 = 101`.
- Pitesti: `I = 0.8 * (0.133*1 + 0.144*0.0132 + 0.063*0.0061) = 0.8 * 0.1352 = 0.108` → `h = 111`.

`h(Giurgiu) = 101 < h(Pitesti) = 111`. Giurgiu's h is above its road cost 90 because of the one hand-over (`-ln 0.8 / 0.02 = 11`); Pitesti's is only 10 above 101 because its two side roads add a little influence back.

## Files

- `method.py` — `influence`, `build`.
- `experiment.py` — lambda/alpha sweep; writes `results.md`.
- Java port: `../../tools/java/OtherHeuristics.java` (`PitchControl`).
