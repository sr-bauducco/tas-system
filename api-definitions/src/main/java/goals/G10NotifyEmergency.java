package goals;

import reactor.core.publisher.Mono;
import api.FulfillmentStatus;

public interface G10NotifyEmergency {
    Mono<FulfillmentStatus> notifyEmergency(EmergencyRequest request);
}