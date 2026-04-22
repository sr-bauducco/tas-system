package agent;

import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Mono;
import api.*;
import goals.*;
import goals.definition.G10NotifyEmergency;
import goals.request.EmergencyRequest;

/**
 * GoalD Agent for G10: Notify Emergency.
 * Uses Context C1 (Internet) as a Feasibility Guard.
 */
@RestController
@RequestMapping("/emergency/g10")
public class EmergencyAgent implements G10NotifyEmergency {

    @PostMapping("/execute")
    @Override
    public Mono<FulfillmentStatus> notifyEmergency(@RequestBody EmergencyRequest request) {
        return Mono.just(request.context())
            .flatMap(ctx -> {
                // Feasibility Guard C1: Internet Connection
                if (!ctx.isInternetConnected()) {
                    return Mono.just(new FulfillmentStatus(
                        Status.UNFEASIBLE, 
                        "Adaptation Required: C1 violation (No Internet) for G10"
                    ));
                }

                // Logic for Plan P10 (Notify EMS)
                return Mono.just(new FulfillmentStatus(Status.SUCCESS, "EMS Notified via Plan P10"));
            });
    }
}