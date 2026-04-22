package goals;

public record EmergencyRequest(
    String patientId,
    String emergencyType,
    EmergencyContext context
) {}