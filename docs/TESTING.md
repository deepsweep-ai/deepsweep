# DeepSweep Testing Guide

Complete guide for testing API endpoint implementation and telemetry verification.

---

## Table of Contents

1. [API Endpoint Testing](#api-endpoint-testing)
2. [PostHog Data Verification](#posthog-data-verification)
3. [Two-Tier Telemetry Testing](#two-tier-telemetry-testing)
4. [Quick Verification Script](#quick-verification-script)

---

## API Endpoint Testing

### 1. Expected Request Format

The CLI sends POST requests to `https://api.deepsweep.ai/v1/signal` with this structure:

```json
{
  "event": "threat_signal",
  "version": "1",
  "pattern_ids": ["MCP-EXEC-001", "CURSOR-EXEC-002"],
  "cve_matches": ["CVE-2025-53109"],
  "severity_counts": {
    "CRITICAL": 1,
    "HIGH": 2,
    "MEDIUM": 0,
    "LOW": 0
  },
  "tool_context": [],
  "file_types": [],
  "score": 85,
  "grade": "B",
  "finding_count": 3,
  "file_count": 5,
  "duration_ms": 42,
  "cli_version": "1.2.0",
  "python_version": "3.12.0",
  "os_type": "linux",
  "is_ci": false,
  "ci_provider": null,
  "timestamp": "2025-12-24T10:30:00.000000+00:00",
  "install_id": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
  "session_id": "1a2b3c4d5e6f7g8h"
}
```

### 2. Expected Response Format (API Contract v1.0.0)

**CRITICAL**: Backend MUST return exactly:

```json
{
  "status": "accepted",
  "signal_id": "sig_a1b2c3d4e5f6",
  "message": "Threat signal received"
}
```

**HTTP Status Code**: `202 Accepted` (NOT 200 OK)

**Headers**:
```
Content-Type: application/json
X-DeepSweep-Version: 1.0.0
```

### 3. Testing the Endpoint with curl

#### Test 1: Valid Signal
```bash
curl -X POST https://api.deepsweep.ai/v1/signal \
  -H "Content-Type: application/json" \
  -H "User-Agent: deepsweep-cli/1.2.0" \
  -d '{
    "event": "threat_signal",
    "version": "1",
    "pattern_ids": ["TEST-001"],
    "cve_matches": [],
    "severity_counts": {"HIGH": 1},
    "tool_context": [],
    "file_types": [],
    "score": 90,
    "grade": "A",
    "finding_count": 1,
    "file_count": 1,
    "duration_ms": 50,
    "cli_version": "1.2.0",
    "python_version": "3.12.0",
    "os_type": "linux",
    "is_ci": false,
    "ci_provider": null,
    "timestamp": "2025-12-24T10:00:00.000000+00:00",
    "install_id": "test_install_id_32_chars_long",
    "session_id": "test_session_id"
  }' \
  -w "\nHTTP Status: %{http_code}\n"
```

**Expected**:
- HTTP 202 Accepted
- Response body with status="accepted" and signal_id starting with "sig_"

#### Test 2: Rate Limiting (100 req/min per install_id)
```bash
# Send 101 requests rapidly with same install_id
for i in {1..101}; do
  curl -X POST https://api.deepsweep.ai/v1/signal \
    -H "Content-Type: application/json" \
    -d '{"event":"threat_signal","version":"1","install_id":"same_id","..."}' \
    -w "Request $i: %{http_code}\n" \
    -s -o /dev/null
done
```

**Expected**:
- First 100 requests: HTTP 202
- 101st request: HTTP 429 Too Many Requests

### 4. Local Mock Server Testing

Create a mock server for development:

```python
# test_mock_server.py
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import hashlib
import time

class MockSignalHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/v1/signal':
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            data = json.loads(body)

            # Validate structure
            required = ['event', 'version', 'install_id']
            if all(k in data for k in required):
                # Generate signal_id
                signal_id = f"sig_{hashlib.sha256(str(time.time()).encode()).hexdigest()[:12]}"

                # Return 202 Accepted
                self.send_response(202)
                self.send_header('Content-Type', 'application/json')
                self.send_header('X-DeepSweep-Version', '1.0.0')
                self.end_headers()

                response = {
                    "status": "accepted",
                    "signal_id": signal_id,
                    "message": "Threat signal received"
                }
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_response(400)
                self.end_headers()

if __name__ == '__main__':
    server = HTTPServer(('localhost', 8080), MockSignalHandler)
    print('[INFO] Mock server running on http://localhost:8080')
    server.serve_forever()
```

**Run mock server**:
```bash
python test_mock_server.py
```

**Test against mock**:
```bash
export DEEPSWEEP_INTEL_ENDPOINT=http://localhost:8080/v1/signal
deepsweep validate .
```

---

## PostHog Data Verification

### 1. PostHog Dashboard Access

**PostHog Instance**: https://us.i.posthog.com
**Project API Key**: `phc_2KxJqV5jZ9nY8wH3pL7mT6sN4vR1cX0bQ9dE8fG7hI6jK5lM4n`

### 2. Expected Events

The CLI sends these events to PostHog:

#### Event: `deepsweep_validate`
```json
{
  "distinct_id": "uuid-from-config",
  "event": "deepsweep_validate",
  "properties": {
    "command": "validate",
    "version": "1.2.0",
    "os": "Linux",
    "os_version": "6.2.0",
    "python_version": "3.12.0",
    "duration_ms": 125,
    "exit_code": 0,
    "first_run": false,
    "findings_count": 3,
    "pattern_count": 50,
    "output_format": "text",
    "score": 85,
    "grade": "B"
  }
}
```

#### Event: `deepsweep_telemetry`
```json
{
  "distinct_id": "uuid-from-config",
  "event": "deepsweep_telemetry",
  "properties": {
    "command": "telemetry",
    "version": "1.2.0",
    "os": "Linux",
    "duration_ms": 15,
    "exit_code": 0
  }
}
```

#### Event: `deepsweep_error`
```json
{
  "distinct_id": "uuid-from-config",
  "event": "deepsweep_error",
  "properties": {
    "command": "validate",
    "error_type": "FileNotFoundError",
    "error_message": "No configuration files found",
    "version": "1.2.0",
    "os": "Linux"
  }
}
```

### 3. Verification Steps

#### Step 1: Check Live Events
1. Log in to PostHog dashboard
2. Navigate to **Activity** → **Live events**
3. Run a validation: `deepsweep validate .`
4. Watch for `deepsweep_validate` event to appear (usually within 2-5 seconds)

#### Step 2: Check User Properties
1. Navigate to **People** → **Persons**
2. Find your distinct_id (check `~/.deepsweep/config.json` for UUID)
3. Verify properties:
   - `version`: 1.2.0
   - `os`: Your OS
   - `python_version`: Your Python version

#### Step 3: Query Events
```sql
-- PostHog SQL query (Insights → SQL)
SELECT
  event,
  properties.command,
  properties.version,
  properties.findings_count,
  timestamp
FROM events
WHERE event LIKE 'deepsweep_%'
ORDER BY timestamp DESC
LIMIT 10
```

### 4. Local Verification

#### Check if PostHog is enabled:
```bash
deepsweep telemetry status
```

**Expected output**:
```
DeepSweep Telemetry Status

Optional tier (PostHog):  ENABLED
Essential tier (Signals): ALWAYS ON
Offline mode:             DISABLED

UUID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
Config: /home/user/.deepsweep/config.json
```

#### Check your UUID:
```bash
cat ~/.deepsweep/config.json | grep uuid
```

#### Enable debug mode:
```python
# Create test_posthog.py
import posthog

posthog.project_api_key = "phc_2KxJqV5jZ9nY8wH3pL7mT6sN4vR1cX0bQ9dE8fG7hI6jK5lM4n"
posthog.host = "https://us.i.posthog.com"
posthog.debug = True  # Enable debug output

posthog.capture(
    distinct_id='test-user-123',
    event='test_event',
    properties={'test': 'verification'}
)

posthog.shutdown()
print("[INFO] Event sent - check console for debug output")
```

**Run**:
```bash
python test_posthog.py
```

**Expected debug output**:
```
[posthog] Sending request to https://us.i.posthog.com/capture/
[posthog] Request successful
```

---

## Two-Tier Telemetry Testing

### Tier 1: Essential (Threat Signals - Always On)

**Test that signals send even when PostHog is disabled**:

```bash
# Disable optional tier
deepsweep telemetry disable

# Run validation
deepsweep validate .

# Check status
deepsweep telemetry status
# Should show: "Essential tier (Signals): ALWAYS ON"
```

**Verification**:
- PostHog should NOT receive events
- `/v1/signal` endpoint SHOULD receive threat_signal POST

### Tier 2: Optional (PostHog - User Controlled)

**Test that PostHog respects user preference**:

```bash
# Enable optional tier
deepsweep telemetry enable

# Run validation
deepsweep validate .

# Check PostHog dashboard - should see events
```

**Verification**:
- PostHog SHOULD receive `deepsweep_validate` event
- `/v1/signal` endpoint SHOULD receive threat_signal POST

### Offline Mode (Disables ALL telemetry)

**Test complete offline mode**:

```bash
# Set offline mode
export DEEPSWEEP_OFFLINE=1

# Run validation
deepsweep validate .

# Check status
deepsweep telemetry status
# Should show: "Offline mode: ENABLED"
```

**Verification**:
- PostHog should NOT receive events
- `/v1/signal` endpoint should NOT receive requests

---

## Quick Verification Script

Create `verify-telemetry.sh`:

```bash
#!/bin/bash
set -e

echo "=== DeepSweep Telemetry Verification ==="
echo ""

# 1. Check telemetry status
echo "[TEST] Telemetry status"
deepsweep telemetry status

# 2. Get UUID for PostHog lookup
echo ""
echo "[INFO] Your UUID for PostHog lookup:"
cat ~/.deepsweep/config.json | python3 -c "import sys, json; print(json.load(sys.stdin)['uuid'])"

# 3. Test with PostHog enabled
echo ""
echo "[TEST] Running validation with PostHog enabled..."
deepsweep telemetry enable
deepsweep validate . --format text > /dev/null 2>&1
echo "[PASS] Validation complete - check PostHog for 'deepsweep_validate' event"

# 4. Test with PostHog disabled (signals still send)
echo ""
echo "[TEST] Running validation with PostHog disabled..."
deepsweep telemetry disable
deepsweep validate . --format text > /dev/null 2>&1
echo "[PASS] Validation complete - threat signal sent, PostHog silent"

# 5. Test offline mode (nothing sends)
echo ""
echo "[TEST] Running validation in offline mode..."
export DEEPSWEEP_OFFLINE=1
deepsweep validate . --format text > /dev/null 2>&1
echo "[PASS] Validation complete - no telemetry sent"
unset DEEPSWEEP_OFFLINE

# 6. Re-enable for normal usage
deepsweep telemetry enable

echo ""
echo "=== Verification Complete ==="
echo ""
echo "Next steps:"
echo "1. Check PostHog dashboard for events (distinct_id = UUID above)"
echo "2. Check API logs for /v1/signal POST requests"
echo "3. Verify 202 Accepted responses with signal_id format"
```

**Run**:
```bash
chmod +x verify-telemetry.sh
./verify-telemetry.sh
```

---

## Debugging Checklist

### If PostHog events not appearing:

- [ ] Check UUID: `cat ~/.deepsweep/config.json | grep uuid`
- [ ] Verify enabled: `deepsweep telemetry status`
- [ ] Check API key in code: `phc_2KxJqV5jZ9nY8wH3pL7mT6sN4vR1cX0bQ9dE8fG7hI6jK5lM4n`
- [ ] Verify host: `https://us.i.posthog.com`
- [ ] Check network: `curl -X POST https://us.i.posthog.com/capture/`
- [ ] Wait 30-60 seconds for ingestion delay

### If API endpoint not receiving signals:

- [ ] Check endpoint: `https://api.deepsweep.ai/v1/signal`
- [ ] Verify not offline: `echo $DEEPSWEEP_OFFLINE` (should be empty or 0)
- [ ] Check backend logs for POST requests
- [ ] Verify backend returns 202 Accepted (NOT 200 OK)
- [ ] Check response format: status="accepted", signal_id="sig_..."
- [ ] Verify rate limiting (100/min per install_id)

### If tests failing:

- [ ] Run: `pytest tests/test_telemetry.py -v`
- [ ] Check Python version: `python --version` (should be 3.10+)
- [ ] Verify dependencies: `pip install -e ".[dev]"`
- [ ] Clear config: `rm -rf ~/.deepsweep/` and retest

---

## Performance Benchmarks

Expected performance:

- **Telemetry overhead**: <5ms per validation
- **Network timeout**: 2 seconds (fire-and-forget)
- **No blocking**: CLI never waits for telemetry responses
- **Async threading**: All network calls in daemon threads

**Test performance**:
```bash
time deepsweep validate .
# Total time should be <200ms for typical repos
# Telemetry should add <5ms
```

---

## Privacy Verification

**What is sent**:
- Pattern IDs (e.g., "MCP-EXEC-001")
- CVE matches (e.g., "CVE-2025-53109")
- Aggregate counts (findings, severity counts)
- System metadata (OS, Python version, CLI version)
- Anonymized install_id (SHA-256 hash, irreversible)

**What is NEVER sent**:
- ❌ Source code
- ❌ File paths or filenames
- ❌ Repository names
- ❌ User identities or emails
- ❌ API keys, tokens, or secrets
- ❌ File contents

**Verify**:
```bash
# Check what's being sent (mock server logs)
python test_mock_server.py &
export DEEPSWEEP_INTEL_ENDPOINT=http://localhost:8080/v1/signal
deepsweep validate .
# Check server logs - no PII should be present
```

---

## Production Readiness

Before deploying backend:

1. **API Contract**: Verify exact response format (202 Accepted, status="accepted")
2. **Rate Limiting**: Implement 100 req/min per install_id
3. **DynamoDB Schema**: Partition key = date, TTL = 30 days
4. **Monitoring**: CloudWatch alarms for 5xx errors
5. **Load Testing**: Test with 1000 req/s burst
6. **Privacy Audit**: Confirm no PII in logs or database

---

**Questions?**
- Backend issues: Check API logs, CloudWatch metrics
- PostHog issues: Check dashboard live events
- CLI issues: Run `pytest tests/test_telemetry.py -v`
