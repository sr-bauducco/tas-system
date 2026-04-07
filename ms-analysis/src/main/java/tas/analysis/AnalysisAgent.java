package tas.analysis;

import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import tas.goals.G1GetVitalParams;
import tas.goals.G1GetVitalParams.Vitals;
import tas.goals.G10NotifyEmergency;
import tas.goals.G10NotifyEmergency.EmergencyContext;
import tas.goals.G10NotifyEmergency.FulfillmentStatus;
import jakarta.annotation.PostConstruct;
import reactor.core.publisher.Mono;

@Service
public class AnalysisAgent {

    private final WebClient monitorClient;
    private final WebClient emergencyClient;

    public AnalysisAgent(WebClient.Builder builder) {
        this.monitorClient = builder.baseUrl("http://localhost:8081").build();
        this.emergencyClient = builder.baseUrl("http://localhost:8080").build();
    }

    @PostConstruct
    public void initiateAutonomicLoop() {
        // MAPE-K Loop: 1. MONITOR (G1)
        monitorClient.get()
            .uri("/monitor/patient-01")
            .retrieve()
            .bodyToFlux(Vitals.class)
            .flatMap(vitals -> {
                // 2. ANALYZE (G6 logic)
                if (vitals.heartRate() > 100) {
                    System.out.println("CRITICAL: HR " + vitals.heartRate());
                    // 3. EXECUTE (G10)
                    return triggerEmergency(vitals);
                }
                return Mono.empty();
            })
            .subscribe(); 
    }

    private Mono<FulfillmentStatus> triggerEmergency(Vitals vitals) {
        var context = new EmergencyContext(vitals.patientId(), "Tachycardia", vitals.heartRate());
        return emergencyClient.post()
            .uri("/notify")
            .bodyValue(context)
            .retrieve()
            .bodyToMono(FulfillmentStatus.class)
            .doOnSuccess(s -> System.out.println("Emergency Response: " + s.status()));
    }
}