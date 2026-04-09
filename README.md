# TAS - Tele Assistance System (GoalD Microservices)

## Project Overview
Modular TAS implementation following the GoalD pattern: Definition vs Implementation.

## Structure
- /api-definitions: Shared Goal interfaces (contracts).
- /microservices: Autonomous implementation agents.

## Build
Run: mvn clean install

## Running:
    cd ms-emergency 
    mvn spring-boot:run

## Testing:
1. 
    curl -X POST http://localhost:8080/notify \
    -H "Content-Type: application/json" \
    -d '{"patientId":"P-001", "alertType":"Tachycardia", "severity": 95.0}'
2. 
    curl -X POST http://localhost:8080/notify \
    -H "Content-Type: application/json" \
    -d '{"patientId":"P-001", "alertType":"Fever", "severity": 75.0}'