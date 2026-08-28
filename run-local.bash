#!/bin/bash
# run-local.bash - Builds and launches the TAS distributed system on local ports

echo "[1/2] Compiling all Bounded Contexts with Maven..."
mvn clean package -DskipTests

echo "[2/2] Bootstrapping microservices..."

# ARCHITECTURAL FIX: Explicitly create the logs directory to prevent I/O crashes
mkdir -p logs

echo "-> Starting Eureka Registry (Port 8761)..."
java -jar ms-registry/target/*.jar > logs/registry.log 2>&1 &

# RESILIENCE FIX: Active readiness probe replacing the fragile 'sleep 10'
echo "-> Waiting for Eureka Server to establish network readiness..."
until curl -s http://localhost:8761/eureka/apps > /dev/null; do
    echo "   ...awaiting Eureka heartbeat..."
    sleep 2
done
echo "-> Eureka is UP and accepting registrations!"

echo "-> Launching GoalD MAPE-K Edge Planner and Domain Microservices..."
java -jar ms-gateway/target/*.jar > logs/gateway.log 2>&1 &
java -jar ms-intelligence/target/*.jar > logs/intelligence.log 2>&1 &
java -jar ms-treatment/target/*.jar > logs/treatment.log 2>&1 &
java -jar ms-emergency/target/*.jar > logs/emergency.log 2>&1 &
java -jar ms-monitor/target/*.jar > logs/monitor.log 2>&1 &

echo "All services launched. Monitoring health on Gateway (port 8080)..."