package api;

/**
 * Universal return signal for GoalD Agents to trigger adaptation.
 */
public record FulfillmentStatus(
    Status status,
    String message
) {}