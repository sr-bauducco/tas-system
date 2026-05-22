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
            // Monitor: Extract contexts
            Set<String> activeContexts = exchange.getRequest().getHeaders().entrySet().stream()
                    .filter(entry -> entry.getKey().startsWith("X-Context-") && "true".equalsIgnoreCase(entry.getValue().get(0)))
                    .map(entry -> entry.getKey().replace("X-Context-", ""))
                    .collect(Collectors.toSet());

            try {
                // Analyze & Plan (e.g., returns "lb://ms-emergency/emergency/sms")
                String bestStrategyUriString = planner.planBestRoute(targetGoal, activeContexts);
                URI bestStrategyUri = URI.create(bestStrategyUriString);

                log.info("GoalD Planner: Dynamically routing to [{}]", bestStrategyUri);

                // Execute Step 1: Mutate the request path for internal Spring logging
                org.springframework.http.server.reactive.ServerHttpRequest mutatedRequest = 
                        exchange.getRequest().mutate().path(bestStrategyUri.getPath()).build();

                // THE FIX: Execute Step 2: Set the FULL URI (Host + Path) for the Load Balancer!
                exchange.getAttributes().put(ServerWebExchangeUtils.GATEWAY_REQUEST_URL_ATTR, bestStrategyUri);

                // Execute Step 3: Pass down the chain
                return chain.filter(exchange.mutate().request(mutatedRequest).build());

            } catch (Exception e) {
                log.error("GoalD Adaptation Failed: {}", e.getMessage());
                exchange.getResponse().setRawStatusCode(503); 
                return exchange.getResponse().setComplete();
            }
        }

        return chain.filter(exchange);
    }

    @Override
    public int getOrder() {
        // Run right after RouteToRequestUrlFilter (10000) but before LoadBalancer (10150)
        return 10001; 
    }
}