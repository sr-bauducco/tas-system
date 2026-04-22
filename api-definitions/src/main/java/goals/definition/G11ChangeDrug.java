package goals.definition;

import reactor.core.publisher.Mono;
import api.FulfillmentStatus;
import goals.request.DrugRequest;

public interface G11ChangeDrug {
    Mono<FulfillmentStatus> executeChangeDrug(DrugRequest request);
}