import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;

/**
 * Same shape and city ids as the friend's
 * ai-pathfinder-api/.../data/RomaniaMap.java (feature/blindsearch), so a
 * heuristic class from this folder can be dropped into the API by replacing
 * RomaniaGraph.GRAPH with RomaniaMap.GRAPH.
 */
public final class RomaniaGraph {

    public static final Map<String, Map<String, Integer>> GRAPH = Map.ofEntries(
            Map.entry("Oradea", Map.of("Zerind", 71, "Sibiu", 151)),
            Map.entry("Zerind", Map.of("Oradea", 71, "Arad", 75)),
            Map.entry("Arad", Map.of("Zerind", 75, "Sibiu", 140, "Timisoara", 118)),
            Map.entry("Timisoara", Map.of("Arad", 118, "Lugoj", 111)),
            Map.entry("Lugoj", Map.of("Timisoara", 111, "Mehadia", 70)),
            Map.entry("Mehadia", Map.of("Lugoj", 70, "Drobeta", 75)),
            Map.entry("Drobeta", Map.of("Mehadia", 75, "Craiova", 120)),
            Map.entry("Craiova", Map.of("Drobeta", 120, "Rimnicu Vilcea", 146, "Pitesti", 138)),
            Map.entry("Rimnicu Vilcea", Map.of("Sibiu", 80, "Craiova", 146, "Pitesti", 97)),
            Map.entry("Sibiu", Map.of("Oradea", 151, "Arad", 140, "Fagaras", 99, "Rimnicu Vilcea", 80)),
            Map.entry("Fagaras", Map.of("Sibiu", 99, "Bucharest", 211)),
            Map.entry("Pitesti", Map.of("Rimnicu Vilcea", 97, "Craiova", 138, "Bucharest", 101)),
            Map.entry("Bucharest", Map.of("Fagaras", 211, "Pitesti", 101, "Giurgiu", 90, "Urziceni", 85)),
            Map.entry("Giurgiu", Map.of("Bucharest", 90)),
            Map.entry("Urziceni", Map.of("Bucharest", 85, "Hirsova", 98, "Vaslui", 142)),
            Map.entry("Hirsova", Map.of("Urziceni", 98, "Eforie", 86)),
            Map.entry("Eforie", Map.of("Hirsova", 86)),
            Map.entry("Vaslui", Map.of("Urziceni", 142, "Iasi", 92)),
            Map.entry("Iasi", Map.of("Vaslui", 92, "Neamt", 87)),
            Map.entry("Neamt", Map.of("Iasi", 87))
    );

    /** Sorted city list so iteration order is deterministic (matches Python's sorted(GRAPH)). */
    public static final List<String> CITIES;

    static {
        List<String> c = new ArrayList<>(GRAPH.keySet());
        Collections.sort(c);
        CITIES = Collections.unmodifiableList(c);
    }

    public static double meanEdge() {
        double sum = 0;
        int n = 0;
        for (String u : CITIES) {
            for (Map.Entry<String, Integer> e : GRAPH.get(u).entrySet()) {
                if (u.compareTo(e.getKey()) < 0) { sum += e.getValue(); n++; }
            }
        }
        return sum / n;
    }

    private RomaniaGraph() {}
}
