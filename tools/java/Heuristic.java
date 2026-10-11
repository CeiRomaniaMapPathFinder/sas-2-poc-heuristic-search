import java.util.Map;

/**
 * A heuristic is a per-goal table of integer values.  Compute it once per
 * goal (cheap: 20 cities, a few hundred iterations) and cache it.
 */
public interface Heuristic {
    /** city -> h(city) for the given goal; h(goal) == 0. */
    Map<String, Integer> table(String goal);

    default int h(String city, String goal) {
        return table(goal).get(city);
    }
}
