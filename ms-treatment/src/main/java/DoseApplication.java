package tas.system.treatment;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * Bootstrap class for the G12 Change Dose Implementation Bundle.
 * This service hosts the DoseAgent and executes Plan P8.
 */
@SpringBootApplication
public class DoseApplication {

    public static void main(String[] args) {
        // Launches the Reactive WebFlux container on the configured port (8083)
        SpringApplication.run(DoseApplication.class, args);
    }
}