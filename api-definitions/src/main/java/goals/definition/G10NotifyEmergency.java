package goals.definition;

import reactor.core.publisher.Mono;
import api.FulfillmentStatus;
import goals.request.EmergencyRequest;

public interface G10NotifyEmergency {
    Mono<FulfillmentStatus> notifyEmergency(EmergencyRequest request);
}