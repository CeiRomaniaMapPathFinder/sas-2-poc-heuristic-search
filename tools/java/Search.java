import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.PriorityQueue;
import java.util.Set;

/** Dijkstra (ground truth, evaluation only) and A* with re-opening. Port of core/search.py. */
public final class Search {

    public record Result(List<String> path, int cost, int expanded, List<String> order) {}

    public static Map<String, Integer> dijkstra(String goal) {
        Map<String, Integer> dist = new HashMap<>();
        dist.put(goal, 0);
        PriorityQueue<long[]> pq = new PriorityQueue<>((a, b) -> Long.compare(a[0], b[0]));
        List<String> idx = RomaniaGraph.CITIES;
        pq.add(new long[]{0, idx.indexOf(goal)});
        while (!pq.isEmpty()) {
            long[] top = pq.poll();
            String u = idx.get((int) top[1]);
            if (top[0] > dist.get(u)) continue;
            for (Map.Entry<String, Integer> e : RomaniaGraph.GRAPH.get(u).entrySet()) {
                int nd = (int) top[0] + e.getValue();
                if (nd < dist.getOrDefault(e.getKey(), Integer.MAX_VALUE)) {
                    dist.put(e.getKey(), nd);
                    pq.add(new long[]{nd, idx.indexOf(e.getKey())});
                }
            }
        }
        return dist;
    }

    /** A* with f = g + h(table).  Closed nodes are re-opened if a cheaper g is found. */
    public static Result astar(String start, String goal, Map<String, Integer> h) {
        Map<String, Integer> g = new HashMap<>();
        Map<String, String> parent = new HashMap<>();
        Set<String> closed = new HashSet<>();
        List<String> order = new ArrayList<>();
        g.put(start, 0);
        parent.put(start, null);
        // entries: f, insertion counter (tie-break), city index
        PriorityQueue<long[]> pq = new PriorityQueue<>((a, b) -> a[0] != b[0] ? Long.compare(a[0], b[0]) : Long.compare(a[1], b[1]));
        long counter = 0;
        List<String> idx = RomaniaGraph.CITIES;
        pq.add(new long[]{h.get(start), counter, idx.indexOf(start)});
        while (!pq.isEmpty()) {
            long[] top = pq.poll();
            String u = idx.get((int) top[2]);
            if (closed.contains(u)) continue;
            closed.add(u);
            order.add(u);
            if (u.equals(goal)) {
                List<String> path = new ArrayList<>();
                for (String c = u; c != null; c = parent.get(c)) path.add(c);
                Collections.reverse(path);
                return new Result(path, g.get(goal), order.size(), order);
            }
            for (String v : FootballMath.neighbourOrder(u)) {
                int ng = g.get(u) + RomaniaGraph.GRAPH.get(u).get(v);
                if (ng < g.getOrDefault(v, Integer.MAX_VALUE)) {
                    g.put(v, ng);
                    parent.put(v, u);
                    closed.remove(v);
                    counter++;
                    pq.add(new long[]{ng + h.get(v), counter, idx.indexOf(v)});
                }
            }
        }
        return null;
    }

    private Search() {}
}
