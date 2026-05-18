    package monitor;

    import goals.definition.G5MonitorPatient;
    import goals.request.VitalSign;
    import org.springframework.http.MediaType;
    import org.springframework.web.bind.annotation.*;
    import reactor.core.publisher.Flux;
    import java.time.Duration;

    @RestController
    @RequestMapping("/monitor/g5")
    public class MonitorAgent implements G5MonitorPatient {

    @GetMapping(value = "/stream/{patientId}", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    @Override
    public Flux<VitalSign> monitorVitals(@PathVariable("patientId") String patientId) { // Added ("patientId")
        return Flux.interval(Duration.ofSeconds(2))
            .map(tick -> new VitalSign(
                patientId,
                60 + Math.random() * 60,
                110 + Math.random() * 30,
                System.currentTimeMillis()
        ))
        .log("G5-Monitor-Agent");
    }
}