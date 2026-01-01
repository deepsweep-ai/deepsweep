# Production Testing Guide - LIVE SYSTEM

⚠️ **CRITICAL: This system is LIVE in production** ⚠️

This guide provides controlled, safe methods to test production telemetry without polluting metrics.

---

## ✅ Phase 1: Safe Local Verification (COMPLETED)

You can run this anytime without affecting production:

```bash
python test_local_verification.py
```

**Status:** All 8/8 tests passing
- ✅ Code structure verified
- ✅ Configuration correct
- ✅ Payload generation working
- ✅ Privacy guarantees enforced
- ✅ Mock API interactions successful

---

## Phase 2: Controlled Production Testing

### Option A: Use Offline Mode (Recommended for initial testing)

This tests the CLI end-to-end **WITHOUT** sending telemetry:

```bash
# Enable offline mode
export DEEPSWEEP_OFFLINE=1

# Test the CLI (no telemetry sent)
deepsweep validate ./test-project

# Verify command works correctly
# Check output, scoring, etc.

# When done, disable offline mode
unset DEEPSWEEP_OFFLINE
```

**What this does:**
- ✅ Tests full CLI functionality
- ✅ Verifies validation logic
- ✅ No telemetry sent to PostHog
- ✅ No signals sent to threat intel API
- ✅ Zero impact on production metrics

---

### Option B: Single Controlled Test (Minimal Impact)

**WARNING:** This sends ONE event to production APIs.

Use this to verify connectivity **once**:

```bash
# Create a test directory with a simple file
mkdir -p /tmp/deepsweep-test
echo "print('test')" > /tmp/deepsweep-test/test.py

# Run ONE validation
deepsweep validate /tmp/deepsweep-test --format json

# Clean up
rm -rf /tmp/deepsweep-test
```

**What this sends:**

1. **PostHog Event:**
   - Event: `deepsweep_validate`
   - Properties: findings_count, score, grade, etc.
   - Your unique UUID

2. **Threat Intelligence Signal:**
   - Pattern data from validation
   - Score and grade
   - System metadata

**Impact:**
- 1 event in PostHog dashboard
- 1 signal to threat intel API
- Can be filtered out later if needed (using UUID or timestamp)

---

### Option C: Test with Dedicated Test Config

Create a separate config for testing:

```bash
# Backup current config
mv ~/.deepsweep/config.json ~/.deepsweep/config.json.backup

# Run test (creates new config with new UUID)
deepsweep validate /tmp/test-project

# Check the new UUID
cat ~/.deepsweep/config.json

# Restore original config
mv ~/.deepsweep/config.json.backup ~/.deepsweep/config.json
```

**Advantage:**
- Test events have different UUID
- Easy to filter out in analytics
- Doesn't mix with real user data

---

## Phase 3: Verify Production Endpoints

### Check PostHog Dashboard

1. Go to: https://us.i.posthog.com/project/265866/events

2. Look for recent events:
   - Event name: `deepsweep_validate`
   - Check timestamp matches your test
   - Verify properties are populated

3. Verify event properties include:
   ```json
   {
     "command": "validate",
     "version": "0.1.0",
     "os": "Darwin/Linux/Windows",
     "duration_ms": <number>,
     "findings_count": <number>,
     "score": <number>,
     "grade": "A/B/C/D/F"
   }
   ```

### Check Threat Intelligence API

Monitor your backend logs at `api.deepsweep.ai` for:

1. **POST request to `/v1/signal`**

2. **Expected payload structure:**
   ```json
   {
     "event": "threat_signal",
     "version": "1",
     "pattern_ids": [...],
     "cve_matches": [...],
     "severity_counts": {...},
     "score": <number>,
     "grade": "A/B/C/D/F",
     "finding_count": <number>,
     ...
   }
   ```

3. **Expected response:** `200 OK`

---

## Phase 4: Monitor for Errors

### Check for API errors

Watch for any error responses:

```bash
# Run with verbose logging (if available)
deepsweep validate ./project --verbose

# Check for error messages
# Should NOT see network errors or API failures
```

### Check PostHog event delivery

Events are batched and sent asynchronously. Check that:
- Events appear in dashboard within 1-2 minutes
- No error events (`deepsweep_error`) related to telemetry

---

## What to Look For

### ✅ Success Indicators

**PostHog:**
- Events appear in dashboard
- Properties correctly populated
- No error events
- Timestamps match execution time

**Threat Intel API:**
- 200 OK responses
- Payloads correctly structured
- No authentication errors
- All required fields present

**CLI:**
- No telemetry-related error messages
- Normal execution speed (telemetry is async)
- Commands complete successfully

