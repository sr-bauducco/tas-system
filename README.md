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
    for i in {1..10}; do
    curl -X POST http://localhost:8080/notify \
    -H "Content-Type: application/json" \
    -d "{\"patientId\":\"P-00$i\", \"alertType\":\"Tachycardia\", \"severity\": 90.0}" &
    done
    wait   
    echo "All concurrent requests fired."