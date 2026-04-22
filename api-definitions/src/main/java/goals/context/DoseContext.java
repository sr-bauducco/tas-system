package goals.context;

public record DoseContext(
    boolean isDrugAdministered,
    double currentDose
) {}