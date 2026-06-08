package agent;

import api.FulfillmentStatus;
import api.Status;
import goals.request.EmergencyRequest;
import goals.context.EmergencyContext;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@RestController
@RequestMapping("/monitor/g1")
public class SelfDiagnosedOrchestrator {

    private static final Logger log = LoggerFactory.getLogger(SelfDiagnosedOrchestrator.class);
    private final PushButtonAgent pushButtonAgent;
    private final WebClient.Builder webClientBuilder;

    public SelfDiagnosedOrchestrator(PushButtonAgent pushButtonAgent, WebClient.Builder webClientBuilder) {
        this.pushButtonAgent = pushButtonAgent;
        this.webClientBuilder = webClientBuilder;
    }

    @PostMapping("/execute/{patientId}")
    public Mono<FulfillmentStatus> executeSelfDiagnosis(@PathVariable String patientId) {
        log.info("[G1] Commencing Self-Diagnosed Emergency Support for: {}", patientId);

        // Step 1: Ensure G3 (Push Button) is fulfilled
        return pushButtonAgent.registerButtonPress(patientId)
            .flatMap(g3Result -> {
                if (g3Result.status() == Status.SUCCESS) {
                    
                    // Step 2: Route G4 through the GoalD MAPE-K Gateway
                    log.info("[G1] G3 Fulfilled. Triggering G4 via MAPE-K Gateway...");
                    return webClientBuilder.build().post()
                        // Note: Routes through ms-gateway (8080) to allow context analysis!
                        .uri("http://localhost:8080/") 
                        .header("X-Target-Goal", "G4_NotifyEmergency")
                        .bodyValue(new EmergencyRequest(patientId, "Panic Button Pressed", new EmergencyContext(true, "Wearable")))
                        .retrieve()
                        .bodyToMono(FulfillmentStatus.class);
                }
                return Mono.just(new FulfillmentStatus(Status.FAILURE, "G3 Push Button Failed"));
            });
    }
}