package goals.definition;

import reactor.core.publisher.Mono;
import api.FulfillmentStatus;
import goals.request.DoseRequest;

public interface G12ChangeDose {
    Mono<FulfillmentStatus> executeChangeDose(DoseRequest request);
}