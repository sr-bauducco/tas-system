package gateway.filter;

import gateway.planner.GoalKnowledgeBase;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.cloud.gateway.filter.GlobalFilter;
import org.springframework.core.Ordered;
import org.springframework.http.server.reactive.ServerHttpRequest;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

import java.net.URI;

@Component
public class GoalDAdaptationFilter implements GlobalFilter, Ordered {

    private static final Logger log = LoggerFactory.getLogger(GoalDAdaptationFilter.class);
    
    // 1. Explicitly declare the Knowledge Base dependency
    private final GoalKnowledgeBase knowledgeBase;

    // 2. Inject it via the constructor (Spring IoC)
    public GoalDAdaptationFilter(GoalKnowledgeBase knowledgeBase) {
        this.knowledgeBase = knowledgeBase;
    }

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        ServerHttpRequest request = exchange.getRequest();
        String targetGoal = request.getHeaders().getFirst("X-Target-Goal");

        if (targetGoal == null || targetGoal.isEmpty()) {
            return chain.filter(exchange);
        }

        log.info("[MAPE-K] Intercepted routing request for Goal: {}", targetGoal);
        
        // MAPE-K: Analyze Phase
        boolean hasInternet = knowledgeBase.isContextActive("C1_InternetConnection");
        boolean hasDoctor = knowledgeBase.isContextActive("C3_DoctorPresent");
        
        // MAPE-K: Plan Phase - Map goal to Eureka Load-Balanced (lb://) URL
        URI routedUri = resolveStrategy(targetGoal, hasInternet, hasDoctor, request.getURI());
        
        if (routedUri != null) {
            ServerHttpRequest mutatedRequest = request.mutate().uri(routedUri).build();
            log.info("[MAPE-K Plan] Routed Goal {} -> Strategy {}", targetGoal, routedUri);
            return chain.filter(exchange.mutate().request(mutatedRequest).build());
        }

        // Safe fallback if strategy is unresolvable
        return chain.filter(exchange);
    }

    private URI resolveStrategy(String goal, boolean hasInternet, boolean hasDoctor, URI originalUri) {
        // Evaluate the context for the Invasive sensor strategy
        boolean invasiveAllowed = knowledgeBase.isContextActive("C7_InvasiveAllowed");

        // We use 'lb://' so Spring Cloud LoadBalancer resolves the physical IP from Eureka[cite: 3]
        return switch (goal) {
            case "G7_GetVitalParams" -> invasiveAllowed
                ? URI.create("lb://ms-monitor/monitor/g7/invasive") 
                : URI.create("lb://ms-monitor/monitor/g7/noninvasive");

            case "G8_AnalyzeData" -> hasInternet 
                ? URI.create("lb://ms-intelligence/intelligence/g8/remote") 
                : URI.create("lb://ms-intelligence/intelligence/g8/local");
                
            case "G4_NotifyEmergency" -> hasInternet 
                ? URI.create("lb://ms-emergency/emergency/g4/alarm") 
                : URI.create("lb://ms-emergency/emergency/g4/sms");

            case "G10_NotifyEmergency" -> hasInternet 
                ? URI.create("lb://ms-emergency/emergency/g10/alarm") 
                : URI.create("lb://ms-emergency/emergency/g10/sms");
                
            case "G11_ChangeDrug" -> hasDoctor 
                ? URI.create("lb://ms-treatment/treatment/g11/execute") 
                : null; // Null aborts routing if context condition fails
                
            default -> originalUri;
        };
    }

    @Override
    public int getOrder() { 
        return -100; // Ensure this runs early to rewrite the URI before standard routing
    }
}