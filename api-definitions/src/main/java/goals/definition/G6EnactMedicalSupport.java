package goals.definition;

import goals.request.VitalSign;
import reactor.core.publisher.Mono;
import api.FulfillmentStatus;

public interface G6EnactMedicalSupport {
    // Fulfilling G6: Enact medical support
    Mono<FulfillmentStatus> enact(VitalSign vitals); 
}