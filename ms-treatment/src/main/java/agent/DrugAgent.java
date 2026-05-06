package agent;

import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Mono;
import api.FulfillmentStatus;
import api.Status;
import goals.request.DrugRequest;
import goals.context.DrugContext;

@RestController
@RequestMapping("/treatment/g11")
public class DrugAgent {

    // 1. The HTTP REST Entry Point (Called by the API Gateway & Test Script)
    @PostMapping("/execute")
    public Mono<FulfillmentStatus> executeChangeDrugRest(
            @RequestBody DrugRequest request,
            @RequestHeader(value = "X-Context-Doctor", required = false) String doctorPresent) {
        
        // Evaluate the distributed context header injected by the script/wearable
        if ("false".equalsIgnoreCase(doctorPresent)) {
            return Mono.just(new FulfillmentStatus(Status.UNFEASIBLE, "C3 Violation: Doctor not present (Header Evaluated)"));
        }
        
        // If the header is true or missing, proceed to the core logic
        return executeChangeDrug(request);
    }

    // 2. The Internal Java Entry Point (Called directly by G9 Orchestrator)
    public Mono<FulfillmentStatus> executeChangeDrug(DrugRequest request) {
        DrugContext ctx = request.context();
        
        if (ctx != null && !ctx.isDoctorPresent()) {
            return Mono.just(new FulfillmentStatus(Status.UNFEASIBLE, "C3 Violation: Doctor not present"));
        }

        return Mono.just(new FulfillmentStatus(Status.SUCCESS, "Drug changed via G11"));
    }
}