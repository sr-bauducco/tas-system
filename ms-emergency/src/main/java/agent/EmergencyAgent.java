package agent;

import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Mono;
import api.FulfillmentStatus;
import api.Status;
import goals.definition.G10NotifyEmergency;
import goals.request.EmergencyRequest;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@RestController
@RequestMapping("/emergency")
public class EmergencyAgent implements G10NotifyEmergency {

    private static final Logger log = LoggerFactory.getLogger(EmergencyAgent.class);

    /**
     * Strategy P10: Alarm Service (High QoS)
     * The Gateway routes here when X-Context-C1_InternetConnection is true.
     */
    @PostMapping("/alarm")
    @Override
    public Mono<FulfillmentStatus> notifyEmergency(@RequestBody EmergencyRequest request) {
        log.info("Executing High-QoS Strategy (Alarm) for patient: {}", request.patientId());
        return Mono.just(new FulfillmentStatus(Status.SUCCESS, "EMS Notified via P10 (Alarm Service)"));
    }

    /**
     * Strategy P9: Send SMS (Lower QoS Fallback)
     * The Gateway routes here when the internet context is missing.
     */
    @PostMapping("/sms")
    public Mono<FulfillmentStatus> notifyEmergencySmsFallback(@RequestBody EmergencyRequest request) {
        log.warn("Executing Fallback Strategy (SMS) for patient: {}", request.patientId());
        return Mono.just(new FulfillmentStatus(Status.SUCCESS, "EMS Notified via P9 (SMS Fallback)"));
    }
}