#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
set -e

# Gateway coordinates
HOST=localhost
PORT=8080

# Helper function to check if a service is up
function testUrl() {
    url=$@
    if curl $url -ks -f -o /dev/null
    then
          return 0
    else
          return 1
    fi;
}

# Helper function to wait for the Gateway to be ready
function waitForService() {
    url=$@
    echo -n "Waiting for: $url... "
    n=0
    until testUrl $url
    do
        n=$((n + 1))
        if [[ $n == 20 ]]
        then
            echo " Give up"
            exit 1
        else
            sleep 3
            echo -n ", retry #$n "
        fi
    done
    echo "DONE, Gateway is ready!"
}

# Helper functions for assertions
function assertCurl() {
    local expectedHttpCode=$1
    local curlCmd="$2 -w \"%{http_code}\""
    local result=$(eval $curlCmd)
    local httpCode="${result: -3}"
    RESPONSE='' && (( ${#result} > 3 )) && RESPONSE="${result%???}"

    if [ "$httpCode" = "$expectedHttpCode" ]
    then
        echo "Test OK (HTTP Code: $httpCode)"
    else
        echo "Test FAILED, EXPECTED HTTP Code: $expectedHttpCode, GOT: $httpCode"
        echo "- Failing command: $curlCmd"
        echo "- Response Body: $RESPONSE"
        exit 1
    fi
}

function assertEqual() {
    local expected=$1
    local actual=$2

    if [ "$actual" = "$expected" ]
    then
        echo "Test OK (actual value: $actual)"
    else
        echo "Test FAILED, EXPECTED Value: $expected, GOT: $actual"
        exit 1
    fi
}

echo "Start Tests: $(date)"

# Wait for the API Gateway actuator health endpoint (assuming it's enabled)
# If not enabled, we just sleep for a few seconds to let Eureka sync.
echo "Giving Eureka 15 seconds to sync routing tables..."
sleep 15

# ---------------------------------------------------------
# TEST 1: Emergency Primary Route (Internet is UP)
# ---------------------------------------------------------
echo -e "\n=== Test 1: Emergency -> AlarmService (Internet UP) ==="
# We expect a 200 OK. The header dictates the route.
assertCurl 200 "curl -s -X POST http://$HOST:$PORT/emergency/g10/execute \
    -H \"Content-Type: application/json\" \
    -H \"X-Context-Internet: true\" \
    -d '{\"patientId\":\"P1\", \"riskLevel\":\"CRITICAL\"}'"

# ---------------------------------------------------------
# TEST 2: Emergency Fallback Route (Internet is DOWN)
# ---------------------------------------------------------
echo -e "\n=== Test 2: Emergency Fallback -> SendSMS (Internet DOWN) ==="
# By changing the header, the Gateway should fall back to SendSMS.
assertCurl 200 "curl -s -X POST http://$HOST:$PORT/emergency/g10/execute \
    -H \"Content-Type: application/json\" \
    -H \"X-Context-Internet: false\" \
    -d '{\"patientId\":\"P1\", \"riskLevel\":\"CRITICAL\"}'"


# ---------------------------------------------------------
# TEST 3: Treatment Primary Route (Doctor is Present)
# ---------------------------------------------------------
echo -e "\n=== Test 3: Treatment -> ChangeDrug (Doctor UP) ==="
assertCurl 200 "curl -s -X POST http://$HOST:$PORT/treatment/g11/execute \
    -H \"Content-Type: application/json\" \
    -H \"X-Context-Doctor: true\" \
    -d '{\"patientId\":\"P1\", \"drugId\":\"MED_A\"}'"

# ---------------------------------------------------------
# TEST 4: Treatment Guard Failure (Doctor is Absent)
# ---------------------------------------------------------
echo -e "\n=== Test 4: Treatment Guard -> Unfeasible (Doctor DOWN) ==="
# This tests your business logic guard. It should return 200 but with status UNFEASIBLE
assertCurl 200 "curl -s -X POST http://$HOST:$PORT/treatment/g11/execute \
    -H \"Content-Type: application/json\" \
    -H \"X-Context-Doctor: false\" \
    -d '{\"patientId\":\"P1\", \"drugId\":\"MED_A\"}'"

STATUS=$(echo $RESPONSE | jq -r .status)
assertEqual "UNFEASIBLE" "$STATUS"

echo -e "\nEnd, all tests OK: $(date)"