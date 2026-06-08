package agent;

import goals.request.VitalSign;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Mono;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@RestController
@RequestMapping("/monitor/g7")
public class SensedDataAgent {

    private static final Logger log = LoggerFactory.getLogger(SensedDataAgent.class);

    /**
     * Strategy P4: Get Sensed Data
     * Retrieves a discrete physical reading from the wearable hardware.
     */
    @GetMapping("/sensed/{patientId}")
    public Mono<VitalSign> getSensedData(@PathVariable String patientId) {
        log.info("[G7 -> P4] Hardware sensor queried for patient: {}", patientId);
        // Simulated hardware poll
        return Mono.just(new VitalSign(patientId, 75.0, 120.0, System.currentTimeMillis()));
    }
}