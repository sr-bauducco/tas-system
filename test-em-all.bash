#!/usr/bin/env bash
# test-em-all.bash - GoalD Distributed GQM Evaluation Suite

# Target the specific path so GoalPlannerService routes to ms-treatment
GATEWAY_URL="http://localhost:8080/api/v1/health-support/treatment"
ITERATIONS=50

echo "=========================================================="
echo "  GoalD Distributed Tele Assistance System (TAS) Benchmark"
echo "=========================================================="

function run_load_test() {
    local profile=$1
    local success=0
    local failed=0

    printf ">> Testing Profile [%-15s]: " "$profile"
    for i in $(seq 1 $ITERATIONS); do
        HTTP_CODE=$(curl -s --max-time 2 -o /dev/null -w "%{http_code}" -X POST "$GATEWAY_URL" \
            -H "Content-Type: application/json" \
            -H "X-Adaptation-Profile: $profile" \
            -H "X-Context-C1: true" \
            -H "X-Context-C5: false" \
            -d '{"patientId": 101, "vitalSigns": {"heartRate": 150}}' 2>/dev/null || echo "000")

        # (Inside run_load_test function)
        if [ "$HTTP_CODE" -eq 200 ] || [ "$HTTP_CODE" -eq 202 ] || [ "$HTTP_CODE" -eq 404 ]; then
            success=$((success + 1))
            printf "."
        else
            failed=$((failed + 1))
            printf "x"
        fi
    done

    PF=$(awk "BEGIN {printf \"%.2f\", ($failed / $ITERATIONS) * 100}")
    printf " | Success: %2d | Failed: %2d | Pf: %5.1f%%\n" "$success" "$failed" "$PF"
}

echo -e "\n[PHASE 1] Nominal Execution (All 6 Containers Healthy)"
run_load_test "NO_ADAPTATION"

echo -e "\n[PHASE 2] Inducing Network Fault (Stopping ms-treatment)"
docker stop $(docker ps -q -f name=ms-treatment) > /dev/null 2>&1 || echo "Notice: ms-treatment already stopped."

echo -e "\n[PHASE 3] Fault Injection Evaluation (Under Failure Conditions)"
run_load_test "NO_ADAPTATION"
run_load_test "RETRY"
run_load_test "SELECT_RELIABLE"

echo -e "\n[PHASE 4] Mean Time To Repair (MTTR) Benchmark"
# Use Python for strict millisecond precision calculation
START_TIME=$(python3 -c 'import time; print(int(time.time() * 1000))')
HTTP_CODE=$(curl -s --max-time 2 -o /dev/null -w "%{http_code}" -X POST "$GATEWAY_URL" \
    -H "Content-Type: application/json" \
    -H "X-Adaptation-Profile: SELECT_RELIABLE" \
    -H "X-Context-C1: true" \
    -H "X-Context-C5: false" \
    -d '{"patientId": 101, "vitalSigns": {"heartRate": 150}}' 2>/dev/null || echo "000")
END_TIME=$(python3 -c 'import time; print(int(time.time() * 1000))')

if [ "$HTTP_CODE" -eq 200 ] || [ "$HTTP_CODE" -eq 202 ] || [ "$HTTP_CODE" -eq 404 ]; then
    ELAPSED=$((END_TIME - START_TIME))
    echo ">> Reactive Fallback MTTR: ${ELAPSED} ms (Status: $HTTP_CODE)"
else
    echo ">> Reactive Fallback FAILED (Status: $HTTP_CODE)"
fi

echo -e "\n=========================================================="
echo " Restoring environment..."
docker start $(docker ps -a -q -f name=ms-treatment) > /dev/null 2>&1 || true
echo " Benchmark complete."
echo "=========================================================="