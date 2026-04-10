package tas.goals;

import reactor.core.publisher.Mono;

public interface G6AnalyzeData {
    // Determines if an emergency call (G10) is required based on vitals
    Mono<Boolean> shouldNotifyEmergency(int heartRate, double temperature);
}
