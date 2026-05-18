package agent;

import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;

import org.springframework.http.MediaType;
import org.springframework.test.web.reactive.server.WebTestClient;
import goals.request.*;
import goals.context.*;
// Import the application class


/**
 * TAS System Orchestration Test.
 * Explicitly references TreatmentApplication to resolve configuration scanning.
 */
/*@SpringBootTest(
    classes = TreatmentApplication.class, 
    webEnvironment = SpringBootTest.WebEnvironment.NONE
)*/
@Disabled("Waiting for Eureka Registry and API Gateway to be orchestrated")
public class SystemOrchestrationTest {

    // These clients talk to the services started by your shell script
    private final WebTestClient treatmentClient = WebTestClient.bindToServer().baseUrl("http://localhost:8083").build();
    private final WebTestClient emergencyClient = WebTestClient.bindToServer().baseUrl("http://localhost:8084").build();

    @Test
    void test_G10_Emergency_Adaptation() {
        EmergencyRequest req = new EmergencyRequest("P1", "CRITICAL", new EmergencyContext(false, "NONE"));
        
        emergencyClient.post().uri("/emergency/g10/execute")
            .contentType(MediaType.APPLICATION_JSON)
            .bodyValue(req)
            .exchange()
            .expectStatus().isOk()
            .expectBody().jsonPath("$.status").isEqualTo("UNFEASIBLE");
    }

    @Test
    void test_G11_Drug_Feasibility() {
        DrugRequest req = new DrugRequest("P1", "DRUG_A", new DrugContext(true, "DOC_01"));
        
        treatmentClient.post().uri("/treatment/g11/execute")
            .contentType(MediaType.APPLICATION_JSON)
            .bodyValue(req)
            .exchange()
            .expectStatus().isOk()
            .expectBody().jsonPath("$.status").isEqualTo("SUCCESS");
    }

    @Test
    void test_G12_Dose_Adaptation() {
        DoseRequest req = new DoseRequest("P1", 20.5, new DoseContext(false, 0.0));
        
        treatmentClient.post().uri("/treatment/g12/execute")
            .contentType(MediaType.APPLICATION_JSON)
            .bodyValue(req)
            .exchange()
            .expectStatus().isOk()
            .expectBody().jsonPath("$.status").isEqualTo("UNFEASIBLE");
    }

    @Test
    void test_G9_Self_Adaptive_Loop() {
        // G9 Orchestration: G11 is unfeasible (no doctor), should fallback to G12 (feasible)
        MedicineRequest req = new MedicineRequest("P1", "MED", 50.0, 
            new goals.context.DrugContext(false, "NONE"), 
            new goals.context.DoseContext(true, 10.0));

        treatmentClient.post().uri("/treatment/g9/execute")
            .contentType(MediaType.APPLICATION_JSON)
            .bodyValue(req)
            .exchange()
            .expectStatus().isOk()
            .expectBody()
            .jsonPath("$.status").isEqualTo("SUCCESS")
            // We use value(containsString(...)) or just update the expected string:
            .jsonPath("$.message").isEqualTo("[Adapted via G12] Dose updated via P8");
    }
}