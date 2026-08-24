package goals.request;

import goals.context.DrugContext;

/**
 * Request record for changing a patient's medication.
 *
 * <p>Used by {@link goals.definition.G11ChangeDrug} to transport both the
 * technical target (drug code) and the environmental context required
 * for feasibility analysis (MAPE-K).</p>
 *
 * @param patientId the ID of the patient receiving the change
 * @param newDrugCode the unique code of the medication to be administered
 * @param context the professional context (C3: Doctor Presence) required for this goal
 *
 * @see goals.context.DrugContext
 * @since GoalD 2.0
 */
public record DrugRequest(
    /** the ID of the patient receiving the change */
    String patientId,
    /** the unique code of the medication to be administered */
    String newDrugCode,
    /** the professional context (C3: Doctor Presence) required for this goal */
    DrugContext context
) {}