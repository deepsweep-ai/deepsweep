# Testing Quick Start

Quick reference for testing DeepSweep's telemetry system and API integration.

---

## Available Testing Tools

### 1. Telemetry System Verification
```bash
./verify-telemetry.sh
```

**Tests:**
- Two-tier telemetry system (Essential + Optional)
- PostHog enable/disable functionality
- Offline mode verification
- UUID configuration

**What it does:**
- Runs validation with PostHog enabled (both tiers active)
- Runs validation with PostHog disabled (essential tier only)
- Runs validation in offline mode (no telemetry)
- Shows your UUID for PostHog dashboard lookup

---

### 2. API Endpoint Testing
```bash
./test-api-endpoint.sh
```

**Tests:**
- Valid threat signal requests
- Invalid request handling
- Response format validation (202 Accepted, status="accepted")
- Rate limiting (if implemented)

**What it does:**
- Sends curl requests to `https://api.deepsweep.ai/v1/signal`
- Validates API Contract v1.0.0 compliance
- Tests error cases (missing fields, wrong event type)
- Checks signal_id format

---

### 3. PostHog Integration Verification
```bash
./test-posthog.py
```

**Tests:**
- PostHog client initialization
- Event capture and queuing
- Debug output verification

**What it does:**
- Sends test events to PostHog
- Shows debug output for verification
- Provides UUID for dashboard lookup
- Mimics CLI validation events

---

### 4. Mock API Server (Local Testing)
```bash
./test-mock-server.py
```

**Use case:** Test CLI against local mock server

**What it does:**
- Runs mock `/v1/signal` endpoint on localhost:8080
- Validates request structure
- Returns proper 202 Accepted responses
- Logs all received signals for inspection

**Usage:**
```bash
# Terminal 1: Start mock server
./test-mock-server.py

# Terminal 2: Test CLI against mock
export DEEPSWEEP_INTEL_ENDPOINT=http://localhost:8080/v1/signal
deepsweep validate .
```

---

## Quick Verification Flow

**For CLI developers:**

```bash
# 1. Run unit tests
pytest

# 2. Run integration tests
bash test-integration.sh

# 3. Verify telemetry system
bash verify-telemetry.sh

# 4. Test PostHog (check dashboard after)
python test-posthog.py
```

**For backend developers:**

```bash
# 1. Test API endpoint
bash test-api-endpoint.sh

# 2. Check CloudWatch logs for requests
# Look for POST /v1/signal with proper structure

# 3. Verify DynamoDB entries
# Check signals table for stored threat signals

# 4. Monitor PostHog dashboard
# Search for distinct_id from ~/.deepsweep/config.json
```

---

## PostHog Dashboard Verification

1. **URL:** https://us.i.posthog.com
2. **Get your UUID:**
   ```bash
   cat ~/.deepsweep/config.json | grep uuid
   ```
3. **Find your events:**
   - Go to **Activity** → **Live events**
   - Search for your distinct_id (the UUID)
   - Look for events: `deepsweep_validate`, `deepsweep_telemetry`

4. **Timeline:** Events appear within 30-60 seconds

---

## API Endpoint Verification

**Expected request to `https://api.deepsweep.ai/v1/signal`:**

```json
{
  "event": "threat_signal",
  "version": "1",
  "install_id": "32_char_hex_hash",
  "pattern_ids": ["MCP-EXEC-001"],
  "cve_matches": ["CVE-2025-53109"],
  "severity_counts": {"CRITICAL": 1},
  ...
}
```

**Expected response (API Contract v1.0.0):**

```
HTTP/1.1 202 Accepted
Content-Type: application/json
X-DeepSweep-Version: 1.0.0

{
  "status": "accepted",
  "signal_id": "sig_a1b2c3d4e5f6",
  "message": "Threat signal received"
}
```

**CRITICAL:** Must be `202 Accepted` (NOT 200 OK) and status="accepted" (NOT "ok")

---

## Environment Variables

**Testing overrides:**

```bash
# Use local/staging API endpoint
export DEEPSWEEP_INTEL_ENDPOINT=http://localhost:8080/v1/signal

# Enable offline mode (no telemetry)
export DEEPSWEEP_OFFLINE=1

# Disable PostHog debug output
unset POSTHOG_DEBUG
```

---

## Troubleshooting

### PostHog events not appearing?
- Check UUID: `cat ~/.deepsweep/config.json | grep uuid`
- Verify enabled: `deepsweep telemetry status`
- Wait 60 seconds for ingestion delay
- Check network: `curl https://us.i.posthog.com/`

### API endpoint not receiving signals?
- Check endpoint: `echo $DEEPSWEEP_INTEL_ENDPOINT`
- Verify not offline: `echo $DEEPSWEEP_OFFLINE` (should be empty)
- Check backend CloudWatch logs
- Test with mock server first

### Tests failing?
- Install dependencies: `pip install -e ".[dev]"`
- Clear config: `rm -rf ~/.deepsweep/`
- Check Python version: `python --version` (need 3.10+)
- Run pytest with verbose: `pytest -vv`

---

## Full Documentation

For comprehensive testing documentation including:
- Detailed API contract specifications
- Privacy verification procedures
- Performance benchmarks
- Production readiness checklist

See [TESTING.md](TESTING.md)

---

**Quick Links:**
- [Contributing Guide](../CONTRIBUTING.md)
- [Full Testing Docs](TESTING.md)
- [API Documentation](https://docs.deepsweep.ai/api)
