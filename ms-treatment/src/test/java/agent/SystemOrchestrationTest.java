package agent;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.reactive.server.WebTestClient;
import goals.request.*;
import goals.context.*;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.NONE)
public class SystemOrchestrationTest {

    private final WebTestClient treatmentClient = WebTestClient.bindToServer().baseUrl("http://localhost:8083").build();
    private final WebTestClient emergencyClient = WebTestClient.bindToServer().baseUrl("http://localhost:8084").build();

    @Test
    void test_G10_Emergency_Adaptation() {
        // C1 Violation: No Internet
        EmergencyRequest req = new EmergencyRequest("P1", "CRITICAL", new EmergencyContext(false, "NONE"));
        
        emergencyClient.post().uri("/emergency/g10/execute")
            .bodyValue(req)
            .exchange()
            .expectStatus().isOk()
            .expectBody().jsonPath("$.status").isEqualTo("UNFEASIBLE");
    }

    @Test
    void test_G11_Drug_Feasibility() {
        // C3 Met: Doctor Present
        DrugRequest req = new DrugRequest("P1", "DRUG_A", new DrugContext(true, "DOC_01"));
        
        treatmentClient.post().uri("/treatment/g11/execute")
            .bodyValue(req)
            .exchange()
            .expectStatus().isOk()
            .expectBody().jsonPath("$.status").isEqualTo("SUCCESS");
    }

    @Test
    void test_G12_Dose_Adaptation() {
        // C4 Violation: Drug NOT administered
        DoseRequest req = new DoseRequest("P1", 20.5, new DoseContext(false, 0.0));
        
        treatmentClient.post().uri("/treatment/g12/execute")
            .bodyValue(req)
            .exchange()
            .expectStatus().isOk()
            .expectBody().jsonPath("$.status").isEqualTo("UNFEASIBLE");
    }

    @Test
    void test_G9_Self_Adaptive_Loop() {
        // G9 Orchestration: G11 is unfeasible (no doctor), should fallback to G12 (feasible)
        MedicineRequest req = new MedicineRequest("P1", "MED", 50.0, 
            new DrugContext(false, "NONE"), 
            new DoseContext(true, 10.0));

        treatmentClient.post().uri("/treatment/g9/execute")
            .bodyValue(req)
            .exchange()
            .expectStatus().isOk()
            .expectBody().jsonPath("$.status").isEqualTo("SUCCESS")
            .jsonPath("$.message").isEqualTo("Dose updated via P8");
    }
}