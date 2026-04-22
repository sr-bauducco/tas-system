package goals;

public record EmergencyContext(
    boolean isInternetConnected,
    String provider
) {}