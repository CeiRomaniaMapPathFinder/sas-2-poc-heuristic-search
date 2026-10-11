import java.util.HashMap;
import java.util.Map;

/**
 * Expected Goal Threat (port of core/xgt.py).
 *
 *   xGT(goal) = 1
 *   xGT(u)    = sum_v P(u->v) * C(u,v) * xGT(v)
 *   P(u->v)   ~ exp(-beta*w) * xGT(v)^tau        (tau = 0 -> the cost-only passer)
 *   C(u,v)    = exp(-gamma*w)
 *   h(u)      = floor(-log(xGT(u)) / gamma + 0.5)
 *
 * The setting this project settled on: beta = 0.02, gamma = 0.01, tau = 1.5 (see final/).
 */
public final class XgtHeuristic implements Heuristic {

    private final double beta, gamma, tau;
    private final Map<String, Map<String, Integer>> cache = new HashMap<>();

    public XgtHeuristic(double beta, double gamma, double tau) {
        this.beta = beta; this.gamma = gamma; this.tau = tau;
    }

    /** The setting this project settled on. */
    public static XgtHeuristic finalModel() {
        return new XgtHeuristic(0.02, 0.01, 1.5);
    }

    /** Raw xGT values (0..1, goal = 1). */
    public Map<String, Double> values(String goal) {
        Map<String, Map<String, Double>> q = FootballMath.passPreference(beta);
        Map<String, Map<String, Double>> c = FootballMath.completionProbs(gamma);

        Map<String, Double> init = new HashMap<>();
        for (String city : RomaniaGraph.CITIES) init.put(city, tau == 0 ? 0.0 : 1e-3);
        init.put(goal, 1.0);

        return FootballMath.fixedPoint(x -> {
            Map<String, Double> nx = new HashMap<>();
            nx.put(goal, 1.0);
            for (String u : RomaniaGraph.CITIES) {
                if (u.equals(goal)) continue;
                String[] nbrs = FootballMath.neighbourOrder(u);
                double[] pref = new double[nbrs.length];
                double s = 0;
                for (int i = 0; i < nbrs.length; i++) {
                    pref[i] = q.get(u).get(nbrs[i]) * Math.pow(Math.max(x.get(nbrs[i]), 1e-30), tau);
                    s += pref[i];
                }
                double val = 0;
                for (int i = 0; i < nbrs.length; i++) {
                    val += (pref[i] / s) * c.get(u).get(nbrs[i]) * x.get(nbrs[i]);
                }
                nx.put(u, val);
            }
            return nx;
        }, init, 1e-12, 100000);
    }

    @Override
    public Map<String, Integer> table(String goal) {
        return cache.computeIfAbsent(goal, g -> {
            Map<String, Double> x = values(g);
            Map<String, Double> raw = new HashMap<>();
            for (String city : RomaniaGraph.CITIES) raw.put(city, -Math.log(x.get(city)) / gamma);
            raw.put(g, 0.0);
            return FootballMath.toIntTable(raw, g, 1.0);
        });
    }
}
