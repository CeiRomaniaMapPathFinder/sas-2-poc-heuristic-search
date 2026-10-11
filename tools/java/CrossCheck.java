import java.util.LinkedHashMap;
import java.util.Map;

/**
 * Prints every heuristic's int table for the goals given on the command line
 * as one JSON object:  { "method": { "goal": { "city": h, ... } } }.
 * core/crosscheck.py runs this and compares with the Python tables.
 *
 * Run (Java 22+ multi-file launcher, from this folder):
 *     java CrossCheck.java Bucharest Sibiu
 */
public final class CrossCheck {

    public static Map<String, Heuristic> methods() {
        Map<String, Heuristic> m = new LinkedHashMap<>();
        m.put("xgt tau=0 b0.01 g0.01", new XgtHeuristic(0.01, 0.01, 0.0));
        m.put("xgt tau=1 b0.01 g0.01", new XgtHeuristic(0.01, 0.01, 1.0));
        m.put("xgt tau=1.5 b0.02 g0.01 (final)", XgtHeuristic.finalModel());
        m.put("pps b0.01 g0.01", new OtherHeuristics.ProgressivePassing(0.01, 0.01, 0.0));
        m.put("pr_sum b0.01 g0.01", new OtherHeuristics.PressResistance(0.01, 0.01, 0.0));
        m.put("pitch l0.02 a0.8", new OtherHeuristics.PitchControl(0.02, 0.8));
        m.put("pagerank l0.01 d0.85", new OtherHeuristics.GoalCentrality(0.01, 0.85));
        m.put("combined t1 a1 d1", new OtherHeuristics.Combined(0.01, 0.01, 1.0, 1.0, 1.0));
        m.put("expected_time b0.01 k0.005", new OtherHeuristics.ExpectedTime(0.01, 0.005));
        m.put("turnover b0.01 g0.005 k0.005", new OtherHeuristics.TurnoverRisk(0.01, 0.005, RomaniaGraph.meanEdge(), 0.005));
        return m;
    }

    public static void main(String[] args) {
        String[] goals = args.length > 0 ? args : new String[]{"Bucharest", "Sibiu"};
        StringBuilder sb = new StringBuilder("{");
        boolean firstM = true;
        for (Map.Entry<String, Heuristic> e : methods().entrySet()) {
            if (!firstM) sb.append(",");
            firstM = false;
            sb.append("\"").append(e.getKey()).append("\":{");
            boolean firstG = true;
            for (String goal : goals) {
                if (!firstG) sb.append(",");
                firstG = false;
                sb.append("\"").append(goal).append("\":{");
                Map<String, Integer> t = e.getValue().table(goal);
                boolean firstC = true;
                for (String c : RomaniaGraph.CITIES) {
                    if (!firstC) sb.append(",");
                    firstC = false;
                    sb.append("\"").append(c).append("\":").append(t.get(c));
                }
                sb.append("}");
            }
            sb.append("}");
        }
        sb.append("}");
        System.out.println(sb);
    }
}
