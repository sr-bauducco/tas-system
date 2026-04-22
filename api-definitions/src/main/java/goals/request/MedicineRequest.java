package goals.request;

import goals.context.*;

public record MedicineRequest(
    String patientId,
    String drugCode,
    double dose,
    DrugContext drugContext,
    DoseContext doseContext
) {
    public DrugRequest toDrugRequest() { return new DrugRequest(patientId, drugCode, drugContext); }
    public DoseRequest toDoseRequest() { return new DoseRequest(patientId, dose, doseContext); }
}