package intelligence;

import agent.IntelligenceAgent;
import goals.request.VitalSign;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.client.discovery.EnableDiscoveryClient;
import org.springframework.cloud.client.loadbalancer.LoadBalanced;
import org.springframework.context.annotation.Bean;
import org.springframework.web.reactive.function.client.WebClient;

@SpringBootApplication(scanBasePackages = {"intelligence", "agent"}) // Ensures Agent is found
@EnableDiscoveryClient
public class IntelligenceApplication {

    private static final Logger log = LoggerFactory.getLogger(IntelligenceApplication.class);

    public static void main(String[] args) {
        SpringApplication.run(IntelligenceApplication.class, args);
    }

    /**
     * Required for Service Discovery. 
     * Allows using "http://ms-monitor" instead of "localhost:8081"
     */
    @Bean
    @LoadBalanced
    public WebClient.Builder loadBalancedWebClientBuilder() {
        return WebClient.builder();
    }

    /**
     * This represents Goal G2: Provide automated life support.
     * It fulfills G2 by orchestrating G5 (Monitor) and G6 (Enact).
     */
    @Bean
    CommandLineRunner startG2Loop(WebClient.Builder builder, IntelligenceAgent g6Agent) {
        return args -> {
            log.info("[G2] Starting Automated Life Support Loop...");

            builder.build().get()
                .uri("http://ms-monitor/monitor/g5/stream/P-001") // Fulfilling G5 (Monitor)
                .retrieve()
                .bodyToFlux(VitalSign.class)
                .flatMap(vitals -> {
                    // Fulfilling G6 (Enact Medical Support)
                    return g6Agent.enact(vitals);
                })
                .subscribe(
                    success -> {},
                    error -> log.error("[G2] Loop Error: {}", error.getMessage()),
                    () -> log.info("[G2] Loop Terminated")
                );
        };
    }
}