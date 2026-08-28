package goals.definition;

import reactor.core.publisher.Mono;
import api.FulfillmentStatus;
import goals.request.MedicineRequest;

/**
 * Goal Definition: G9 - Administer Medicine.
 *
 * <p>This goal orchestrates the end-to-end medication administration sequence,
 * coordinating between the Drug Agent and Dose Agent. If G11 (change drug) is
 * unfeasible (e.g. C3 violation), it adaptively falls back to G12 (change dose).
 *
 * @since GoalD 2.0
 */
public interface G9AdministerMedicine {
    Mono<FulfillmentStatus> administerMedicine(MedicineRequest request);
}