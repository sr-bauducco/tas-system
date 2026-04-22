package agent;

import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Mono;
import api.*;
import goals.*;
import service.DoseService;

@RestController
@RequestMapping("/treatment/g12")
public class DoseAgent implements G12ChangeDose {

    private final DoseService doseService;

    public DoseAgent(DoseService doseService) {
        this.doseService = doseService;
    }

    @PostMapping("/execute")
    @Override
    public Mono<FulfillmentStatus> executeChangeDose(@RequestBody DoseRequest request) {
        return Mono.just(request.context())
            .flatMap(ctx -> {
                // Feasibility Guard C4: Drug must already be administered
                if (!ctx.isDrugAdministered()) {
                    return Mono.just(new FulfillmentStatus(Status.UNFEASIBLE, "C4 Violation: Drug not yet administered"));
                }
                return doseService.updateDose(request.patientId(), request.newDose())
                    .map(success -> new FulfillmentStatus(Status.SUCCESS, "Dose updated via P8"))
                    .onErrorResume(e -> Mono.just(new FulfillmentStatus(Status.FAILURE, e.getMessage())));
            });
    }
}