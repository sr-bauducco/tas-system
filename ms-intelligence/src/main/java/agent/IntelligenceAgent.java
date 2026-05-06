package agent;

import goals.definition.G6EnactMedicalSupport;
import goals.request.*;
import goals.context.EmergencyContext;
import api.FulfillmentStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Service
public class IntelligenceAgent implements G6EnactMedicalSupport {
    private static final Logger log = LoggerFactory.getLogger(IntelligenceAgent.class);
    private final WebClient.Builder webClientBuilder;

    public IntelligenceAgent(WebClient.Builder webClientBuilder) {
        this.webClientBuilder = webClientBuilder;
    }

    @Override
    public Mono<FulfillmentStatus> enact(VitalSign vitals) {
        log.info("[G6] Enacting support for Patient: {}", vitals.patientId());
        
        if (vitals.heartRate() > 100) {
            return triggerG10(vitals.patientId());
        }
        return Mono.empty(); 
    }

    private Mono<FulfillmentStatus> triggerG10(String patientId) {
        return webClientBuilder.build().post()
            .uri("http://ms-emergency/emergency/g10/execute")
            .bodyValue(new EmergencyRequest(
                patientId, 
                "Tachycardia", // The missing 2nd parameter
                new EmergencyContext(true, "Intelligence-G6")
            ))
            .retrieve()
            .bodyToMono(FulfillmentStatus.class);
    }
}