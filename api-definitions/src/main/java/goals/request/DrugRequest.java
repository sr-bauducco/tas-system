package goals.request;

import goals.context.DrugContext;

public record DrugRequest(
    String patientId,
    String newDrugCode,
    DrugContext context
) {}