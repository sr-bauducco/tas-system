package goals;
import reactor.core.publisher.Mono;

public interface G12ChangeDose {
    // Immutable context for G12/P8
    record DoseContext(
        String patientId,
        double requestedDose,
        boolean isDrugAdministered // Maps to C4
    ) {}

    // Structured response for the MAPE-K loop
    record FulfillmentStatus(
        String status, 
        String planId, 
        String message
    ) {}

    Mono<FulfillmentStatus> execute(DoseContext context);
}