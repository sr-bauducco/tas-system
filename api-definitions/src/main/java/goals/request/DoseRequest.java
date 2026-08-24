package goals.request;

import goals.context.DoseContext;

/**
 * Request record for modifying a patient's medication dose.
 *
 * <p>Used by {@link goals.definition.G12ChangeDose} to transport both the
 * new dosage amount and the environmental context required
 * for feasibility analysis (MAPE-K), specifically C4 (drug administered).
 * This record is often created as a fallback adaptation of a {@link MedicineRequest}.</p>
 *
 * @param patientId the ID of the patient receiving the dose change
 * @param newDose the new dosage amount (unit: mg/mcg)
 * @param context the environmental context (C4) required for this goal
 *
 * @see goals.context.DoseContext
 * @since GoalD 2.0
 */
public record DoseRequest(
    /** the ID of the patient receiving the dose change */
    String patientId,
    /** the new dosage amount (unit: mg/mcg) */
    double newDose,
    /** the environmental context (C4) required for this goal */
    DoseContext context
) {}