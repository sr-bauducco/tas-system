package agent;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.reactive.server.WebTestClient;
import goals.request.*;
import goals.context.*;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.DEFINED_PORT)
public class TreatmentSystemTest {

    @Autowired
    private WebTestClient webTestClient;

    @Test
    void verify_G11_Feasibility_Guard() {
        DrugRequest unfeasibleRequest = new DrugRequest("P1", "MED_A", new DrugContext(false, null));

        webTestClient.post().uri("/treatment/g11/execute")
            .contentType(MediaType.APPLICATION_JSON)
            .bodyValue(unfeasibleRequest)
            .exchange()
            .expectStatus().isOk()
            .expectBody().jsonPath("$.status").isEqualTo("UNFEASIBLE");
    }

    @Test
    void verify_G12_Success_Flow() {
        DoseRequest feasibleRequest = new DoseRequest("P1", 50.0, new DoseContext(true, 25.0));

        webTestClient.post().uri("/treatment/g12/execute")
            .contentType(MediaType.APPLICATION_JSON)
            .bodyValue(feasibleRequest)
            .exchange()
            .expectStatus().isOk()
            .expectBody().jsonPath("$.status").isEqualTo("SUCCESS");
    }
}