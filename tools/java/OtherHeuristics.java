import java.util.HashMap;
import java.util.Map;

/**
 * Java ports of the remaining football methods (one static nested class each).
 * Each mirrors the corresponding method.py so Python and Java can be cross-checked.
 */
public final class OtherHeuristics {

    static final double EPS = 1e-9;

    /** Shift so the smallest non-goal value is >= 0 (matches the Python builders). */
    static Map<String, Double> shiftNonNegative(Map<String, Double> raw, String goal) {
        double m = Double.POSITIVE_INFINITY;
        for (String c : RomaniaGraph.CITIES) if (!c.equals(goal)) m = Math.min(m, raw.get(c));
        if (m < 0) {
            for (String c : RomaniaGraph.CITIES) raw.put(c, c.equals(goal) ? 0.0 : raw.get(c) - m);
        }
        return raw;
    }

    // ---------------------------------------------------------------- Method 2
    /** PPS(u) = sum_v P(u->v) * max(0, xGT(v) - xGT(u));  h = road-scaled -log(PPS). */
    public static final class ProgressivePassing implements Heuristic {
        final double beta, gamma, tau;
        public ProgressivePassing(double beta, double gamma, double tau) { this.beta = beta; this.gamma = gamma; this.tau = tau; }

        public Map<String, Integer> table(String goal) {
            Map<String, Double> x = new XgtHeuristic(beta, gamma, tau).values(goal);
            Map<String, Map<String, Double>> p = FootballMath.transitionProbs(beta);
            Map<String, Double> raw = new HashMap<>();
            for (String u : RomaniaGraph.CITIES) {
                double s = 0;
                for (String v : FootballMath.neighbourOrder(u)) s += p.get(u).get(v) * Math.max(0.0, x.get(v) - x.get(u));
                raw.put(u, -Math.log(s + EPS));
            }
            raw.put(goal, 0.0);
            return Scaling.toIntRoadScaled(shiftNonNegative(raw, goal), goal);
        }
    }

    // ---------------------------------------------------------------- Method 3
    /** PR_sum(u) = sum_v C(u,v) * xGT(v);  h = road-scaled -log(PR_sum). */
    public static final class PressResistance implements Heuristic {
        final double beta, gamma, tau;
        public PressResistance(double beta, double gamma, double tau) { this.beta = beta; this.gamma = gamma; this.tau = tau; }

        public Map<String, Integer> table(String goal) {
            Map<String, Double> x = new XgtHeuristic(beta, gamma, tau).values(goal);
            Map<String, Map<String, Double>> c = FootballMath.completionProbs(gamma);
            Map<String, Double> raw = new HashMap<>();
            for (String u : RomaniaGraph.CITIES) {
                double s = 0;
                for (String v : FootballMath.neighbourOrder(u)) s += c.get(u).get(v) * x.get(v);
                raw.put(u, -Math.log(s + EPS));
            }
            raw.put(goal, 0.0);
            return Scaling.toIntRoadScaled(shiftNonNegative(raw, goal), goal);
        }
    }

    // ---------------------------------------------------------------- Method 5
    /** I(goal)=1, I(u) = alpha * sum_v exp(-lambda w) I(v);  h = -log(I)/lambda. */
    public static final class PitchControl implements Heuristic {
        final double lambda, alpha;
        public PitchControl(double lambda, double alpha) { this.lambda = lambda; this.alpha = alpha; }

        public Map<String, Integer> table(String goal) {
            Map<String, Map<String, Double>> a = FootballMath.passPreference(lambda);
            Map<String, Double> init = FootballMath.zeros();
            init.put(goal, 1.0);
            Map<String, Double> x = FootballMath.fixedPoint(cur -> {
                Map<String, Double> nx = new HashMap<>();
                nx.put(goal, 1.0);
                for (String u : RomaniaGraph.CITIES) {
                    if (u.equals(goal)) continue;
                    double s = 0;
                    for (String v : FootballMath.neighbourOrder(u)) s += a.get(u).get(v) * cur.get(v);
                    nx.put(u, alpha * s);
                }
                return nx;
            }, init, 1e-12, 20000);
            Map<String, Double> raw = new HashMap<>();
            for (String c : RomaniaGraph.CITIES) raw.put(c, x.get(c) > 0 ? -Math.log(x.get(c)) / lambda : Double.POSITIVE_INFINITY);
            raw.put(goal, 0.0);
            return FootballMath.toIntTable(raw, goal, 1.0);
        }
    }

    // ---------------------------------------------------------------- Method 6
    /** Personalized PageRank restarted at the goal;  h = road-scaled ln(pi(goal)/pi(u)). */
    public static final class GoalCentrality implements Heuristic {
        final double lambda, damping;
        public GoalCentrality(double lambda, double damping) { this.lambda = lambda; this.damping = damping; }

        public Map<String, Integer> table(String goal) {
            Map<String, Map<String, Double>> p = FootballMath.transitionProbs(lambda);
            Map<String, Double> init = new HashMap<>();
            for (String c : RomaniaGraph.CITIES) init.put(c, 1.0 / RomaniaGraph.CITIES.size());
            Map<String, Double> pi = FootballMath.fixedPoint(cur -> {
                Map<String, Double> npi = new HashMap<>();
                for (String c : RomaniaGraph.CITIES) npi.put(c, c.equals(goal) ? 1.0 - damping : 0.0);
                for (String u : RomaniaGraph.CITIES) {
                    for (String v : FootballMath.neighbourOrder(u)) {
                        npi.put(v, npi.get(v) + damping * p.get(u).get(v) * cur.get(u));
                    }
                }
                return npi;
            }, init, 1e-14, 100000);
            Map<String, Double> raw = new HashMap<>();
            for (String c : RomaniaGraph.CITIES) raw.put(c, Math.log(pi.get(goal) / pi.get(c)));
            return Scaling.toIntRoadScaled(raw, goal);
        }
    }

