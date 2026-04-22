package agent;

import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;
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
    
    private final DrugAgent drugAgent;
    private final DoseAgent doseAgent;
    private final Counter adaptationCounter;

    public AdministerMedicineOrchestrator(DrugAgent drugAgent, DoseAgent doseAgent, MeterRegistry registry) {
        this.drugAgent = drugAgent;
        this.doseAgent = doseAgent;
        
        this.adaptationCounter = Counter.builder("tas.adaptation.count")
            .description("Number of times G9 adapted from G11 to G12")
            .tag("goal", "G9")
            .tag("strategy", "fallback")
            .register(registry);
    }

    @PostMapping("/execute")
    @Override
    public Mono<FulfillmentStatus> administerMedicine(@RequestBody MedicineRequest request) {
        log.info("[G9] Initiating administration sequence for patient: {}", request.patientId());

        return drugAgent.executeChangeDrug(request.toDrugRequest())
            .flatMap(result -> {
                if (result.status() == Status.UNFEASIBLE) {
                    adaptationCounter.increment();
                    log.warn("[G9] G11 unfeasible. Triggering fallback to G12.");
                    
                    return doseAgent.executeChangeDose(request.toDoseRequest())
                        .map(doseRes -> new FulfillmentStatus(
                            doseRes.status(), 
                            "[Adapted via G12] " + doseRes.message()
                        ));
                }
                return Mono.just(result);
            })
            .onErrorResume(e -> {
                log.error("[G9] Critical failure: {}", e.getMessage());
                return Mono.just(new FulfillmentStatus(Status.FAILURE, "G9 Orchestration Error"));
            });
    }
} // <--- This was likely the missing brace!