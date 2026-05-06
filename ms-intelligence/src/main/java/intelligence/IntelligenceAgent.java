package agent;

import goals.definition.G6AnalyzeData;
import goals.request.VitalSign;
import goals.request.EmergencyRequest;
import goals.context.EmergencyContext;
import api.FulfillmentStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Service
public class IntelligenceAgent implements G6AnalyzeData {
    private static final Logger log = LoggerFactory.getLogger(IntelligenceAgent.class);
    private final WebClient.Builder webClientBuilder;

    public IntelligenceAgent(WebClient.Builder webClientBuilder) {
        this.webClientBuilder = webClientBuilder;
    }

    @Override
    public Mono<FulfillmentStatus> analyze(VitalSign vitals) {
        log.info("[G6] Analyzing: Patient={}, HR={}, BP={}", 
                 vitals.patientId(), vitals.heartRate(), vitals.bloodPressure());
        
        // GORE logic: If Heart Rate > 100, trigger G10 (Emergency)
        if (vitals.heartRate() > 100) {
            log.warn("[G6] ALERT: Tachycardia detected (>100). Triggering G10!");
            return triggerEmergency(vitals.patientId());
        }
        
        return Mono.empty(); 
    }

    private Mono<FulfillmentStatus> triggerEmergency(String patientId) {
        return webClientBuilder.build().post()
            .uri("http://ms-emergency/emergency/g10/execute") // Service discovery name
            .bodyValue(new EmergencyRequest(patientId, new EmergencyContext(true, "Intelligence-G6")))
            .retrieve()
            .bodyToMono(FulfillmentStatus.class)
            .doOnSuccess(res -> log.info("[G6] G10 Execution Result: {}", res.status()));
    }
}