package goals.context;

public record DrugContext(
    boolean isDoctorPresent,
    String professionalId
) {}