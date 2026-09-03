package emergency;

import api.TelemetryLogger;
import org.springframework.web.server.ServerWebExchange;
import org.springframework.web.server.WebFilter;
import org.springframework.web.server.WebFilterChain;
import reactor.core.publisher.Mono;

import java.util.Map;

public class BundleTelemetryFilter implements WebFilter {
    @Override
    public Mono<Void> filter(ServerWebExchange exchange, WebFilterChain chain) {
        String path = exchange.getRequest().getPath().value();

        if (path.startsWith("/actuator") || path.equals("/error")) {
            return chain.filter(exchange);
        }

        long start = TelemetryLogger.simulationTime(
            exchange.getRequest().getHeaders().getFirst("X-Simulation-Time-Ms"));

        return chain.filter(exchange)
            .doFinally(signal -> {
                String endHeader = exchange.getRequest().getHeaders()
                    .getFirst("X-Simulation-End-Time-Ms");

                long end = endHeader == null
                    ? start
                    : TelemetryLogger.simulationTime(endHeader);

                TelemetryLogger.logBundle(
                    path,
                    start,
                    end,
                    Map.of(
                        "scenario", header(exchange, "X-Scenario", "1"),
                        "execIndex", header(exchange, "X-Exec-Index", "1"),
                        "plotIndex", header(exchange, "X-Plot-Index", "-1")
                    )
                );
            });
    }

    private static String header(
            ServerWebExchange exchange, String name, String fallback) {
        String value = exchange.getRequest().getHeaders().getFirst(name);
        return value == null ? fallback : value;
    }
}