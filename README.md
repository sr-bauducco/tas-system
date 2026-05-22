# GoalD 2.0: Reactive Tele Assistance System (TAS)

[![Java 17](https://img.shields.io/badge/Java-17-blue.svg)](https://www.oracle.com/java/)
[![Spring Boot](https://img.shields.io/badge/Spring%20Boot-3.2.0-brightgreen.svg)](https://spring.io/projects/spring-boot)
[![Spring Cloud](https://img.shields.io/badge/Spring%20Cloud-2023.0.0-blue.svg)](https://spring.io/projects/spring-cloud)

This repository contains a modernized, cloud-native implementation of the **Tele Assistance System (TAS)**, originally an exemplar for self-adaptive systems. It utilizes the **GoalD Framework** principles to dynamically adapt its deployment topology based on real-time environmental contexts (e.g., internet availability, patient vitals).

## Architectural Evolution: From OSGi to Microservices

Originally, GoalD managed adaptability by hot-swapping local OSGi bundles within a single JVM. This project elevates the GoalD methodology into a **distributed, reactive microservices environment**:

* **Network-Isolated Processes:** Implementation agents are completely decoupled into independent Spring Boot containers.
* **Decentralized MAPE-K:** The adaptation loop is no longer a centralized monolith. Context monitoring and execution are handled via network routing.
* **Reactive Non-Blocking I/O:** Built on Spring WebFlux and Project Reactor to handle distributed network fallacies and ensure high availability during adaptations.

## How the Distributed MAPE-K Loop Works

Instead of stopping and starting local JAR files, adaptation happens dynamically on the network layer through a decentralized MAPE-K control loop:

1. **Monitor:** Core services and sensors observe the environment and inject context states (e.g., internet availability, patient vitals) into cross-service requests using `X-Context-*` HTTP headers.
2. **Analyze:** The **Spring Cloud Gateway** (acting as the GoalD Manager) intercepts these requests and analyzes the active contexts to identify if the currently requested goal (e.g., *Notify Emergency*) is at risk of failing, or if newly available contexts offer an opportunity to improve the system.
3. **Plan:** The Gateway evaluates the internal **Deployment Variability Model (DVM)**. It filters out any implementation strategies that are unachievable under the current context. For the remaining valid alternatives, it calculates their expected Quality of Service (QoS) and *plans* the adaptation by selecting the service route that yields the highest score.
4. **Execute:** The Gateway translates the plan into action by dynamically rewriting its `RouteLocator` to forward the network request to the winning microservice strategy (e.g., seamlessly rerouting traffic from `ms-send-sms` to `ms-alarm-service` without restarting any containers).
5. **Knowledge:** **Netflix Eureka** serves as the dynamic knowledge base and service registry, maintaining the real-time truth of which implementation agents (Docker containers) are currently online, healthy, and available to receive traffic.

## Project Structure

The project follows a strict separation of goal definitions (contracts) from implementation agents, structured as a Maven multi-module project:

```text
tas-parent/
├── api-definitions/   # Shared Interfaces and DTOs (The "Goal Definitions")
├── ms-registry/       # Netflix Eureka Server (The Knowledge Base)
├── ms-gateway/        # Spring Cloud Gateway (The Context-Aware Planner)
├── ms-monitor/        # TAS Core: Monitors patient vitals
├── ms-intelligence/   # TAS Core: Analyzes data locally or remotely
├── ms-treatment/      # TAS Core: Enacts medical treatments
└── ms-emergency/      # Implementation Agents: Alarm Service vs. SMS Service