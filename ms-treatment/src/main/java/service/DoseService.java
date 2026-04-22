package service;

import org.springframework.stereotype.Service;
import reactor.core.publisher.Mono;

@Service
public class DoseService {
    public Mono<Boolean> updateDose(String patientId, double dose) {
        // Plan P8: Non-blocking call to medical device
        return Mono.just(true);
    }
}