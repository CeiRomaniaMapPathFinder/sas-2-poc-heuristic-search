import java.util.HashMap;
import java.util.Map;
import java.util.function.Function;

import static java.util.Map.Entry;

/** Line-by-line port of core/football_math.py. */
public final class FootballMath {

    /** q(u,v) = exp(-beta * w). */
    public static Map<String, Map<String, Double>> passPreference(double beta) {
        Map<String, Map<String, Double>> q = new HashMap<>();
        for (String u : RomaniaGraph.CITIES) {
            Map<String, Double> row = new HashMap<>();
            for (Entry<String, Integer> e : RomaniaGraph.GRAPH.get(u).entrySet()) {
                row.put(e.getKey(), Math.exp(-beta * e.getValue()));
            }
            q.put(u, row);
        }
        return q;
    }

    /** P(u->v) = q(u,v) / sum_k q(u,k). */
    public static Map<String, Map<String, Double>> normalizeRows(Map<String, Map<String, Double>> q) {
        Map<String, Map<String, Double>> p = new HashMap<>();
        for (String u : q.keySet()) {
            double s = sumValues(q.get(u), u);
            Map<String, Double> row = new HashMap<>();
            for (Entry<String, Double> e : q.get(u).entrySet()) row.put(e.getKey(), e.getValue() / s);
            p.put(u, row);
        }
        return p;
    }

    public static Map<String, Map<String, Double>> transitionProbs(double beta) {
        return normalizeRows(passPreference(beta));
    }

    /** C(u,v) = exp(-gamma * w). */
    public static Map<String, Map<String, Double>> completionProbs(double gamma) {
        return passPreference(gamma);
    }

    /**
     * Sum of a neighbour map in the same order Python iterates GRAPH[u]
     * (insertion order of the edge list) -- see neighbourOrder().
     */
    static double sumValues(Map<String, Double> row, String u) {
        double s = 0;
        for (String v : neighbourOrder(u)) s += row.get(v);
        return s;
    }

    /**
     * Python builds GRAPH[u] from the EDGES list, so its neighbour order is the
     * order edges appear there.  We replicate that so floating point sums are
     * added in the same order and the two implementations agree bit-for-bit.
     */
    public static String[] neighbourOrder(String u) {
        return NEIGHBOUR_ORDER.get(u);
    }

    private static final Map<String, String[]> NEIGHBOUR_ORDER = Map.ofEntries(
            Map.entry("Arad", new String[]{"Zerind", "Sibiu", "Timisoara"}),
            Map.entry("Zerind", new String[]{"Arad", "Oradea"}),
            Map.entry("Oradea", new String[]{"Zerind", "Sibiu"}),
            Map.entry("Sibiu", new String[]{"Oradea", "Arad", "Rimnicu Vilcea", "Fagaras"}),
            Map.entry("Timisoara", new String[]{"Arad", "Lugoj"}),
            Map.entry("Lugoj", new String[]{"Timisoara", "Mehadia"}),
            Map.entry("Mehadia", new String[]{"Lugoj", "Drobeta"}),
            Map.entry("Drobeta", new String[]{"Mehadia", "Craiova"}),
            Map.entry("Craiova", new String[]{"Drobeta", "Rimnicu Vilcea", "Pitesti"}),
            Map.entry("Rimnicu Vilcea", new String[]{"Craiova", "Sibiu", "Pitesti"}),
            Map.entry("Pitesti", new String[]{"Craiova", "Rimnicu Vilcea", "Bucharest"}),
            Map.entry("Fagaras", new String[]{"Sibiu", "Bucharest"}),
            Map.entry("Bucharest", new String[]{"Fagaras", "Pitesti", "Giurgiu", "Urziceni"}),
            Map.entry("Giurgiu", new String[]{"Bucharest"}),
            Map.entry("Urziceni", new String[]{"Bucharest", "Hirsova", "Vaslui"}),
            Map.entry("Hirsova", new String[]{"Urziceni", "Eforie"}),
            Map.entry("Eforie", new String[]{"Hirsova"}),
            Map.entry("Vaslui", new String[]{"Urziceni", "Iasi"}),
            Map.entry("Iasi", new String[]{"Vaslui", "Neamt"}),
            Map.entry("Neamt", new String[]{"Iasi"})
    );

    /** Iterate x <- update(x) until max |change| < tol. */
    public static Map<String, Double> fixedPoint(Function<Map<String, Double>, Map<String, Double>> update,
                                                 Map<String, Double> init, double tol, int maxIter) {
        Map<String, Double> x = new HashMap<>(init);
        for (int it = 0; it < maxIter; it++) {
            Map<String, Double> nx = update.apply(x);
            double delta = 0;
            for (String c : nx.keySet()) delta = Math.max(delta, Math.abs(nx.get(c) - x.get(c)));
            x = nx;
            if (delta < tol) return x;
        }
        return x;
    }

    /** int h = floor(scale*raw + 0.5), h >= 0, h(goal) = 0.  Same rounding as Python. */
    public static Map<String, Integer> toIntTable(Map<String, Double> raw, String goal, double scale) {
        Map<String, Integer> out = new HashMap<>();
        for (Entry<String, Double> e : raw.entrySet()) {
            out.put(e.getKey(), Math.max(0, (int) Math.floor(scale * e.getValue() + 0.5)));
        }
        out.put(goal, 0);
        return out;
    }

    public static Map<String, Double> zeros() {
        Map<String, Double> m = new HashMap<>();
        for (String c : RomaniaGraph.CITIES) m.put(c, 0.0);
        return m;
    }

    private FootballMath() {}
}
