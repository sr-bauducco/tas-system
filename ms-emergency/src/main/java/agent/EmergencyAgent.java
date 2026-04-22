package agent;

import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Mono;
import api.FulfillmentStatus;
import api.Status;
// --- Updated Specific Imports ---
import goals.definition.G10NotifyEmergency;
import goals.request.EmergencyRequest;
import goals.context.EmergencyContext;

@RestController
@RequestMapping("/emergency/g10")
public class EmergencyAgent implements G10NotifyEmergency {

    @PostMapping("/execute")
    @Override
    public Mono<FulfillmentStatus> notifyEmergency(@RequestBody EmergencyRequest request) {
        return Mono.just(request.context())
            .flatMap(ctx -> {
                if (!ctx.isInternetConnected()) {
                    return Mono.just(new FulfillmentStatus(Status.UNFEASIBLE, "C1 Violation: No Internet"));
                }
                return Mono.just(new FulfillmentStatus(Status.SUCCESS, "EMS Notified via P10"));
            });
    }
}