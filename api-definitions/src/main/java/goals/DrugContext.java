package goals;

/**
 * Maps to Context C3 (Doctor is present).
 */
public record DrugContext(
    boolean isDoctorPresent,
    String professionalId
) {}