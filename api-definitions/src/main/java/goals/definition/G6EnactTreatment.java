package goals.definition;

import api.FulfillmentStatus;
import goals.request.MedicineRequest; // Using your existing MedicineRequest
import reactor.core.publisher.Mono;

public interface G6EnactTreatment {
    /**
     * G6: Enact Treatment.
     * Tries G9; if unfeasible (C3/C4 fail), escalates to G10 tree.
     */
    Mono<FulfillmentStatus> enact(MedicineRequest request);
}