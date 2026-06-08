package agent;

import api.FulfillmentStatus;
import api.Status;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Mono;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@RestController
@RequestMapping("/monitor/g3")
public class PushButtonAgent {

    private static final Logger log = LoggerFactory.getLogger(PushButtonAgent.class);

    /**
     * Strategy P1: Push Button
     * Represents the physical hardware interrupt of a patient pressing the panic button.
     */
    @PostMapping("/push/{patientId}")
    public Mono<FulfillmentStatus> registerButtonPress(@PathVariable String patientId) {
        log.error("[G3 -> P1] ALERT: Panic Button physically pressed by patient: {}", patientId);
        return Mono.just(new FulfillmentStatus(Status.SUCCESS, "Panic button engaged"));
    }
}