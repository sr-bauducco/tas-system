#!/usr/bin/env bash
# test-em-all.bash - GoalD Distributed GQM Evaluation Suite
set -e

GATEWAY_URL="http://localhost:8080/api/v1/health-support"
ITERATIONS=100

echo "========================================================="
echo " GoalD Distributed Microservices Evaluation"
echo "========================================================="

function run_load_test() {
    local profile=$1
    local success=0
    local failed=0

    echo ">> Executing Profile: $profile"
    for i in $(seq 1 $ITERATIONS); do
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$GATEWAY_URL" \
            -H "Content-Type: application/json" \
            -H "X-Adaptation-Profile: $profile" \
            -H "X-Context-C1: true" \
            -H "X-Context-C5: false" \
            -d '{"patientId": 101, "vitalSigns": {"heartRate": 150}}')

        if [ "$HTTP_CODE" -eq 200 ] || [ "$HTTP_CODE" -eq 202 ]; then
            ((success++))
        else
            ((failed++))
        fi
    done

    # Calculate Failure Rate (Pf)
    PF=$(echo "scale=2; ($failed / $ITERATIONS) * 100" | bc)
    echo "   Success: $success | Failed: $failed | Failure Rate (Pf): $PF%"
}

echo -e "\n[PHASE 1] Nominal Execution (All Containers Healthy)"
run_load_test "NO_ADAPTATION"

echo -e "\n[PHASE 2] Inducing Network Fault (Stopping ms-treatment)"
docker stop $(docker ps -q -f name=ms-treatment) || echo "Warning: ms-treatment container not found."

echo -e "\n[PHASE 3] Re-evaluating Failure Rates (Pf) under Fault Conditions"
run_load_test "NO_ADAPTATION"
run_load_test "RETRY"
run_load_test "SELECT_RELIABLE"

echo -e "\n[PHASE 4] MTTR Benchmark (Mean Time To Repair)"
START_TIME=$(date +%s%3N)
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$GATEWAY_URL" \
    -H "Content-Type: application/json" \
    -H "X-Adaptation-Profile: SELECT_RELIABLE" \
    -d '{"patientId": 101}')
END_TIME=$(date +%s%3N)

if [ "$HTTP_CODE" -eq 200 ] || [ "$HTTP_CODE" -eq 202 ]; then
    ELAPSED=$((END_TIME - START_TIME))
    echo ">> Reactive Fallback MTTR: ${ELAPSED} ms"
else
    echo ">> Reactive Fallback FAILED"
fi

echo "========================================================="
echo " Restarting environment..."
docker start $(docker ps -a -q -f name=ms-treatment)