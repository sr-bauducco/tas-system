package goals.request;

import goals.context.EmergencyContext;

public record EmergencyRequest(
    String patientId,
    String alertType,
    EmergencyContext context
) {}