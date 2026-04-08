package tas.services.emergency;

import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import tas.goals.G10NotifyEmergency;
import reactor.core.publisher.Mono;

@Service
public class EmergencyAgent implements G10NotifyEmergency {

    private final WebClient webClient;

    public EmergencyAgent(WebClient.Builder builder) {
        this.webClient = builder.build();
    }

    @Override
    public Mono<FulfillmentStatus> execute(EmergencyContext context) {
        // The Agent evaluates the context to decide which Plan (P9 or P10) to execute
        
        if (context.severity() > 80.0) {
            System.out.println("High Severity: Selecting Plan P9");
            return executeP9CallAmbulance(context);
        } else {
            System.out.println("Moderate Severity: Selecting Plan P10");
            return executeP10SendSMS(context);
        }
    }

    // ==========================================
    // PLAN P9: Alarm Service
    // ==========================================
    private Mono<FulfillmentStatus> executeP9CallAmbulance(EmergencyContext context) {
        return webClient.post()
            .uri("http://hospital-api/ambulance/dispatch")
            .bodyValue(context)
            .retrieve()
            .bodyToMono(FulfillmentStatus.class)
            // If P9 fails, we adapt and immediately try P10 as a fallback
            .onErrorResume(error -> executeP10SendSMS(context)); 
    }

    // ==========================================
    // PLAN P10: Send SMS
    // ==========================================
    private Mono<FulfillmentStatus> executeP10SendSMS(EmergencyContext context) {
        return webClient.post()
            .uri("http://twilio-gateway/sms/send")
            .bodyValue(context)
            .retrieve()
            .bodyToMono(FulfillmentStatus.class);
    }
}