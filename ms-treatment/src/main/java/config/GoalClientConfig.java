@Configuration
public class GoalClientConfig {

    @Bean
    public G10 emergencyClient(WebClient.Builder builder) {
        WebClient client = builder.baseUrl("http://localhost:8084").build();
        
        return request -> client.post()
            .uri("/goals/g10")
            .bodyValue(request)
            .retrieve()
            .bodyToMono(FulfillmentStatus.class);
    }
}