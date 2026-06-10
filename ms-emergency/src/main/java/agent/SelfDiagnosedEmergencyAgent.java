package agent;

import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Mono;
import api.FulfillmentStatus;
import api.Status;
import goals.request.EmergencyRequest;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@RestController
@RequestMapping("/emergency/g4")
public class SelfDiagnosedEmergencyAgent {

    private static final Logger log = LoggerFactory.getLogger(SelfDiagnosedEmergencyAgent.class);

    /**
     * Strategy P3: Alarm Service (High QoS for G4)
     * Context Precondition: C1 (Internet Connection)
     */
    @PostMapping("/alarm")
    public Mono<FulfillmentStatus> notifyAlarm(@RequestBody EmergencyRequest request) {
        log.info("[G4 -> P3] Self-Diagnosed Emergency routed via High-QoS Alarm: {}", request.patientId());
        return Mono.just(new FulfillmentStatus(Status.SUCCESS, "G4 Notified via P3 (Alarm)"));
    }

    /**
     * Strategy P2: Send SMS (Lower QoS Fallback for G4)
     * Context Precondition: None
     */
    @PostMapping("/sms")
    public Mono<FulfillmentStatus> notifySms(@RequestBody EmergencyRequest request) {
        log.warn("[G4 -> P2] Self-Diagnosed Emergency routed via Fallback SMS: {}", request.patientId());
        return Mono.just(new FulfillmentStatus(Status.SUCCESS, "G4 Notified via P2 (SMS)"));
    }
}