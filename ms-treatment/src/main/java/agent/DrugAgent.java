package agent;

import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Mono;
import api.FulfillmentStatus;
import api.Status;
// --- Updated Specific Imports ---
import goals.definition.G11ChangeDrug;
import goals.request.DrugRequest;
import goals.context.DrugContext;
import service.DrugService;

@RestController
@RequestMapping("/treatment/g11")
public class DrugAgent implements G11ChangeDrug {

    private final DrugService drugService;

    public DrugAgent(DrugService drugService) {
        this.drugService = drugService;
    }

    @PostMapping("/execute")
    @Override
    public Mono<FulfillmentStatus> executeChangeDrug(@RequestBody DrugRequest request) {
        return Mono.just(request.context())
            .flatMap(ctx -> {
                // Feasibility Guard C3
                if (!ctx.isDoctorPresent()) {
                    return Mono.just(new FulfillmentStatus(Status.UNFEASIBLE, "C3 Violation: Doctor required"));
                }
                return drugService.changeDrug(request.patientId(), request.newDrugCode())
                    .map(success -> new FulfillmentStatus(Status.SUCCESS, "Drug changed via P7"))
                    .onErrorResume(e -> Mono.just(new FulfillmentStatus(Status.FAILURE, e.getMessage())));
            });
    }
}