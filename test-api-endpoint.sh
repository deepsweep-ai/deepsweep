#!/bin/bash
set -e

# DeepSweep API Endpoint Testing Script
# Tests the /v1/signal endpoint with curl

# Color output (respects NO_COLOR)
if [ -z "$NO_COLOR" ]; then
    GREEN='\033[0;32m'
    RED='\033[0;31m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    NC='\033[0m'
else
    GREEN=''
    RED=''
    YELLOW=''
    BLUE=''
    NC=''
fi

# Configuration
ENDPOINT="${DEEPSWEEP_INTEL_ENDPOINT:-https://api.deepsweep.ai/v1/signal}"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%S.%6N+00:00")

echo "============================================================"
echo "DeepSweep API Endpoint Testing"
echo "============================================================"
echo -e "Endpoint: ${BLUE}$ENDPOINT${NC}"
echo "Timestamp: $TIMESTAMP"
echo ""

# Test 1: Valid signal
echo "============================================================"
echo "TEST 1: Valid Threat Signal"
echo "============================================================"

RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST "$ENDPOINT" \
  -H "Content-Type: application/json" \
  -H "User-Agent: deepsweep-cli/1.2.0" \
  -d "{
    \"event\": \"threat_signal\",
    \"version\": \"1\",
    \"pattern_ids\": [\"TEST-001\", \"TEST-002\"],
    \"cve_matches\": [\"CVE-2025-53109\"],
    \"severity_counts\": {
      \"CRITICAL\": 1,
      \"HIGH\": 1,
      \"MEDIUM\": 0,
      \"LOW\": 0
    },
    \"tool_context\": [],
    \"file_types\": [],
    \"score\": 85,
    \"grade\": \"B\",
    \"finding_count\": 2,
    \"file_count\": 5,
    \"duration_ms\": 42,
    \"cli_version\": \"1.2.0\",
    \"python_version\": \"3.12.0\",
    \"os_type\": \"linux\",
    \"is_ci\": false,
    \"ci_provider\": null,
    \"timestamp\": \"$TIMESTAMP\",
    \"install_id\": \"test_install_id_32chars_hash1\",
    \"session_id\": \"test_session_16c\"
  }")

# Extract HTTP status
HTTP_STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_STATUS/d')

echo "Response Code: $HTTP_STATUS"
echo "Response Body:"
echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
echo ""

# Validate response
if [ "$HTTP_STATUS" = "202" ]; then
    echo -e "${GREEN}[PASS]${NC} HTTP 202 Accepted (correct)"
elif [ "$HTTP_STATUS" = "200" ]; then
    echo -e "${RED}[FAIL]${NC} HTTP 200 OK (should be 202 Accepted)"
else
    echo -e "${RED}[FAIL]${NC} HTTP $HTTP_STATUS (expected 202)"
fi

if echo "$BODY" | grep -q '"status".*:.*"accepted"'; then
    echo -e "${GREEN}[PASS]${NC} Response status is 'accepted'"
else
    echo -e "${RED}[FAIL]${NC} Response status is not 'accepted' (check API contract)"
fi

if echo "$BODY" | grep -q '"signal_id".*:.*"sig_'; then
    echo -e "${GREEN}[PASS]${NC} Signal ID format correct (starts with 'sig_')"
else
    echo -e "${RED}[FAIL]${NC} Signal ID format incorrect (should start with 'sig_')"
fi

echo ""
read -p "Press Enter to continue to next test..."
echo ""

# Test 2: Missing required field
echo "============================================================"
echo "TEST 2: Invalid Request (Missing Fields)"
echo "============================================================"

RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST "$ENDPOINT" \
  -H "Content-Type: application/json" \
  -H "User-Agent: deepsweep-cli/1.2.0" \
  -d "{
    \"event\": \"threat_signal\"
  }")

HTTP_STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_STATUS/d')

echo "Response Code: $HTTP_STATUS"
echo "Response Body:"
echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
echo ""

if [ "$HTTP_STATUS" = "400" ]; then
    echo -e "${GREEN}[PASS]${NC} HTTP 400 Bad Request (correct for invalid request)"
else
    echo -e "${YELLOW}[WARN]${NC} Expected HTTP 400, got $HTTP_STATUS"
fi

