package goals.context;

public record EmergencyContext(
    boolean isInternetConnected,
    String provider
) {}