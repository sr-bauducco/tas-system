#!/bin/bash

# ==============================================================================
# TAS System Lifecycle & Automated Validation Utility
# Purpose: Orchestrates the build, deployment, and testing of GoalD services.
# Usage: ./run-system.sh
# ==============================================================================

set -e # Exit on any command failure

# --- Configuration ---
TREATMENT_JAR="ms-treatment/target/ms-treatment-1.0-SNAPSHOT.jar"
EMERGENCY_JAR="ms-emergency/target/ms-emergency-1.0-SNAPSHOT.jar"
WAIT_SECONDS=25

# --- Cleanup Logic ---
cleanup() {
    echo "[INFO] Commencing system shutdown and process cleanup..."
    pkill -f 'ms-treatment' || true
    pkill -f 'ms-emergency' || true
}

# Ensure cleanup is triggered on script exit, interruption, or termination
trap cleanup EXIT SIGINT SIGTERM

log_info() {
    echo "[INFO] $(date +'%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo "[ERROR] $(date +'%Y-%m-%d %H:%M:%S') - $1" >&2
}

# --- Main Execution ---

log_info "Initiating TAS Reactive Architecture build phase..."
mvn clean install -DskipTests -q
if [ $? -ne 0 ]; then
    log_error "Maven build failed. Aborting deployment."
    exit 1
fi

log_info "Verifying executable artifacts..."
if [[ ! -f "$TREATMENT_JAR" || ! -f "$EMERGENCY_JAR" ]]; then
    log_error "One or more target JAR files are missing. Verify pom.xml repackage settings."
    exit 1
fi

log_info "Starting ms-treatment on port 8083..."
java -jar "$TREATMENT_JAR" > treatment-service.log 2>&1 &

log_info "Starting ms-emergency on port 8084..."
java -jar "$EMERGENCY_JAR" > emergency-service.log 2>&1 &

log_info "Waiting ${WAIT_SECONDS}s for full system convergence..."
sleep "$WAIT_SECONDS"

log_info "Executing automated system-wide validation (G9, G10, G11, G12)..."
mvn test -pl ms-treatment -Dtest=SystemOrchestrationTest
TEST_STATUS=$?

if [ $TEST_STATUS -eq 0 ]; then
    log_info "SYSTEM VALIDATION SUCCESSFUL: All architectural goals verified."
else
    log_error "SYSTEM VALIDATION FAILED: Review service logs for details."
fi

exit $TEST_STATUS