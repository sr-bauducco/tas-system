package tas.services.emergency;

import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;
import tas.goals.G10NotifyEmergency;
import reactor.core.publisher.Mono;
import jakarta.annotation.PostConstruct;

@RestController
public class EmergencyAgent implements G10NotifyEmergency {

    @PostConstruct
    public void init() {
        System.out.println("\n=========================================================");
        System.out.println("[G10 AGENT READY] Emergency Service Listening on Port 8080");
        System.out.println("=========================================================\n");
    }

    @PostMapping("/notify")
    @Override
    public Mono<FulfillmentStatus> execute(@RequestBody EmergencyContext context) {
        System.out.println("\n[🚨 G10 EXECUTION TRIGGERED] Context: " + context);
        
        if (context.severity() > 80.0) {
            System.out.println("[PLAN P9] Executing Call Ambulance...");
        } else {
            System.out.println("[PLAN P10] Executing Send SMS...");
        }
        
        System.out.println("Notification Dispatched Successfully.");
        return Mono.just(new FulfillmentStatus("SUCCESS", "MOCK_EMERGENCY_GATEWAY"));
    }
}