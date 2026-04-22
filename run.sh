#!/bin/bash

echo "🚀 Performing Hard Reset and System Initialization..."

# 1. Kill any existing TAS processes to free up ports 8083/8084
pkill -f 'ms-treatment' || true
pkill -f 'ms-emergency' || true

# 2. Rebuild and Repackage
echo "📦 Building executable JARs..."
mvn clean install -DskipTests
if [ $? -ne 0 ]; then echo "❌ Build failed"; exit 1; fi

# 3. Start Services
echo "🔌 Starting ms-treatment (8083)..."
java -jar ms-treatment/target/ms-treatment-1.0-SNAPSHOT.jar > treatment.log 2>&1 &
echo "🔌 Starting ms-emergency (8084)..."
java -jar ms-emergency/target/ms-emergency-1.0-SNAPSHOT.jar > emergency.log 2>&1 &

# 4. Wait for stability
echo "⏳ Waiting 25 seconds for full system readiness..."
sleep 25

# 5. Run Automated Tests
echo "🧪 Running SystemOrchestrationTest..."
mvn test -pl ms-treatment -Dtest=SystemOrchestrationTest
TEST_RESULT=$?

# 6. Cleanup
pkill -f 'ms-treatment'
pkill -f 'ms-emergency'

if [ $TEST_RESULT -eq 0 ]; then
    echo "✅ SYSTEM FULLY VERIFIED: G10, G11, G12, and G9 are all operational."
else
    echo "❌ VERIFICATION FAILED. Check emergency.log for 404 details."
fi