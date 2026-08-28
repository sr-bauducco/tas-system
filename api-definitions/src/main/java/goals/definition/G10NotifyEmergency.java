package goals.definition;

import reactor.core.publisher.Mono;
import api.FulfillmentStatus;
import goals.request.EmergencyRequest;

/**
 * Goal Definition: G10 - Notify Emergency.
 *
 * <p>This goal triggers emergency notification services. The {@code ms-gateway}
 * analyzes context (C1: Internet) before routing to either the Alarm Service (high QoS)
 * or SMS Service (fallback).</p>
 *
 * @since GoalD 2.0
 */
public interface G10NotifyEmergency {
    Mono<FulfillmentStatus> notifyEmergency(EmergencyRequest request);
}