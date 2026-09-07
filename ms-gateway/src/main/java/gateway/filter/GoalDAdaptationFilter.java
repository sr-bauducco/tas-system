package gateway.filter;

import api.TelemetryLogger;
import gateway.planner.GoalPlannerService;
import org.springframework.cloud.gateway.filter.GatewayFilter;
import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

import java.util.UUID;

public class GoalDAdaptationFilter implements GatewayFilter {

    private final GoalPlannerService plannerService;

    public GoalDAdaptationFilter(GoalPlannerService plannerService) {
        this.plannerService = plannerService;
    }

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        
        // 1. Gera o Trace ID unificado para este ciclo de adaptação
        String traceId = UUID.randomUUID().toString();

        // 2. Injeta o Trace ID no cabeçalho para propagar aos próximos microserviços
        ServerWebExchange mutatedExchange = exchange.mutate()
            .request(r -> r.header("X-Trace-Id", traceId))
            .build();

        // 3. Captura o tempo inicial
        long startTime = System.nanoTime();
        String endpoint = mutatedExchange.getRequest().getURI().getPath();

        // Mantém seu log original
        TelemetryLogger.logEvent("GatewayFilter", "system", "system_available", "start");

        // Passa a requisição mutada (com o header) adiante
        return chain.filter(mutatedExchange)
            .doOnSuccess(v -> {
                long durationNs = System.nanoTime() - startTime;
                double durationMs = durationNs / 1_000_000.0;
                
                TelemetryLogger.logEvent("GatewayFilter", "system", "system_available", "end");
                
                // Grava a telemetria em JSON para o Python ler depois
                TelemetryLogger.logExecution(traceId, "ms-gateway", endpoint, durationMs);
            })
            .doOnError(throwable -> {
                long durationNs = System.nanoTime() - startTime;
                double durationMs = durationNs / 1_000_000.0;
                
                TelemetryLogger.logEvent("GatewayFilter", "failure", "system_unavailable", "start");
                TelemetryLogger.logEvent("GatewayFilter", "failure", "system_unavailable", "end");
                
                // Grava a telemetria de erro
                TelemetryLogger.logExecution(traceId, "ms-gateway-error", endpoint, durationMs);
            });
    }
}