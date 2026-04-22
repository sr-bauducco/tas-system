package goals;

import reactor.core.publisher.Mono;
import api.FulfillmentStatus; // Assuming FulfillmentStatus is in the 'api' folder

public interface G11ChangeDrug {
    Mono<FulfillmentStatus> executeChangeDrug(DrugRequest request);
}