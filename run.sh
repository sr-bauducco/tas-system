#!/bin/bash

# TAS Unified Execution & Test Automation
echo "🚀 Initializing TAS Reactive Architecture..."

# 1. Build and Install all modules
echo "📦 Building modules..."
mvn clean install -DskipTests
if [ $? -ne 0 ]; then echo "❌ Build failed"; exit 1; fi

# 2. Start Microservices in the background
echo "🔌 Starting ms-treatment (Port 8083)..."
java -jar ms-treatment/target/ms-treatment-1.0-SNAPSHOT.jar > treatment.log 2>&1 &
TREATMENT_PID=$!

echo "🔌 Starting ms-emergency (Port 8084)..."
java -jar ms-emergency/target/ms-emergency-1.0-SNAPSHOT.jar > emergency.log 2>&1 &
EMERGENCY_PID=$!

# 3. Wait for services to be healthy
echo "⏳ Waiting for services to initialize..."
sleep 15 

# 4. Run Automated Integration Tests
echo "🧪 Running Automated GoalD Tests (G10, G11, G12)..."
mvn test -pl ms-treatment -Dtest=SystemOrchestrationTest
TEST_RESULT=$?

# 5. Shutdown and Cleanup
echo "🛑 Shutting down services..."
kill $TREATMENT_PID
kill $EMERGENCY_PID

if [ $TEST_RESULT -eq 0 ]; then
    echo "✅ ALL GOALS VERIFIED SUCCESSFULLY"
else
    echo "❌ TEST FAILURES DETECTED. Check logs."
fi

exit $TEST_RESULT