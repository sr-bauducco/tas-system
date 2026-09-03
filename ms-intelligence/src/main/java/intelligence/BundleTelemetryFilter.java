package intelligence;

import api.TelemetryLogger;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ServerWebExchange;
import org.springframework.web.server.WebFilter;
import org.springframework.web.server.WebFilterChain;
import reactor.core.publisher.Mono;

import java.util.UUID;

@Component
public class BundleTelemetryFilter implements WebFilter {

    private static final Logger logger = LoggerFactory.getLogger(BundleTelemetryFilter.class);
    // Identificador fixo deste microserviço
    private final String bundleName = "ms-intelligence";

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, WebFilterChain chain) {
        long startTime = System.nanoTime();

        // Pega o Trace ID do cabeçalho que o gateway injetou
        String traceId = exchange.getRequest().getHeaders().getFirst("X-Trace-Id");
        if (traceId == null) {
            traceId = UUID.randomUUID().toString();
        }

        String finalTraceId = traceId;
        String endpoint = exchange.getRequest().getURI().getPath();

        logger.info("Bundle [{}] ATIVADO. Endpoint: {}", bundleName, endpoint);

        // chain.filter(exchange) retorna um Mono (assíncrono).
        // doFinally garante a execução no encerramento, seja em sucesso ou falha.
        return chain.filter(exchange).doFinally(signalType -> {
            long durationNs = System.nanoTime() - startTime;
            double durationMs = durationNs / 1_000_000.0;

            logger.info("Bundle [{}] DESATIVADO. Tempo ativo: {} ms", bundleName, durationMs);

            // Envia os dados para a telemetria em JSONL
            TelemetryLogger.logExecution(finalTraceId, bundleName, endpoint, durationMs);
        });
    }
}