# TAS: Goal-Oriented Distributed Microservices
Tele Assistance System with GoalD Framework Integration
### 1. Architectural Vision

The primary objective of this architecture is to decouple the system's strategic requirements (goals) from their technical implementations (microservices). By utilizing a Contextual Goal Model (CGM), the system dynamically adapts its deployment topology based on real-time environmental factors such as network availability, battery status, and sensor health.

- Key Evolutions:Transition from OSGi to Network-Isolated Processes: Replaced local bundle interactions with HTTP/REST communication using Spring WebFlux.  
- Reactive Pipelines: Implemented non-blocking I/O using Project Reactor to handle distributed computing fallacies and high concurrency.  
- Decentralized MAPE-K: The control loop is distributed across the infrastructure, with the API Gateway acting as a context-aware Planner.  

### 2. Distributed Goal-to-Service Mapping

We map the GoalD Contextual Goal Model to independent microservices:
Goal ID	Definition (Intent)	Implementation Service	Implementation Strategy
G0	Provide Health Support	ms-tas-orchestrator	

Root composite orchestrator.  
G4	Notify Emergency Services	ms-medical-services	

Dynamic selection (Alarm vs. SMS).  
G7	Get Vital Params	ms-sensor-gateway	

High-throughput data ingestion.  
G8	Analyze Data	ms-analytics-engine	

Local vs. Remote processing selection.

#### Distributed Sequence: Autonomous Adaptation (G4)

This diagram illustrates the means-end refinement process over the network, where the system proactively switches strategies based on the C1: Internet Connection context.

    participant O as TAS Orchestrator
    participant G as Spring Cloud Gateway (Planner)
    participant A as Alarm-Service (Strategy P3)
    participant S as SMS-Service (Strategy P2)

    Note over O, S: Context C1 is True (Internet Available)
    O->>G: POST /notify (Header: X-Context-C1: true)
    G->>A: Route to High-Quality Service
    A-->>G: 200 OK
    G-->>O: Success (Quality: 25)

    Note over O, S: Context Change Detected (!C1)
    O->>G: POST /notify (Header: X-Context-C1: false)
    G->>S: Route to Fallback Strategy
    S-->>G: 200 OK
    G-->>O: Success (Quality: 13)

### 3. Technology Stack & Prerequisites

    Core: Java 17+, Spring Boot 3.0.4+.  

    Reactive: Spring WebFlux, Project Reactor.  

    Connectivity: Spring Cloud Gateway, Netflix Eureka.  

    Persistence: Spring Data (MongoDB for non-blocking stores, MySQL for legacy state).  

    Observability: Micrometer Tracing, Zipkin, Prometheus.  

    Containerization: Docker, Docker Compose (for automated E2E system verification).

### 4. Implementation Guidelines
#### Separating Definitions from Agents

In accordance with GoalD principles, we maintain strict isolation between Goal Definitions (Shared Interface Models) and Implementation Agents (The actual microservices).
1. API Project: Contains Data Transfer Objects (DTOs) and Service Interfaces (e.g., ProductService.java).
2. Implementation Project: Contains the @RestController and business logic that realizes the goal.

#### Resilient Reactive Operators
All cross-service calls must utilize standard resilience patterns:
- flatMap: For transforming context-dependent responses.  
- onErrorResume: For providing GORE-based fallbacks when a service is unreachable. 
- switchIfEmpty: For handling missing data without breaking the stream.

5. Deployment & Testing
Automated System Verification

We utilize a unified verification script to ensure the Deployment Variability Model (DVM) is functioning correctly across the network.