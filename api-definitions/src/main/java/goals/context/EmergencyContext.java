package goals.context;

/**
 * Context record for emergency notification operations.
 *
 * <p>Contains environmental context regarding connectivity and service providers,
 * used by {@link agent.EmergencyAgent} (and G10/G4 goals) to select the
 * appropriate adaptation strategy (e.g., Alarm vs. SMS fallback).
 * This context is packaged in {@link goals.request.EmergencyRequest}.</p>
 *
 * @param isInternetConnected flag indicating if high-bandwidth internet connectivity is available
 * @param provider the identification string of the emergency service provider
 *
 * @since GoalD 2.0
 */
public record EmergencyContext(
    /** flag indicating if high-bandwidth internet connectivity is available */
    boolean isInternetConnected,
    /** the identification string of the emergency service provider */
    String provider
) {}