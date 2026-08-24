package goals.definition;

import reactor.core.publisher.Mono;
import api.FulfillmentStatus;
import goals.request.DrugRequest;

/**
 * Goal Definition: G11 - Change Medication Drug.
 *
 * <p>Implementation of this goal is conditional on C3 (Doctor Present).
 * If the condition fails, it returns {@link api.Status#UNFEASIBLE} to trigger
 * adaptation towards G12.</p>
 *
 * @since GoalD 2.0
 */
public interface G11ChangeDrug {
    Mono<FulfillmentStatus> executeChangeDrug(DrugRequest request);
}