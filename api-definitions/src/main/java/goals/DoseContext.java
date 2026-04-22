package goals;

public record DoseContext(
    boolean isDrugAdministered,
    double currentDose
) {}