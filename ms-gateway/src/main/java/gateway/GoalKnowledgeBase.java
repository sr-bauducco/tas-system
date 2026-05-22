package gateway.planner;

import org.springframework.stereotype.Component;
import java.util.*;

@Component
public class GoalKnowledgeBase {

    public record Strategy(String serviceUri, List<String> requiredContexts, int qosScore) {}

    private final Map<String, List<Strategy>> dvm = new HashMap<>();

    public GoalKnowledgeBase() {
        // G4: Notify Emergency Medical Services
        dvm.put("G4_NotifyEmergency", List.of(
            new Strategy("lb://ms-emergency/emergency/alarm", List.of("C1_InternetConnection"), 25),
            new Strategy("lb://ms-emergency/emergency/sms", List.of(), 13) // Fallback
        ));
        
        // G8: Analyze Data (For future implementation)
        dvm.put("G8_AnalyzeData", List.of(
            new Strategy("lb://ms-intelligence/analyze/remote", List.of("C1_InternetConnection"), 30),
            new Strategy("lb://ms-intelligence/analyze/local", List.of(), 10)
        ));
    }

    public List<Strategy> getStrategiesForGoal(String goalId) {
        return dvm.getOrDefault(goalId, Collections.emptyList());
    }
}