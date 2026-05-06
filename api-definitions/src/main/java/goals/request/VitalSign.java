package goals.request; // This MUST be the first line

public record VitalSign(
    String patientId,
    double heartRate,
    double bloodPressure,
    long timestamp
) {}