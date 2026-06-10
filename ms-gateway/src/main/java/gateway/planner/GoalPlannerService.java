package gateway.planner;

import org.springframework.stereotype.Service;
import java.util.List;
import java.util.Set;

@Service
public class GoalPlannerService {

    private final GoalKnowledgeBase knowledgeBase;

    public GoalPlannerService(GoalKnowledgeBase knowledgeBase) {
        this.knowledgeBase = knowledgeBase;
    }

    public String planBestRoute(String goalId, Set<String> activeContexts) {
        List<GoalKnowledgeBase.Strategy> alternatives = knowledgeBase.getStrategiesForGoal(goalId);

        return alternatives.stream()
                // Analyze: Keep only strategies where all required contexts are currently active
                .filter(strategy -> activeContexts.containsAll(strategy.requiredContexts()))
                // Plan: Sort by highest QoS score
                .max((s1, s2) -> Integer.compare(s1.qosScore(), s2.qosScore()))
                .map(GoalKnowledgeBase.Strategy::serviceUri)
                .orElseThrow(() -> new RuntimeException("System Unavailable: No achievable strategy for goal " + goalId));
    }
}