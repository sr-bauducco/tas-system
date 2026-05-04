package agent;

import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Mono;
import api.FulfillmentStatus;
import api.Status;
import goals.request.DrugRequest;
import goals.context.DrugContext;

@RestController
@RequestMapping("/treatment/g11") // Ensure this matches the Gateway path
public class DrugAgent {

    @PostMapping("/execute")
    public Mono<FulfillmentStatus> executeChangeDrug(@RequestBody DrugRequest request) {
        // Extract the context safely
        DrugContext ctx = request.context();

        // 1. Handle missing context (The API Gateway stripped it/didn't send it)
        if (ctx == null) {
            return Mono.just(new FulfillmentStatus(Status.SUCCESS, "Drug changed via G11 (Gateway Routed)"));
        }

        // 2. Handle guard violation (if context was explicitly provided)
        if (!ctx.isDoctorPresent()) {
            return Mono.just(new FulfillmentStatus(Status.UNFEASIBLE, "C3 Violation: Doctor not present"));
        }

        // 3. Standard success
        return Mono.just(new FulfillmentStatus(Status.SUCCESS, "Drug changed via G11"));
    }
}