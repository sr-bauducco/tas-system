package agent;

import api.FulfillmentStatus;
import api.Status;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@RestController
@RequestMapping("/monitor/g2")
public class AutomatedLifeSupportOrchestrator {

    private static final Logger log = LoggerFactory.getLogger(AutomatedLifeSupportOrchestrator.class);
    private final WebClient webClient;

    public AutomatedLifeSupportOrchestrator(WebClient.Builder webClientBuilder) {
        this.webClient = webClientBuilder.baseUrl("http://localhost:8080").build(); // Routes through MAPE-K
    }

    @PostMapping("/execute/{patientId}")
    public Mono<FulfillmentStatus> executeLifeSupport(@PathVariable String patientId) {
        log.info("[G2] Commencing Automated Life Support AND-Refinement for: {}", patientId);

        // G2 requires G5 (Monitor) AND G6 (Enact Treatment)
        Mono<FulfillmentStatus> monitorMono = webClient.post()
                .uri("/api/monitor")
                .header("X-Target-Goal", "G5_MonitorPatient")
                .retrieve()
                .bodyToMono(FulfillmentStatus.class)
                .onErrorResume(e -> Mono.just(new FulfillmentStatus(Status.FAILURE, "G5 Failed")));

        Mono<FulfillmentStatus> treatmentMono = webClient.post()
                .uri("/api/treatment")
                .header("X-Target-Goal", "G6_EnactTreatment")
                .retrieve()
                .bodyToMono(FulfillmentStatus.class)
                .onErrorResume(e -> Mono.just(new FulfillmentStatus(Status.FAILURE, "G6 Failed")));

        return Mono.zip(monitorMono, treatmentMono)
                .map(tuple -> new FulfillmentStatus(Status.SUCCESS, "G2 Automated Life Support Fulfilled"));
    }
}