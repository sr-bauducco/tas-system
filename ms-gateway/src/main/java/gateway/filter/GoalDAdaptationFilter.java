package gateway.filter;

import api.TelemetryLogger; // <--- Importe o logger
import gateway.planner.GoalPlannerService;
import org.springframework.cloud.gateway.filter.GatewayFilter;
import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

public class GoalDAdaptationFilter implements GatewayFilter {

    private final GoalPlannerService plannerService;

    public GoalDAdaptationFilter(GoalPlannerService plannerService) {
        this.plannerService = plannerService;
    }

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        // Marca o sistema como disponível ao iniciar o fluxo da requisição
        TelemetryLogger.logEvent("GatewayFilter", "system", "system_available", "start");

        return chain.filter(exchange)
            .doOnSuccess(v -> {
                TelemetryLogger.logEvent("GatewayFilter", "system", "system_available", "end");
            })
            .doOnError(throwable -> {
                // Se houver falha na chamada do microserviço, registra a indisponibilidade
                TelemetryLogger.logEvent("GatewayFilter", "failure", "system_unavailable", "start");
                TelemetryLogger.logEvent("GatewayFilter", "failure", "system_unavailable", "end");
            });
    }
}