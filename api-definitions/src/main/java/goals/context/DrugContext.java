package goals.context;

/**
 * Context record for drug change operations.
 *
 * <p>Contains information about the professional currently in charge,
 * used to satisfy precondition C3 (doctor must be present for
 * {@link goals.definition.G11ChangeDrug} operations). This context
 * is evaluated by {@link DrugAgent} and injected through
 * {@link goals.request.DrugRequest} and {@link goals.request.MedicineRequest}.</p>
 *
 * @param isDoctorPresent flag indicating if a doctor is currently overseeing the patient
 * @param professionalId the unique identifier of the medical professional
 *
 * @since GoalD 2.0
 */
public record DrugContext(
    /** flag indicating if a doctor is currently overseeing the patient */
    boolean isDoctorPresent,
    /** the unique identifier of the medical professional */
    String professionalId
) {}