echo ""
read -p "Press Enter to continue to next test..."
echo ""

# Test 3: Wrong event type
echo "============================================================"
echo "TEST 3: Wrong Event Type"
echo "============================================================"

RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST "$ENDPOINT" \
  -H "Content-Type: application/json" \
  -H "User-Agent: deepsweep-cli/1.2.0" \
  -d "{
    \"event\": \"wrong_event\",
    \"version\": \"1\",
    \"install_id\": \"test_id\",
    \"cli_version\": \"1.2.0\",
    \"timestamp\": \"$TIMESTAMP\"
  }")

HTTP_STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_STATUS/d')

echo "Response Code: $HTTP_STATUS"
echo "Response Body:"
echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
echo ""

if [ "$HTTP_STATUS" = "400" ]; then
    echo -e "${GREEN}[PASS]${NC} HTTP 400 Bad Request (correct for wrong event type)"
else
    echo -e "${YELLOW}[WARN]${NC} Expected HTTP 400, got $HTTP_STATUS"
fi

echo ""
read -p "Press Enter to continue to rate limit test..."
echo ""

# Test 4: Rate limiting (if implemented)
echo "============================================================"
echo "TEST 4: Rate Limiting (100 req/min per install_id)"
echo "============================================================"
echo "Sending 5 rapid requests with same install_id..."
echo ""

INSTALL_ID="rate_test_install_id_12345678"
SUCCESS_COUNT=0
RATE_LIMITED=0

for i in {1..5}; do
    RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST "$ENDPOINT" \
      -H "Content-Type: application/json" \
      -H "User-Agent: deepsweep-cli/1.2.0" \
      -d "{
        \"event\": \"threat_signal\",
        \"version\": \"1\",
        \"pattern_ids\": [],
        \"cve_matches\": [],
        \"severity_counts\": {},
        \"tool_context\": [],
        \"file_types\": [],
        \"score\": 100,
        \"grade\": \"A\",
        \"finding_count\": 0,
        \"file_count\": 1,
        \"duration_ms\": 10,
        \"cli_version\": \"1.2.0\",
        \"python_version\": \"3.12.0\",
        \"os_type\": \"linux\",
        \"is_ci\": false,
        \"ci_provider\": null,
        \"timestamp\": \"$TIMESTAMP\",
        \"install_id\": \"$INSTALL_ID\",
        \"session_id\": \"session_$i\"
      }" 2>/dev/null)

    HTTP_STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)

    if [ "$HTTP_STATUS" = "202" ]; then
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        echo -e "Request $i: ${GREEN}202 Accepted${NC}"
    elif [ "$HTTP_STATUS" = "429" ]; then
        RATE_LIMITED=$((RATE_LIMITED + 1))
        echo -e "Request $i: ${YELLOW}429 Too Many Requests${NC}"
    else
        echo -e "Request $i: ${RED}$HTTP_STATUS${NC}"
    fi
done

echo ""
echo "Results:"
echo "  - Accepted: $SUCCESS_COUNT"
echo "  - Rate Limited: $RATE_LIMITED"
echo ""

if [ $SUCCESS_COUNT -eq 5 ]; then
    echo -e "${BLUE}[INFO]${NC} All requests accepted (rate limiting may not be enforced yet)"
elif [ $RATE_LIMITED -gt 0 ]; then
    echo -e "${GREEN}[PASS]${NC} Rate limiting is enforced"
fi

echo ""

# Summary
echo "============================================================"
echo "TESTING SUMMARY"
echo "============================================================"
echo ""
echo "Endpoint tested: $ENDPOINT"
echo ""
echo "API Contract v1.0.0 Requirements:"
echo "  1. HTTP 202 Accepted (NOT 200 OK)"
echo "  2. Response: {\"status\": \"accepted\", \"signal_id\": \"sig_...\", ...}"
echo "  3. Header: X-DeepSweep-Version: 1.0.0"
echo "  4. Rate limit: 100 requests/minute per install_id"
echo ""
echo "Next steps:"
echo "  1. Check backend CloudWatch logs for requests"
echo "  2. Verify DynamoDB for stored signals"
echo "  3. Test with actual CLI: deepsweep validate ."
echo "  4. Monitor production metrics"
echo ""
echo "Done."
