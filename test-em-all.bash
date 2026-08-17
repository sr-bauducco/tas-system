#!/usr/bin/env bash
set -e

HOST=localhost
PORT=8080

# --- Helper Functions ---

function assertEqual() {
  local expected=$1
  local actual=$2
  if [ "$actual" != "$expected" ]; then
    echo "ASSERTION FAILED: Expected '$expected' but got '$actual'"
    exit 1
  fi
}

function testUrl() {
  url=$@
  if curl $url -ks -f -o /dev/null
  then
    return 0
  else
    return 1
  fi;
}

function waitForService() {
  url=$@
  echo -n "Wait for: $url... "
  n=0
  until testUrl $url
  do
    n=$((n + 1))
    if [[ $n == 100 ]]
    then
      echo " Give up"
      exit 1
    else
      sleep 3
      echo -n ", retry #$n "
    fi
  done
  echo "DONE, continues..."
}

# --- Initialization ---

if [[ $@ == *"start"* ]]
then
  echo "Restarting the test environment..."
  echo "$ docker-compose down --remove-orphans"
  docker-compose down --remove-orphans
  echo "$ docker-compose up -d"
  docker-compose up -d
fi

# Wait for the API Gateway to be responsive[cite: 3]
waitForService http://$HOST:$PORT/actuator/health

# Allow additional time for Eureka Service Registry propagation
echo "Waiting for Eureka instance registrations to propagate..."
sleep 30

echo "========================================================"
echo "TEST 1: Dynamic Adaptation - G8 Analyze Data (Ideal Context)"
echo "========================================================"
# GoalD Context: C1_InternetConnection is TRUE by default
RESPONSE=$(curl -s -X POST http://$HOST:$PORT/ \
  -H "Content-Type: application/json" \
  -H "X-Target-Goal: G8_AnalyzeData" \
  -d '{"patientId": "pt-101", "heartRate": 115}')

# The Gateway should route to the High-QoS Strategy P6 (Remote)
ACTUAL_MESSAGE=$(echo $RESPONSE | jq -r .message)
assertEqual "CRITICAL: Tachycardia Detected (via P6)" "$ACTUAL_MESSAGE"
echo "SUCCESS: Gateway autonomously routed G8 to Remote Strategy (P6)."

echo "========================================================"
echo "TEST 2: Context Shift & Adaptation Fallback"
echo "========================================================"
# Simulate a physical sensor detecting a network outage
curl -s -X POST "http://$HOST:$PORT/api/context/C1_InternetConnection?state=false"

# Re-issue the exact same Goal execution request
RESPONSE=$(curl -s -X POST http://$HOST:$PORT/ \
  -H "Content-Type: application/json" \
  -H "X-Target-Goal: G8_AnalyzeData" \
  -d '{"patientId": "pt-101", "heartRate": 115}')

# The Gateway must intercept the lack of C1 and route to Fallback Strategy P5 (Local)
ACTUAL_MESSAGE=$(echo $RESPONSE | jq -r .message)
assertEqual "CRITICAL: Tachycardia Detected (via P5)" "$ACTUAL_MESSAGE"
echo "SUCCESS: Gateway autonomously adapted G8 to Local Fallback Strategy (P5)."

echo "========================================================"
echo "TEST 3: Distributed Orchestrator & Circuit Breaker (G1)"
echo "========================================================"
# Trigger the AND-Refinement Orchestrator in ms-monitor
# Since C1_InternetConnection is still FALSE, G10 must fallback to SMS instead of Alarm
RESPONSE=$(curl -s -X POST http://$HOST:$PORT/monitor/g1/execute/pt-101)

STATUS=$(echo $RESPONSE | jq -r .status)
assertEqual "SUCCESS" "$STATUS"
echo "SUCCESS: Orchestrator successfully combined G3 and G4 dynamically across the network."

# --- Teardown ---

if [[ $@ == *"stop"* ]]
then
  echo "We are done, stopping the test environment..."
  echo "$ docker-compose down"
  docker-compose down
fi

echo "End, all tests OK: $(date)"