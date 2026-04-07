package tas.goals;
import reactor.core.publisher.Flux;

public interface G1GetVitalParams {
    record Vitals(String patientId, int heartRate, double temperature) {}
    Flux<Vitals> monitor(String patientId);
}
