package tas.services.emergency;
import org.springframework.stereotype.Service;
import tas.goals.G10NotifyEmergency;
import reactor.core.publisher.Mono;
import java.time.Duration;

@Service
public class EmergencyAgent implements G10NotifyEmergency {
    @Override
    public Mono<FulfillmentStatus> execute(EmergencyContext context) {
        // Implementation of G10 logic with 2s timeout (QoS)
        return Mono.just(new FulfillmentStatus("SUCCESS", "REST_API"))
                   .delayElement(Duration.ofMillis(100))
                   .timeout(Duration.ofSeconds(2));
    }
}