### ❌ Failure Indicators

**PostHog:**
- Events not appearing (check API key)
- 401/403 errors (authentication issue)
- Missing properties (code bug)
- Error events being generated

**Threat Intel API:**
- 4xx/5xx responses
- Timeout errors
- Malformed payload errors
- Missing required fields

**CLI:**
- Telemetry errors printed to console
- Slow execution (blocking issue)
- Crashes related to telemetry

---

## Rollback Plan

If you need to disable telemetry quickly:

### Option 1: User-Level Disable

```bash
# Disable optional telemetry (PostHog only)
deepsweep telemetry disable
```

This keeps threat intelligence active (Tier 1) but disables PostHog (Tier 2).

### Option 2: Full Offline Mode

```bash
# Disable ALL telemetry
export DEEPSWEEP_OFFLINE=1

# Or add to ~/.bashrc or ~/.zshrc for persistence
echo 'export DEEPSWEEP_OFFLINE=1' >> ~/.bashrc
```

### Option 3: Code-Level Disable (Emergency)

If needed, you can disable telemetry in the code:

```python
# In src/deepsweep/telemetry.py

# Change line 224:
def enabled(self) -> bool:
    """Check if optional telemetry (PostHog) is enabled."""
    return False  # <-- Always return False

# And/or line 229:
def offline_mode(self) -> bool:
    """Check if fully offline (disables ALL telemetry)."""
    return True  # <-- Always return True
```

---

## Monitoring in Production

### Key Metrics to Watch

**PostHog Dashboard:**
- DAU (Daily Active Users)
- Event counts by command type
- Error rates
- Grade distribution
- Failure reasons

**Threat Intel API:**
- Request rate
- Success/failure ratio
- Payload sizes
- Response times

### Set Up Alerts

Consider alerting on:
- Spike in error events
- API failure rate > 5%
- Missing required fields in payloads
- Unusual traffic patterns

---

## Filtering Test Data

If you run controlled tests and want to filter them out:

**In PostHog:**
1. Go to Filters
2. Add filter: `distinct_id != <your-test-uuid>`
3. Save as default filter

**In Backend:**
- Filter by `install_id` or `session_id`
- Filter by timestamp (during test window)
- Filter by specific test patterns you used

---

## FAQ

### Q: Will telemetry slow down the CLI?
**A:** No. All telemetry is async/fire-and-forget with a 2-second timeout.

### Q: What if PostHog is down?
**A:** CLI continues normally. Errors are suppressed silently.

### Q: What if my threat intel API is down?
**A:** CLI continues normally. Errors are suppressed silently.

### Q: Can users opt out?
**A:** Yes:
- `deepsweep telemetry disable` - Disables PostHog (Tier 2)
- `DEEPSWEEP_OFFLINE=1` - Disables everything (both tiers)

### Q: Is PII being collected?
**A:** No. Privacy guarantees enforced:
- No code, file paths, or repo names
- No personal information
- Anonymous UUID only
- Error messages sanitized

### Q: How do I verify privacy?
**A:** Run the local verification test:
```bash
python test_local_verification.py
```
Check "TEST 4: Privacy Guarantees" section.

---

## Recommended Testing Sequence

For your first production test:

1. **Backup config:**
   ```bash
   cp ~/.deepsweep/config.json ~/.deepsweep/config.json.backup
   ```

2. **Run offline test first:**
   ```bash
   export DEEPSWEEP_OFFLINE=1
   deepsweep validate ./test-project
   unset DEEPSWEEP_OFFLINE
   ```

3. **Run ONE controlled test:**
   ```bash
   mkdir -p /tmp/test-deepsweep
   echo "print('test')" > /tmp/test-deepsweep/test.py
   deepsweep validate /tmp/test-deepsweep
   ```

4. **Verify in PostHog dashboard**
   - Check for event in last 5 minutes
   - Verify properties look correct

5. **Verify threat intel API**
   - Check backend logs for POST to /v1/signal
   - Verify 200 OK response

6. **Monitor for errors**
   - Run a few more validations
   - Watch for any error patterns

7. **If all good, restore and proceed:**
   ```bash
   mv ~/.deepsweep/config.json.backup ~/.deepsweep/config.json
   ```

---

## Support

If you encounter issues:

1. Check local verification first: `python test_local_verification.py`
2. Review error messages carefully
3. Check PostHog dashboard for error events
4. Review backend API logs
5. Verify API keys are correct
6. Test with offline mode to isolate issues

**Remember:** All telemetry is non-blocking and gracefully handles failures.
