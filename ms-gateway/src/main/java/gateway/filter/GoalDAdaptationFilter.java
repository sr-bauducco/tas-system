package gateway.filter;

import gateway.planner.GoalPlannerService;
import org.springframework.cloud.gateway.filter.GatewayFilter;
import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.http.HttpStatus;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;
import reactor.util.retry.Retry;
import java.time.Duration;
import java.net.URI;

public class GoalDAdaptationFilter implements GatewayFilter {

    private final GoalPlannerService plannerService;

    public GoalDAdaptationFilter(GoalPlannerService plannerService) {
        this.plannerService = plannerService;
    }

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        // 1. Extract Profile and Primary Goal Context
        String profile = exchange.getRequest().getHeaders().getFirst("X-Adaptation-Profile");
        if (profile == null) profile = "NO_ADAPTATION";

        // 2. Resolve Primary Route via DVM KnowledgeBase
        URI primaryRoute = plannerService.resolvePrimaryVE(exchange.getRequest());
        ServerWebExchange primaryExchange = mutateExchangeUri(exchange, primaryRoute);

        // 3. Apply Reactive Adaptation Strategy
        switch (profile.toUpperCase()) {
            case "RETRY":
                // TAS Exemplar: Retry twice before failing
                return chain.filter(primaryExchange)
                        .retryWhen(Retry.fixedDelay(2, Duration.ofMillis(200)));

            case "SELECT_RELIABLE":
                // TAS Exemplar: Select equivalent reliable service on failure
                return chain.filter(primaryExchange)
                        .onErrorResume(throwable -> {
                            // Trigger Analyze/Plan phase of MAPE-K loop
                            URI fallbackRoute = plannerService.resolveFallbackVE(exchange.getRequest(), primaryRoute);
                            if (fallbackRoute == null) {
                                return Mono.error(new RuntimeException("No reliable fallback available"));
                            }
                            ServerWebExchange fallbackExchange = mutateExchangeUri(exchange, fallbackRoute);
                            return chain.filter(fallbackExchange);
                        });

            case "NO_ADAPTATION":
            default:
                // Direct execution with zero fault tolerance
                return chain.filter(primaryExchange);
        }
    }

    private ServerWebExchange mutateExchangeUri(ServerWebExchange exchange, URI targetUri) {
        return exchange.mutate()
                .request(r -> r.uri(targetUri))
                .build();
    }
}