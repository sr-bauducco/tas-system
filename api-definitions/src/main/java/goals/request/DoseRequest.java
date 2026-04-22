package goals.request;

import goals.context.DoseContext;

public record DoseRequest(
    String patientId,
    double newDose,
    DoseContext context
) {}