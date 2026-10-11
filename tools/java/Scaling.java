import java.util.HashMap;
import java.util.Map;

/** Port of core/scaling.py: scale = mean(d*) / mean(raw) over non-goal cities (calibration only). */
public final class Scaling {

    public static Map<String, Integer> toIntRoadScaled(Map<String, Double> rawIn, String goal) {
        Map<String, Double> raw = new HashMap<>(rawIn);
        double maxFinite = 0;
        for (double v : raw.values()) if (!Double.isInfinite(v)) maxFinite = Math.max(maxFinite, v);
        double cap = maxFinite * 2 + 1;
        for (String c : raw.keySet()) if (Double.isInfinite(raw.get(c))) raw.put(c, cap);

        Map<String, Integer> d = Search.dijkstra(goal);
        double sumRaw = 0, sumD = 0;
        int n = 0;
        for (String c : RomaniaGraph.CITIES) {
            if (c.equals(goal)) continue;
            sumRaw += raw.get(c);
            sumD += d.get(c);
            n++;
        }
        double mRaw = sumRaw / n, mD = sumD / n;
        double scale = mRaw > 0 ? mD / mRaw : 1.0;
        return FootballMath.toIntTable(raw, goal, scale);
    }

    private Scaling() {}
}
