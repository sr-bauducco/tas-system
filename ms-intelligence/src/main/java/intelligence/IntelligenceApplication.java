package intelligence;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.client.discovery.EnableDiscoveryClient;
import org.springframework.context.annotation.Bean;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.cloud.client.loadbalancer.LoadBalanced;

@SpringBootApplication(scanBasePackages = {"intelligence", "agent"}) // Scan both packages
@EnableDiscoveryClient
public class IntelligenceApplication {

    @Bean
    @LoadBalanced // Required for 'http://ms-emergency' URL to work
    public WebClient.Builder loadBalancedWebClientBuilder() {
        return WebClient.builder();
    }

    public static void main(String[] args) {
        SpringApplication.run(IntelligenceApplication.class, args);
    }
}