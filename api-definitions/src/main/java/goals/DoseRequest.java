package goals;

public record DoseRequest(
    String patientId,
    double newDose,
    DoseContext context
) {}