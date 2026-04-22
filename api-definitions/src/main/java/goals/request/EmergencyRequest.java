package goals.request;

import goals.context.EmergencyContext;

public record EmergencyRequest(
    String patientId,
    String emergencyType,
    EmergencyContext context
) {}