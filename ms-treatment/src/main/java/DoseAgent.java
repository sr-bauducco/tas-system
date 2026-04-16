package unb.tg.treatment.agent;

import org.springframework.web.bind.annotation.*;
import unb.tg.api.goals.G12ChangeDose;
import reactor.core.publisher.Mono;
import java.time.Duration;
import java.time.Instant;

@RestController
@RequestMapping("/g12")
public class DoseAgent implements G12ChangeDose {

    @PostMapping("/execute")
    @Override
    public Mono<FulfillmentStatus> execute(@RequestBody DoseContext context) {
        long startTime = Instant.now().toEpochMilli();

        // Branch based on Context Condition C1 (Connection)
        return Mono.just(context.connectionAvailable())
            .flatMap(online -> {
                if (online) {
                    // Try Plan P12 (Automated) with QoS enforcement
                    return executePlanP12(context)
                        .timeout(Duration.ofSeconds(2)) // QoS: max 2s response
                        .onErrorResume(e -> executePlanP13(context, "P12_TIMEOUT"));
                } else {
                    // C1 is false: Direct fallback to Plan P13 (Manual/Offline)
                    return executePlanP13(context, "CONNECTION_OFFLINE");
                }
            })
            .map(plan -> new FulfillmentStatus(
                "SUCCESS", 
                plan, 
                Instant.now().toEpochMilli(), 
                (int)(Instant.now().toEpochMilli() - startTime)
            ));
    }

    /**
     * Plan P12: Automated Pharmacy Update (Reactive WebClient call)
     */
    private Mono<String> executePlanP12(DoseContext ctx) {
        // Logic would typically use WebClient to call the external Pharmacy service
        return Mono.just("P12_AUTOMATED_PHARMACY_API");
    }

    /**
     * Plan P13: Manual Intervention Alert (Fallback Strategy)
     */
    private Mono<String> executePlanP13(DoseContext ctx, String reason) {
        // Logic to alert a nurse via SMS or local console
        return Mono.just("P13_MANUAL_INTERVENTION_TRIGGERED");
    }
}