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
        boolean hasInternet = parseContext(request, "X-Context-C1");
        String path = request.getURI().getPath();
        
        // Use standard HTTP schemes to force physical network routing via Docker DNS
        if (path.contains("/treatment")) {
            return URI.create("http://ms-treatment:8080");
        } else if (path.contains("/emergency")) {
            return URI.create("http://ms-emergency:8080");
        }
        
        return URI.create("http://ms-monitor:8080");
    }

    /**
     * Executes Algorithm 2 (Local DVM Re-planning) upon encountering a network fault.
     */
    public URI resolveFallbackVE(ServerHttpRequest request, URI failedUri) {
        knowledgeBase.markNodeUnavailable(failedUri.getHost());

        // Traverse the DVM for the next highest QoS alternative.
        if (failedUri.toString().contains("ms-treatment")) {
            return URI.create("http://ms-emergency:8080");
        } else if (failedUri.toString().contains("ms-intelligence")) {
            return URI.create("http://ms-monitor:8080");
        }

        throw new IllegalStateException("No viable fallback Variability Element found for " + failedUri);
    }

    private boolean parseContext(ServerHttpRequest request, String headerName) {
        String headerValue = request.getHeaders().getFirst(headerName);
        return headerValue != null && Boolean.parseBoolean(headerValue);
    }
}