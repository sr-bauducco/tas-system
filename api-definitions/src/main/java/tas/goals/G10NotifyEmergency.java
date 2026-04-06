package tas.goals;
import reactor.core.publisher.Mono;

public interface G10NotifyEmergency {
    record EmergencyContext(String patientId, String alertType, double severity) {}
    record FulfillmentStatus(String status, String providerId) {}
    Mono<FulfillmentStatus> execute(EmergencyContext context);
}
