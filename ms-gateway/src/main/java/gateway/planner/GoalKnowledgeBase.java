package gateway.planner;

import org.springframework.stereotype.Component;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Component
public class GoalKnowledgeBase {

    // Simulates the Context-VE Map from the GoalD architecture
    private final Map<String, Boolean> nodeAvailability = new ConcurrentHashMap<>();

    public GoalKnowledgeBase() {
        // Initialize default distributed components as available
        nodeAvailability.put("ms-treatment", true);
        nodeAvailability.put("ms-emergency", true);
        nodeAvailability.put("ms-monitor", true);
        nodeAvailability.put("ms-intelligence", true);
    }

    /**
     * Updates the Knowledge Base when a node drops off the network or fails a health check.
     * This directly maps to updating the Context-VE Map in GoalD.
     *
     * @param nodeId The hostname of the failed microservice.
     */
    public void markNodeUnavailable(String nodeId) {
        if (nodeId != null) {
            // Thread-safe mutation of the operational context
            nodeAvailability.put(nodeId, false);
            System.out.println("[MAPE-K: ANALYZE] Node marked unavailable in KnowledgeBase: " + nodeId);
        }
    }

    /**
     * Checks the DVM state to see if a specific component is currently viable.
     */
    public boolean isNodeAvailable(String nodeId) {
        return nodeAvailability.getOrDefault(nodeId, false);
    }

    /**
     * Restores a node's availability in the DVM, typically called by a health-check polling mechanism
     * or Eureka registry heartbeat sync.
     */
    public void restoreNode(String nodeId) {
        if (nodeId != null) {
            nodeAvailability.put(nodeId, true);
            System.out.println("[MAPE-K: ANALYZE] Node restored in KnowledgeBase: " + nodeId);
        }
    }
}