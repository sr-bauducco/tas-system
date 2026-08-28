package goals.definition;

import goals.request.VitalSign;
import reactor.core.publisher.Flux;

/**
 * Goal Definition: G5 - Monitor Patient Vitals.
 *
 * <p>This goal represents the continuous monitoring phase of the TAS system.
 * It provides a reactive stream of {@link goals.request.VitalSign} data
 * for real-time analysis and adaptation.
 * Used by {@link agent.MonitorAgent} to provide telemetry for the MAPE-K loop.</p>
 *
 * @since GoalD 2.0
 */
public interface G5MonitorPatient {
    /**
     * Streams vital signs for a given patient.
     *
     * @param patientId the ID of the patient to monitor
     * @return a reactive stream of {@link goals.request.VitalSign} measurements
     */
    Flux<VitalSign> monitorVitals(String patientId);
}