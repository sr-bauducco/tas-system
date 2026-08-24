package goals.context;

/**
 * Context record for medication dose modifications.
 *
 * <p>Carries the state needed by {@link goals.definition.G12ChangeDose}
 * and {@link goals.definition.G11ChangeDrug} to evaluate whether a dose
 * or drug change is feasible under the current context (e.g. C4: has the
 * drug already been administered?).</p>
 *
 * @param isDrugAdministered flag indicating whether a drug has already been administered to the patient
 * @param currentDose the most recent administered dose value (unit: mg or mcg, depends on medication)
 *
 * @since GoalD 2.0
 */
public record DoseContext(
    /** flag indicating whether a drug has already been administered to the patient */
    boolean isDrugAdministered,
    /** the most recent administered dose value (unit: mg or mcg, depends on medication) */
    double currentDose
) {}