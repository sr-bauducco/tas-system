package gateway.filter;

import gateway.planner.GoalPlannerService;
import org.springframework.cloud.gateway.filter.GatewayFilter;
import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.cloud.gateway.route.Route;
import org.springframework.cloud.gateway.support.ServerWebExchangeUtils;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;
import reactor.util.retry.Retry;

import java.net.URI;
import java.time.Duration;

public class GoalDAdaptationFilter implements GatewayFilter {

    private final GoalPlannerService plannerService;

    public GoalDAdaptationFilter(GoalPlannerService plannerService) {
        this.plannerService = plannerService;
    }

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        String profile = exchange.getRequest().getHeaders().getFirst("X-Adaptation-Profile");
        if (profile == null) {
            profile = "NO_ADAPTATION";
        }

        // 1. Resolve Primary Route
        URI primaryRoute = plannerService.resolvePrimaryVE(exchange.getRequest());
        mutateExchangeRoute(exchange, primaryRoute);

        // 2. Apply Reactive Strategy
        switch (profile.toUpperCase()) {
            case "RETRY":
                return chain.filter(exchange)
                        .retryWhen(Retry.fixedDelay(2, Duration.ofMillis(200)));

            case "SELECT_RELIABLE":
                return chain.filter(exchange)
                        .onErrorResume(throwable -> {
                            URI fallbackRoute = plannerService.resolveFallbackVE(exchange.getRequest(), primaryRoute);
                            if (fallbackRoute == null) {
                                return Mono.error(new RuntimeException("No fallback available"));
                            }
                            mutateExchangeRoute(exchange, fallbackRoute);
                            return chain.filter(exchange);
                        });

            case "NO_ADAPTATION":
            default:
                return chain.filter(exchange);
        }
    }

    /**
     * Rebuilds the Spring Cloud Gateway Route object dynamically.
     * This ensures RouteToRequestUrlFilter builds the physical HTTP URL correctly.
     */
    private void mutateExchangeRoute(ServerWebExchange exchange, URI targetUri) {
        Route originalRoute = exchange.getAttribute(ServerWebExchangeUtils.GATEWAY_ROUTE_ATTR);
        if (originalRoute != null) {
            Route newRoute = Route.async()
                    .id(originalRoute.getId())
                    .uri(targetUri)
                    .order(originalRoute.getOrder())
                    .asyncPredicate(originalRoute.getPredicate())
                    .filters(originalRoute.getFilters())
                    .build();
            exchange.getAttributes().put(ServerWebExchangeUtils.GATEWAY_ROUTE_ATTR, newRoute);
        }
    }
}