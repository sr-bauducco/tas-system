package agent;

import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Mono;
import api.*;
import goals.definition.*;
import goals.request.*;
import goals.context.*;

@RestController
@RequestMapping("/treatment/g9")
public class AdministerMedicineOrchestrator {

    private final DrugAgent drugAgent; // G11
    private final DoseAgent doseAgent; // G12

    public AdministerMedicineOrchestrator(DrugAgent drugAgent, DoseAgent doseAgent) {
        this.drugAgent = drugAgent;
        this.doseAgent = doseAgent;
    }

    @PostMapping("/execute")
    public Mono<FulfillmentStatus> administerMedicine(@RequestBody MedicineRequest request) {
        System.out.println("G9 Orchestrator: Starting Administer Medicine sequence...");

        // Strategy 1: Attempt Goal G11 (Change Drug)
        return drugAgent.executeChangeDrug(request.toDrugRequest())
            .flatMap(status -> {
                if (status.status() == Status.UNFEASIBLE) {
                    System.out.println("G9 Adaptation: G11 unfeasible. Attempting Goal G12 (Change Dose)...");
                    
                    // Strategy 2: Fallback to Goal G12 (Change Dose)
                    return doseAgent.executeChangeDose(request.toDoseRequest());
                }
                return Mono.just(status);
            })
            .onErrorResume(e -> Mono.just(new FulfillmentStatus(Status.FAILURE, "G9 Orchestration Error: " + e.getMessage())));
    }
}