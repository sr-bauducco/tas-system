package agent;

import api.FulfillmentStatus;
import api.Status;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@RestController
@RequestMapping("/system/g0")
public class HealthSupportOrchestrator {

    private static final Logger log = LoggerFactory.getLogger(HealthSupportOrchestrator.class);
    private final WebClient webClient;

    public HealthSupportOrchestrator(WebClient.Builder webClientBuilder) {
        this.webClient = webClientBuilder.baseUrl("http://localhost:8080").build();
    }

    @PostMapping("/start/{patientId}")
    public Mono<FulfillmentStatus> startSystem(@PathVariable String patientId) {
        log.info("[G0] Bootstrapping TAS Root Goal for: {}", patientId);

        // G0 AND-Decomposition: G1 (Self-Diagnosed) AND G2 (Automated)[cite: 4]
        Mono<FulfillmentStatus> g1Mono = webClient.post()
                .uri("/monitor/g1/execute/" + patientId)
                .retrieve()
                .bodyToMono(FulfillmentStatus.class);

        Mono<FulfillmentStatus> g2Mono = webClient.post()
                .uri("/monitor/g2/execute/" + patientId)
                .retrieve()
                .bodyToMono(FulfillmentStatus.class);

        return Mono.zip(g1Mono, g2Mono)
                .map(tuple -> new FulfillmentStatus(Status.SUCCESS, "G0 Fully Realized. TAS Active."));
    }
}