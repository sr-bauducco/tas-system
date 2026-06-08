package agent;

import goals.request.VitalSign;
import api.FulfillmentStatus;
import api.Status;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Mono;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@RestController
@RequestMapping("/intelligence/g8")
public class AnalyzeAgent {
    
    private static final Logger log = LoggerFactory.getLogger(AnalyzeAgent.class);

    /**
     * Strategy P6: Remote Analysis (High QoS)
     * Context Precondition: C1 (Internet Connection)
     */
    @PostMapping("/remote")
    public Mono<FulfillmentStatus> executeRemoteAnalysis(@RequestBody VitalSign vitals) {
        log.info("[G8 -> P6] Performing High-QoS Remote Cloud Analysis for Patient: {}", vitals.patientId());
        return Mono.just(new FulfillmentStatus(Status.SUCCESS, evaluate(vitals) + " (via P6)"));
    }

    /**
     * Strategy P5: Local Analysis (Lower QoS Fallback)
     * Context Precondition: None (Always Available Edge Computing)
     */
    @PostMapping("/local")
    public Mono<FulfillmentStatus> executeLocalAnalysis(@RequestBody VitalSign vitals) {
        log.warn("[G8 -> P5] Performing Fallback Local Edge Analysis for Patient: {}", vitals.patientId());
        return Mono.just(new FulfillmentStatus(Status.SUCCESS, evaluate(vitals) + " (via P5)"));
    }

    private String evaluate(VitalSign vitals) {
        if (vitals.heartRate() > 100) return "CRITICAL: Tachycardia Detected";
        if (vitals.heartRate() < 50) return "CRITICAL: Bradycardia Detected";
        return "NORMAL: Vitals Stable";
    }
}