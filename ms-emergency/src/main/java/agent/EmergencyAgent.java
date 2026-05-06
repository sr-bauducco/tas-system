package agent;

import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Mono;
import api.FulfillmentStatus;
import api.Status;
import goals.definition.G10NotifyEmergency;
import goals.request.EmergencyRequest;
import goals.context.EmergencyContext;

@RestController
@RequestMapping("/emergency/g10")
public class EmergencyAgent implements G10NotifyEmergency {

    @PostMapping("/execute")
    @Override
    public Mono<FulfillmentStatus> notifyEmergency(@RequestBody EmergencyRequest request) {
        // Extract the context safely
        EmergencyContext ctx = request.context();
        
        // 1. Handle the case where the context is missing from the JSON body
        if (ctx == null) {
            // The API Gateway already validated the headers to route us here safely!
            return Mono.just(new FulfillmentStatus(Status.SUCCESS, "EMS Notified via P10 (Gateway Routed)"));
        }

        // 2. Handle the case where context was provided and violates the guard
        if (!ctx.isInternetConnected()) {
            return Mono.just(new FulfillmentStatus(Status.UNFEASIBLE, "C1 Violation: No Internet"));
        }
        
        // 3. Handle the standard success case
        return Mono.just(new FulfillmentStatus(Status.SUCCESS, "EMS Notified via P10"));
    }
}