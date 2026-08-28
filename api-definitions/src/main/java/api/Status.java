/**
 * Universal return signal for GoalD Agents to trigger adaptation.
 *
 * <p>This enum is the single contract for the outcome of any GoalD goal
 * execution. It is intentionally minimal and is consumed by both the
 * orchestrators (which branch on it) and the GoalD Manager / Gateway
 * (which uses it to drive the MAPE-K adaptation loop).</p>
 *
 * <p>Semantics of each value:</p>
 * <ul>
 *   <li>{@link #SUCCESS} &mdash; the goal was fulfilled as planned.</li>
 *   <li>{@link #FAILURE} &mdash; the goal was attempted but failed.</li>
 *   <li>{@link #UNFEASIBLE} &mdash; the goal could not be executed under the
 *       current context (e.g. a precondition such as "doctor present" is
 *       violated). This is the signal that triggers adaptation.</li>
 * </ul>
 *
 * @see FulfillmentStatus
 * @since GoalD 2.0
 */
public enum Status {
    /** Goal was fulfilled successfully. */
    SUCCESS,
    /** Goal was attempted but failed. */
    FAILURE,
    /** Goal is unfeasible under the current context; triggers adaptation. */
    UNFEASIBLE
}