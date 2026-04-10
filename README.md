# Tele Assistance System (TAS) - GoalD Implementation

## Project Architecture
Following the GoalD framework and Magnus Larsson's patterns:
- **api-definitions**: Shared interfaces for Goal-Service contracts.
- **ms-monitor**: (G1) Reactive vital sign generator (Port 8081).
- **ms-analysis**: (G6) Orchestrator of the autonomic loop (Port 8082).
- **ms-emergency**: (G10) Emergency notification dispatcher (Port 8080).

## Structure
- /api-definitions: Shared Goal interfaces (contracts).
- /ms-emergency: Agent implementation

## Build
Run: mvn clean install

## Running:
    cd ms-emergency 
    mvn spring-boot:run

## Testing:
1. 
    for i in {1..10}; do
    curl -X POST http://localhost:8080/notify \
    -H "Content-Type: application/json" \
    -d "{\"patientId\":\"P-00$i\", \"alertType\":\"Tachycardia\", \"severity\": 90.0}" &
    done
    wait   
    echo "All concurrent requests fired."
