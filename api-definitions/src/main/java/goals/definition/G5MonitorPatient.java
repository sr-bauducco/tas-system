package goals.definition;

import goals.request.VitalSign;
import reactor.core.publisher.Flux;

public interface G5MonitorPatient {
    // A reactive stream of vital signs
    Flux<VitalSign> monitorVitals(String patientId);
}