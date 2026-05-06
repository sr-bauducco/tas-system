package goals.request;

public record VitalSign(
    String patientId,
    double heartRate,
    double bloodPressure,
    long timestamp
) {}