package goals;

import reactor.core.publisher.Mono;
import api.FulfillmentStatus;

public interface G12ChangeDose {
    Mono<FulfillmentStatus> executeChangeDose(DoseRequest request);
}