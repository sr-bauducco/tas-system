# Tele Assistance System (TAS) - GoalD Implementation

## Project Architecture
Following the GoalD framework and Magnus Larsson's patterns:
- **api-definitions**: Shared interfaces for Goal-Service contracts.
- **ms-monitor**: (G1) Reactive vital sign generator (Port 8081).
- **ms-analysis**: (G6) Orchestrator of the autonomic loop (Port 8082).
- **ms-emergency**: (G10) Emergency notification dispatcher (Port 8080).

## Execution Guide
1. **Compilation**:
   mvn clean install

2. **Run Services**:
   (Open 3 terminals)
   - Terminal 1: cd ms-emergency && mvn spring-boot:run
   - Terminal 2: cd ms-monitor && mvn spring-boot:run
   - Terminal 3: cd ms-analysis && mvn spring-boot:run