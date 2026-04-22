package goals;

import reactor.core.publisher.Mono;
import api.FulfillmentStatus;

public interface G11ChangeDrug {
    Mono<FulfillmentStatus> executeChangeDrug(DrugRequest request);
}