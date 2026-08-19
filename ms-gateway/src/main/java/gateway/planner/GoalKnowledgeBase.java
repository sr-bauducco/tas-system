package gateway.planner;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import java.util.concurrent.ConcurrentHashMap;

@Component
public class GoalKnowledgeBase {

    private static final Logger log = LoggerFactory.getLogger(GoalKnowledgeBase.class);
    
    // Thread-safe distributed context storage to prevent blocking during concurrent I/O
    private final ConcurrentHashMap<String, Boolean> activeContexts = new ConcurrentHashMap<>();

    public GoalKnowledgeBase() {
        // Initialize the baseline Contextual Goal Model environments (Ideal State)
        activeContexts.put("C1_InternetConnection", true);
        activeContexts.put("C3_DoctorPresent", true);
        activeContexts.put("C4_DrugAvailable", true);
        activeContexts.put("C7_InvasiveAllowed", true);
        
        log.info("[GoalD Knowledge Base] Initialized baseline environment.");
    }

    /**
     * Called asynchronously by the ms-monitor layer to update the state of the world.
     */
    public void updateContext(String contextId, boolean state) {
        activeContexts.put(contextId, state);
        log.warn("[MAPE-K Monitor] Context Shift: {} is now {}", contextId, state ? "ACTIVE" : "INACTIVE");
    }

    /**
     * Called by the GoalDAdaptationFilter (Analyze Phase) to evaluate routing viability.
     */
    public boolean isContextActive(String contextId) {
        return activeContexts.getOrDefault(contextId, false);
    }
}