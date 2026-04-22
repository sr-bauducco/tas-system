package tas.system.treatment.agent;

import org.springframework.web.bind.annotation.*;
import tas.system.api.goals.G12ChangeDose;
import reactor.core.publisher.Mono;

@RestController
@RequestMapping("/g12")
public class DoseAgent implements G12ChangeDose {

    @PostMapping("/execute")
    @Override
    public Mono<FulfillmentStatus> execute(@RequestBody DoseContext context) {
        
        // 1. EVALUATE FEASIBILITY (Context C4)
        // Per GoalD: If the required context for the plan is missing, the goal is UNFEASIBLE.
        if (!context.isDrugAdministered()) {
            return Mono.just(new FulfillmentStatus(
                "UNFEASIBLE", 
                "P8", 
                "Plan P8 rejected: Drug is not currently being administered (C4 inactive)."
            ));
        }

        // 2. EXECUTE PLAN P8
        return executePlanP8(context);
    }

    /**
     * PLAN P8: Change Dose Logic
     * This is the atomic task that achieves Goal G12.
     */
    private Mono<FulfillmentStatus> executePlanP8(DoseContext ctx) {
        return Mono.just(new FulfillmentStatus(
            "SUCCESS", 
            "P8", 
            "Dosage successfully changed to " + ctx.requestedDose() + " for Patient " + ctx.patientId()
        ));
    }
}