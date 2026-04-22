package agent;

import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Mono;
import api.FulfillmentStatus;
import api.Status;
import goals.definition.G9AdministerMedicine;
import goals.request.MedicineRequest;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@RestController
@RequestMapping("/treatment/g9")
public class AdministerMedicineOrchestrator implements G9AdministerMedicine {

    private static final Logger log = LoggerFactory.getLogger(AdministerMedicineOrchestrator.class);
    
    private final DrugAgent drugAgent; // Goal G11
    private final DoseAgent doseAgent; // Goal G12

    public AdministerMedicineOrchestrator(DrugAgent drugAgent, DoseAgent doseAgent) {
        this.drugAgent = drugAgent;
        this.doseAgent = doseAgent;
    }

    @PostMapping("/execute")
    @Override
    public Mono<FulfillmentStatus> administerMedicine(@RequestBody MedicineRequest request) {
        log.info("[G9] Initiating administration sequence for patient: {}", request.patientId());

        // Step 1: Attempt preferred Strategy (G11 - Change Drug)
        return drugAgent.executeChangeDrug(request.toDrugRequest())
            .flatMap(result -> {
                // Step 2: Check for Unfeasibility (C3 Violation)
                if (result.status() == Status.UNFEASIBLE) {
                    log.warn("[G9] Strategy G11 unfeasible: {}. Triggering Adaptation...", result.message());
                    
                    // Step 3: Adaptation - Fallback to Strategy G12 (Change Dose)
                    return doseAgent.executeChangeDose(request.toDoseRequest())
                        .map(doseResult -> new FulfillmentStatus(
                            doseResult.status(),
                            "[Adapted via G12] " + doseResult.message()
                        ));
                }
                
                // If G11 was successful or failed definitively, return its result
                return Mono.just(result);
            })
            .onErrorResume(e -> {
                log.error("[G9] Critical failure in orchestration: {}", e.getMessage());
                return Mono.just(new FulfillmentStatus(Status.FAILURE, "G9 Orchestration Error"));
            });
    }
}