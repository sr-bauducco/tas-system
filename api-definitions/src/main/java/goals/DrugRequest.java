package goals;

public record DrugRequest(
    String patientId,
    String newDrugCode,
    DrugContext context
) {}