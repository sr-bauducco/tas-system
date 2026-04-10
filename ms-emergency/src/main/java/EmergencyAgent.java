package tas.services.emergency;

import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;
import tas.goals.G10NotifyEmergency;
import reactor.core.publisher.Mono;
import jakarta.annotation.PostConstruct;
import java.time.Duration;
import java.util.Random;

@RestController
public class EmergencyAgent implements G10NotifyEmergency {

    private final Random random = new Random();

    @PostConstruct
    public void init() {
        System.out.println("\n[G10 AGENT READY] Emergency Service (QoS Aware) Listening on Port 8080\n");
    }

    @PostMapping("/notify")
    @Override
    public Mono<FulfillmentStatus> execute(@RequestBody EmergencyContext context) {
        System.out.println("\n[G10 EXECUTION TRIGGERED] Context: " + context);
        
        return checkInternetConnection()
            .flatMap(hasInternet -> {
                if (hasInternet) {
                    System.out.println("[Context] Internet available. Attempting AlarmService...");
                    return executeP10AlarmService(context)
                            .onErrorResume(error -> {
                                System.err.println("[QoS Violation] AlarmService failed: " + error.getMessage());
                                return executeP9SendSms(context);
                            });
                } else {
                    System.out.println("[Context] No Internet. Defaulting to SMS...");
                    return executeP9SendSms(context);
                }
            });
    }

    private Mono<Boolean> checkInternetConnection() {
        boolean isConnected = random.nextInt(100) < 70;
        return Mono.just(isConnected);
    }

    // PLAN P10: Alarm Service
    //precision: 10, response_time: 5
    private Mono<FulfillmentStatus> executeP10AlarmService(EmergencyContext context) {
        return Mono.defer(() -> {
            System.out.println("   -> Executing AlarmService API (Expecting max 5s response)...");
            
            // Simulating network delay to show QoS timeout in action
            return Mono.just(new FulfillmentStatus("SUCCESS_P10", "ALARM_SERVICE_API", 10, 5))
                       .delayElement(Duration.ofSeconds(random.nextInt(7))); // Random delay 0-6 seconds
        })
        .timeout(Duration.ofSeconds(5), Mono.error(new RuntimeException("QoS Timeout: Exceeded 5 seconds")));
    }

    // PLAN P9: Send SMS 
    // precision: 5, response_time: 3
    private Mono<FulfillmentStatus> executeP9SendSms(EmergencyContext context) {
        return Mono.defer(() -> {
            System.out.println("   -> Executing SendSms API (Fallback / Fast path)...");
            return Mono.just(new FulfillmentStatus("SUCCESS_P9", "LOCAL_SMS_MODEM", 5, 3));
        })

        .timeout(Duration.ofSeconds(3)); 
    }
}
