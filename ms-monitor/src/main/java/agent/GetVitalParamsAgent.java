package agent;

import goals.request.VitalSign;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Mono;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@RestController
@RequestMapping("/monitor/g7")
public class GetVitalParamsAgent {

    private static final Logger log = LoggerFactory.getLogger(GetVitalParamsAgent.class);

    /**
     * Strategy: Invasive (High Precision)
     * Maps to OSGi bundle: Invasive-impl
     */
    @GetMapping("/invasive/{patientId}")
    public Mono<VitalSign> getInvasiveData(@PathVariable String patientId) {
        log.info("[G7 -> Invasive] Reading high-precision internal sensors for: {}", patientId);
        return Mono.just(new VitalSign(patientId, 75.0, 120.0, System.currentTimeMillis()));
    }

    /**
     * Strategy: Non-Invasive (Lower Precision, High Comfort)
     * Maps to OSGi bundle: NonInvasive-impl[cite: 5]
     */
    @GetMapping("/noninvasive/{patientId}")
    public Mono<VitalSign> getNonInvasiveData(@PathVariable String patientId) {
        log.warn("[G7 -> NonInvasive] Reading external wearable sensors for: {}", patientId);
        return Mono.just(new VitalSign(patientId, 72.0, 118.0, System.currentTimeMillis()));
    }
}