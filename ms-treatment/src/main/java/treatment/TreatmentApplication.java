package treatment;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.ComponentScan;

/**
 * The single entry point for the 'ms-treatment' microservice.
 * This bootstraps the MAPE-K Agents for both Change Dose (G12) and Change Drug (G11).
 */
@SpringBootApplication
@ComponentScan(basePackages = {"agent", "service", "treatment"}) 
public class TreatmentApplication {
    public static void main(String[] args) {
        SpringApplication.run(TreatmentApplication.class, args);
    }
}