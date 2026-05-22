package gateway.filter;

import gateway.planner.GoalPlannerService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.cloud.gateway.filter.GlobalFilter;
import org.springframework.cloud.gateway.support.ServerWebExchangeUtils;
import org.springframework.core.Ordered;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

import java.net.URI;
import java.util.Set;
import java.util.stream.Collectors;

@Component
public class GoalDAdaptationFilter implements GlobalFilter, Ordered {

    private static final Logger log = LoggerFactory.getLogger(GoalDAdaptationFilter.class);
    private final GoalPlannerService planner;

    public GoalDAdaptationFilter(GoalPlannerService planner) {
        this.planner = planner;
    }

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        String targetGoal = exchange.getRequest().getHeaders().getFirst("X-Target-Goal");
        
        if (targetGoal != null) {
            // Monitor: Extract contexts (e.g., X-Context-C1_InternetConnection: true)
            Set<String> activeContexts = exchange.getRequest().getHeaders().entrySet().stream()
                    .filter(entry -> entry.getKey().startsWith("X-Context-") && "true".equalsIgnoreCase(entry.getValue().get(0)))
                    .map(entry -> entry.getKey().replace("X-Context-", ""))
                    .collect(Collectors.toSet());

            try {
                // Analyze & Plan
                String bestStrategyUri = planner.planBestRoute(targetGoal, activeContexts);
                
                // Execute: Dynamically rewrite the destination route
                URI newUri = URI.create(bestStrategyUri);
                exchange.getAttributes().put(ServerWebExchangeUtils.GATEWAY_REQUEST_URL_ATTR, newUri);
                
                log.info("GoalD Planner: Routed Goal [{}] to Strategy [{}] under contexts {}", targetGoal, newUri, activeContexts);
            } catch (Exception e) {
                log.error("GoalD Adaptation Failed: {}", e.getMessage());
                exchange.getResponse().setRawStatusCode(503); // Service Unavailable
                return exchange.getResponse().setComplete();
            }
        }

        return chain.filter(exchange);
    }

    @Override
    public int getOrder() {
        return 10000; // Run early in the filter chain
    }
}