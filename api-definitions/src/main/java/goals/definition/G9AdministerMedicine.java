package goals.definition;

import reactor.core.publisher.Mono;
import api.FulfillmentStatus;
import goals.request.MedicineRequest;

public interface G9AdministerMedicine {
    Mono<FulfillmentStatus> administerMedicine(MedicineRequest request);
}