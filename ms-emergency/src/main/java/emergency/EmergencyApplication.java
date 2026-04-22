package emergency;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.ComponentScan;

@SpringBootApplication
@ComponentScan(basePackages = {"agent", "emergency"}) // CRITICAL: Must scan the agent folder
public class EmergencyApplication {
    public static void main(String[] args) {
        SpringApplication.run(EmergencyApplication.class, args);
    }
}