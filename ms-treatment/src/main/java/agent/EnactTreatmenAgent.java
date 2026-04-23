package agent;

import goals.definition.G6;
import goals.definition.G9;
import goals.definition.G10;
import goals.request.MedicineRequest;
import goals.request.EmergencyRequest;
import api.FulfillmentStatus;
import api.Status;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Mono;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@Service
public class EnactTreatmentAgent implements G6 {

    private final G9 g9Orchestrator;   // AdministerMedicineOrchestrator (Internal)
    private final G10 emergencyClient; // EmergencyAgent WebClient Proxy (Remote)

    public EnactTreatmentAgent(G9 g9Orchestrator, G10 emergencyClient) {
        this.g9Orchestrator = g9Orchestrator;
        this.emergencyClient = emergencyClient;
    }

    @Override
    public Mono<FulfillmentStatus> enact(MedicineRequest request) {
        log.info("EnactTreatmentAgent: Initiating G9 -> G10 escalation policy...");

        // 1. Monitor/Execute G9 Tree (Logic: G11/C3 -> Fallback G12/C4)
        return g9Orchestrator.administer(request)
            .flatMap(status -> {
                // 2. Analyze: If G9 tree is UNFEASIBLE (Physical guards failed)
                if (status.status() == Status.UNFEASIBLE) {
                    log.warn("[Adaptation] Medication unfeasible. Escalating to Emergency Tree (G10).");
                    
                    // 3. Plan/Execute: Horizontal adaptation to ms-emergency
                    return emergencyClient.execute(new EmergencyRequest(request.context()))
                        .map(res -> new FulfillmentStatus(
                            res.status(), 
                            "[Escalated via G6] Medication unfeasible: " + res.message()
                        ));
                }
                
                // Return Success or Failure if G9 was actually executable
                return Mono.just(status);
            })
            .onErrorResume(e -> Mono.just(new FulfillmentStatus(
                Status.FAILURE, 
                "EnactTreatment orchestration failed: " + e.getMessage()
            )));
    }
}