    // ---------------------------------------------------------------- Method 7
    /** AttackValue = xGT * (1+alpha PR_n)/(1+alpha) * (1+delta PPS_n)/(1+delta);  h = -log(AV)/gamma. */
    public static final class Combined implements Heuristic {
        final double beta, gamma, tau, alpha, delta;
        public Combined(double beta, double gamma, double tau, double alpha, double delta) {
            this.beta = beta; this.gamma = gamma; this.tau = tau; this.alpha = alpha; this.delta = delta;
        }

        public Map<String, Integer> table(String goal) {
            Map<String, Double> x = new XgtHeuristic(beta, gamma, tau).values(goal);
            Map<String, Map<String, Double>> p = FootballMath.transitionProbs(beta);
            Map<String, Map<String, Double>> c = FootballMath.completionProbs(gamma);
            Map<String, Double> pr = new HashMap<>(), pps = new HashMap<>();
            for (String u : RomaniaGraph.CITIES) {
                double sPr = 0, sPps = 0;
                for (String v : FootballMath.neighbourOrder(u)) {
                    sPr += c.get(u).get(v) * x.get(v);
                    sPps += p.get(u).get(v) * Math.max(0.0, x.get(v) - x.get(u));
                }
                pr.put(u, sPr);
                pps.put(u, sPps);
            }
            double mPr = 0, mPps = 0;
            for (String u : RomaniaGraph.CITIES) if (!u.equals(goal)) { mPr = Math.max(mPr, pr.get(u)); mPps = Math.max(mPps, pps.get(u)); }
            Map<String, Double> raw = new HashMap<>();
            for (String u : RomaniaGraph.CITIES) {
                double prn = mPr > 0 ? pr.get(u) / mPr : 0, ppsn = mPps > 0 ? pps.get(u) / mPps : 0;
                double av = x.get(u) * (1 + alpha * prn) / (1 + alpha) * (1 + delta * ppsn) / (1 + delta);
                raw.put(u, -Math.log(av) / gamma);
            }
            raw.put(goal, 0.0);
            return FootballMath.toIntTable(raw, goal, 1.0);
        }
    }

    // ---------------------------------------------------------------- Method 8 (own)
    /** T(u) = sum_v P(u->v) (w + T(v)),  P ~ exp(-beta w) exp(-kappa T(v));  h = round(T). */
    public static final class ExpectedTime implements Heuristic {
        final double beta, kappa;
        public ExpectedTime(double beta, double kappa) { this.beta = beta; this.kappa = kappa; }

        public Map<String, Integer> table(String goal) {
            Map<String, Map<String, Double>> q = FootballMath.passPreference(beta);
            Map<String, Double> t = FootballMath.fixedPoint(cur -> {
                Map<String, Double> nt = new HashMap<>();
                nt.put(goal, 0.0);
                for (String u : RomaniaGraph.CITIES) {
                    if (u.equals(goal)) continue;
                    String[] nbrs = FootballMath.neighbourOrder(u);
                    double[] pref = new double[nbrs.length];
                    double s = 0;
                    for (int i = 0; i < nbrs.length; i++) { pref[i] = q.get(u).get(nbrs[i]) * Math.exp(-kappa * cur.get(nbrs[i])); s += pref[i]; }
                    double val = 0;
                    for (int i = 0; i < nbrs.length; i++) val += (pref[i] / s) * (RomaniaGraph.GRAPH.get(u).get(nbrs[i]) + cur.get(nbrs[i]));
                    nt.put(u, val);
                }
                return nt;
            }, FootballMath.zeros(), 1e-9, 200000);
            return FootballMath.toIntTable(t, goal, 1.0);
        }
    }

    // ---------------------------------------------------------------- Method 9 (own)
    /** K(u) = expected road cost + turnover penalties before scoring;  h = round(K). */
    public static final class TurnoverRisk implements Heuristic {
        final double beta, gamma, L, kappa;
        public TurnoverRisk(double beta, double gamma, double L, double kappa) { this.beta = beta; this.gamma = gamma; this.L = L; this.kappa = kappa; }

        public Map<String, Integer> table(String goal) {
            Map<String, Map<String, Double>> q = FootballMath.passPreference(beta);
            Map<String, Map<String, Double>> c = FootballMath.completionProbs(gamma);
            Map<String, Double> k = FootballMath.fixedPoint(cur -> {
                Map<String, Double> nk = new HashMap<>();
                nk.put(goal, 0.0);
                for (String u : RomaniaGraph.CITIES) {
                    if (u.equals(goal)) continue;
                    String[] nbrs = FootballMath.neighbourOrder(u);
                    double[] pref = new double[nbrs.length];
                    double s = 0;
                    for (int i = 0; i < nbrs.length; i++) { pref[i] = q.get(u).get(nbrs[i]) * Math.exp(-kappa * cur.get(nbrs[i])); s += pref[i]; }
                    double num = 0, den = 1.0;
                    for (int i = 0; i < nbrs.length; i++) {
                        double p = pref[i] / s, cc = c.get(u).get(nbrs[i]);
                        num += p * (RomaniaGraph.GRAPH.get(u).get(nbrs[i]) + cc * cur.get(nbrs[i]) + (1 - cc) * L);
                        den -= p * (1 - cc);
                    }
                    nk.put(u, num / den);
                }
                return nk;
            }, FootballMath.zeros(), 1e-9, 200000);
            return FootballMath.toIntTable(k, goal, 1.0);
        }
    }

    private OtherHeuristics() {}
}
