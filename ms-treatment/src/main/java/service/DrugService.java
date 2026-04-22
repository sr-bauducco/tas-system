package service;

import org.springframework.stereotype.Service;
import reactor.core.publisher.Mono;

@Service
public class DrugService {
    public Mono<Boolean> changeDrug(String patientId, String drugCode) {
        // Plan P7: Non-blocking call to pharmacy subsystem
        return Mono.just(true); 
    }
}