package service;

import org.springframework.stereotype.Service;
import reactor.core.publisher.Mono;

@Service
public class DrugService {
    public Mono<Boolean> changeDrug(String patientId, String drugCode) {
        // Implementation of Plan P7
        return Mono.just(true); 
    }
}