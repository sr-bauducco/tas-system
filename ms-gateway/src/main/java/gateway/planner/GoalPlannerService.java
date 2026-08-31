package gateway.planner;

import api.TelemetryLogger; // <--- Importe o logger
import org.springframework.http.server.reactive.ServerHttpRequest;
import org.springframework.stereotype.Service;
import java.net.URI;

@Service
public class GoalPlannerService {

    private final GoalKnowledgeBase knowledgeBase;

    public GoalPlannerService(GoalKnowledgeBase knowledgeBase) {
        this.knowledgeBase = knowledgeBase;
    }

    public URI resolvePrimaryVE(ServerHttpRequest request) {
        String path = request.getURI().getPath();
        
        if (path.contains("/treatment")) {
            TelemetryLogger.logEvent("GoalPlanner", "bundle", "EnactTreatment-impl", "start");
            URI uri = URI.create("http://ms-treatment:8080");
            TelemetryLogger.logEvent("GoalPlanner", "bundle", "EnactTreatment-impl", "end");
            return uri;
        } else if (path.contains("/emergency")) {
            TelemetryLogger.logEvent("GoalPlanner", "bundle", "AlarmService-impl", "start");
            URI uri = URI.create("http://ms-emergency:8080");
            TelemetryLogger.logEvent("GoalPlanner", "bundle", "AlarmService-impl", "end");
            return uri;
        }
        
        // CORREÇÃO PARA A RAIZ (/): Aponta para o monitor ou retorna o próprio gateway para testes de Uptime
        return URI.create("http://ms-monitor:8080");
    }

    private boolean parseContext(ServerHttpRequest request, String headerName) {
        String val = request.getHeaders().getFirst(headerName);
        return val == null || Boolean.parseBoolean(val);
    }
}