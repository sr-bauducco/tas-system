package tas.monitor;

import org.springframework.web.bind.annotation.*;
import org.springframework.http.MediaType;
import tas.goals.G1GetVitalParams;
import reactor.core.publisher.Flux;
import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;
import java.time.Duration;
import java.util.Random;

@RestController
public class MonitorAgent implements G1GetVitalParams {
    private final Random random = new Random();

    // Replaces OSGi activate()
    @PostConstruct
    public void activate() {
        System.out.println("GetVitalParams Microservice Activated (Bean Initialized)");
    }

    // Replaces OSGi deactivate()
    @PreDestroy
    public void deactivate() {
        System.out.println("GetVitalParams Microservice Deactivated (Context Closing)");
    }

    @GetMapping(value = "/monitor/{id}", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<Vitals> monitor(@PathVariable String id) {
        return Flux.interval(Duration.ofSeconds(1))
            .map(tick -> {
                System.out.println("Getting Vital Params for patient: " + id);
                return new Vitals(
                    id, 
                    60 + random.nextInt(60), // Simulated HR
                    36.5 + random.nextDouble() * 2, // Simulated Temp
                    0, // Failure rate (per legacy code)
                    0  // Cost (per legacy code)
                );
            });
    }
}