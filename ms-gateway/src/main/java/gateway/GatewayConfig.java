package gateway;

import gateway.filter.GoalDAdaptationFilter;
import gateway.planner.GoalPlannerService;
import org.springframework.cloud.gateway.route.RouteLocator;
import org.springframework.cloud.gateway.route.builder.RouteLocatorBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class GatewayConfig {

    private final GoalPlannerService plannerService;

    public GatewayConfig(GoalPlannerService plannerService) {
        this.plannerService = plannerService;
    }

    @Bean
    public RouteLocator customRouteLocator(RouteLocatorBuilder builder) {
        GoalDAdaptationFilter adaptationFilter = new GoalDAdaptationFilter(plannerService);

        return builder.routes()
                .route("goald_health_support_route", r -> r
                        .path("/api/v1/health-support/**")
                        .filters(f -> f.filter(adaptationFilter))
                        // The filter determines the actual dynamic URI, but Spring requires a default placeholder
                        .uri("no://op")) 
                .build();
    }
}