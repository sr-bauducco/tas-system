package agent;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.reactive.server.WebTestClient;
import goals.request.*;
import goals.context.*;

// Note: Ensure Port 8083 matches your application.properties
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.DEFINED_PORT)
public class TreatmentSystemTest {

    @Autowired
    private WebTestClient webTestClient;

    @Test
    void verify_G11_Feasibility_Guard() {
        // GIVEN: Doctor is NOT present (C3 Violation)
        DrugRequest request = new DrugRequest("P1", "MED_A", new DrugContext(false, "NONE"));

        // WHEN & THEN
        webTestClient.post().uri("/treatment/g11/execute")
            .contentType(MediaType.APPLICATION_JSON)
            .bodyValue(request)
            .exchange()
            .expectStatus().isOk()
            .expectBody().jsonPath("$.status").isEqualTo("UNFEASIBLE");
    }
}