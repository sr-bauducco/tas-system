package tas.monitor;

import org.springframework.web.bind.annotation.*;
import org.springframework.http.MediaType;
import tas.goals.G1GetVitalParams;
import reactor.core.publisher.Flux;
import java.time.Duration;
import java.util.Random;

@RestController
public class MonitorController implements G1GetVitalParams {
    private final Random random = new Random();

    @GetMapping(value = "/monitor/{id}", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<Vitals> monitor(@PathVariable String id) {
        return Flux.interval(Duration.ofSeconds(1))
                .map(tick -> new Vitals(id, 60 + random.nextInt(60), 36.5 + random.nextDouble() * 2))
                .log("MonitorAgent");
    }
}