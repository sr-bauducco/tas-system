package tas.system.treatment.agent;

import org.springframework.web.bind.annotation.*;
import org.springframework.web.reactive.function.client.WebClient;
import tas.system.api.goals.G12ChangeDose;
import reactor.core.publisher.Mono;
import java.time.Duration;
import java.time.Instant;

@RestController
@RequestMapping("/g12")
public class DoseAgent implements G12ChangeDose {

    private final WebClient pharmacyWebClient;

    public DoseAgent(WebClient.Builder builder) {
        // Points to an external Pharmacy API (Simulation or Real)
        this.pharmacyWebClient = builder.baseUrl("http://pharmacy-service:8090").build();
    }

    @PostMapping("/execute")
    @Override
    public Mono<FulfillmentStatus> execute(@RequestBody DoseContext context) {
        long startTime = Instant.now().toEpochMilli();

        // GoalD Logic: Execute P12, if failure or timeout, adapt to P13
        return executePlanP12(context)
            .timeout(Duration.ofSeconds(2)) // QoS Constraint: 2s max
            .onErrorResume(e -> {
                // Autonomic Adaptation Triggered by Latency or System Error
                return executePlanP13(context, e.getMessage());
            })
            .map(result -> {
                int latency = (int) (Instant.now().toEpochMilli() - startTime);
                return new FulfillmentStatus("SUCCESS", result, Instant.now().toEpochMilli(), latency);
            });
    }

    /**
     * PLAN P12: Automated Pharmacy Dispatch
     * This plan represents the primary path: High Precision, Lower Reliability (Network dependent).
     */
    private Mono<String> executePlanP12(DoseContext ctx) {
        return pharmacyWebClient.post()
            .uri("/dispense")
            .bodyValue(ctx)
            .retrieve()
            .bodyToMono(String.class)
            .map(res -> "P12_AUTOMATED_CONFIRMED: " + res);
    }

    /**
     * PLAN P13: Nurse Intervention Alert
     * This plan represents the fallback path: High Reliability, High Cost (Human effort).
     */
    private Mono<String> executePlanP13(DoseContext ctx, String reason) {
        // In a real scenario, this would call an SMS/Alert Gateway service
        return Mono.just("P13_MANUAL_INTERVENTION_TRIGGERED_DUE_TO_" + reason);
    }
}