package goals.request;

import goals.context.EmergencyContext;

/**
 * Request record for triggering emergency notification services.
 *
 * <p>Used by {@link goals.definition.G10NotifyEmergency} (and G4) to
 * communicate an emergency event. It carries environmental context regarding
 * connectivity (C1) to allow the {@code ms-gateway} to select the
 * appropriate notification strategy (Alarm vs. SMS). This record is consumed
 * by the emergency agents (e.g., {@code ms-emergency}).</p>
 *
 * @param patientId the ID of the patient involved in the emergency
 * @param alertType a descriptive string of the type of emergency (e.g. "Tachycardia", "Panic Button")
 * @param context the environmental context (C1) required for strategy selection
 *
 * @see goals.context.EmergencyContext
 * @since GoalD 2.0
 */
public record EmergencyRequest(
    /** the ID of the patient involved in the emergency */
    String patientId,
    /** a descriptive string of the type of emergency (e.g. "Tachycardia", "Panic Button") */
    String alertType,
    /** the environmental context (C1) required for strategy selection */
    EmergencyContext context
) {}