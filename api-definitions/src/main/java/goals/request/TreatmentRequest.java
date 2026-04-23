package goals.request;

import goals.context.TreatmentContext;

/**
 * Reuses existing MedicineRequest as the payload for EnactTreatment.
 */
public record TreatmentRequest(
    TreatmentContext context,
    MedicineRequest medicineRequest // REUSE: Use your existing implemented record
) {
    public MedicineRequest toMedicineRequest() { 
        return medicineRequest; 
    }

    public EmergencyRequest toEmergencyRequest() { 
        // Mapping to your existing EmergencyRequest signature: 
        // required: java.lang.String (id), java.lang.String (desc), EmergencyContext
        return new EmergencyRequest(
            medicineRequest.patientId(), // Reuse ID from existing request
            "G6 Escalation", 
            context.toEmergencyContext() // We'll add this helper to TreatmentContext
        );
    }
}