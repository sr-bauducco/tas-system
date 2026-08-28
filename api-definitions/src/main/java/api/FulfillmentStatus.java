/**
 * Universal return signal for GoalD Agents to trigger adaptation.
 *
 * <p>Every Goal execution in the GoalD 2.0 framework returns this record.
 * The {@link #status} field conveys whether the goal was satisfied, failed,
 * or deemed unfeasible given current environmental context (MAPE-K loop).
 * The {@link #message} provides human-readable context or trace information.</p>
 *
 * @param status the outcome of the goal execution (SUCCESS, FAILURE, UNFEASIBLE)
 * @param message an informative message describing the execution result or reason for unfeasibility
 *
 * @see Status
 * @since GoalD 2.0
 */
public record FulfillmentStatus(
    /** the outcome of the goal execution (SUCCESS, FAILURE, UNFEASIBLE) */
    Status status,
    /** an informative message describing the execution result or reason for unfeasibility */
    String message
) {}