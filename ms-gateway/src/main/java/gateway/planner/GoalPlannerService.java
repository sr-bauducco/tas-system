package gateway.planner;

import org.springframework.http.server.reactive.ServerHttpRequest;
import org.springframework.stereotype.Service;
import java.net.URI;

@Service
public class GoalPlannerService {

    private final GoalKnowledgeBase knowledgeBase;

    public GoalPlannerService(GoalKnowledgeBase knowledgeBase) {
        this.knowledgeBase = knowledgeBase;
    }

    /**
     * Executes Algorithm 1 (Initial DVM Synthesis) to find the primary route.
     */
    public URI resolvePrimaryVE(ServerHttpRequest request) {
        // 1. Extract context constraints from headers
        boolean hasInternet = parseContext(request, "X-Context-C1");
        
        // 2. Identify the requested goal based on the URI path
        String path = request.getURI().getPath();
        
        // 3. Map to the appropriate distributed microservice via Eureka (lb://)
        if (path.contains("/treatment")) {
            return URI.create("lb://ms-treatment");
        } else if (path.contains("/emergency")) {
            return URI.create("lb://ms-emergency");
        }
        
        // Default to monitoring
        return URI.create("lb://ms-monitor");
    }

    /**
     * Executes Algorithm 2 (Local DVM Re-planning) upon encountering a network fault.
     */
    public URI resolveFallbackVE(ServerHttpRequest request, URI failedUri) {
        // 1. Register the failure in the KnowledgeBase to invalidate the current VE
        knowledgeBase.markNodeUnavailable(failedUri.getHost());

        // 2. Traverse the DVM for the next highest QoS alternative.
        // For example, if ms-treatment fails, fallback to ms-emergency (Alarm Service).
        if (failedUri.toString().contains("ms-treatment")) {
            return URI.create("lb://ms-emergency");
        } else if (failedUri.toString().contains("ms-intelligence")) {
            // If remote analysis fails, fallback to local analysis inside ms-monitor
            return URI.create("lb://ms-monitor");
        }

        throw new IllegalStateException("No viable fallback Variability Element found for " + failedUri);
    }

    private boolean parseContext(ServerHttpRequest request, String headerName) {
        String headerValue = request.getHeaders().getFirst(headerName);
        return headerValue != null && Boolean.parseBoolean(headerValue);
    }
}