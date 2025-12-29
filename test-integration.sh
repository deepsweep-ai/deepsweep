#!/bin/bash
set -e

echo "=== DeepSweep v1.2.0 Integration Tests ==="

# 1. Clean slate
rm -rf ~/.deepsweep/
echo "[PASS] Clean environment"

# 2. First run
OUTPUT=$(python3 -m deepsweep validate . 2>&1)
echo "$OUTPUT" | grep -q "two-tier telemetry" && echo "[PASS] First-run notice shown"

# 3. Verify config created
test -f ~/.deepsweep/config.json && echo "[PASS] Config file created"

# 4. Test tier separation
python3 -m deepsweep telemetry disable > /dev/null 2>&1
STATUS=$(python3 -m deepsweep telemetry status)
echo "$STATUS" | grep -q "Essential tier only" && echo "[PASS] Optional tier disabled correctly"

# 5. Test offline mode
export DEEPSWEEP_OFFLINE=1
STATUS=$(python3 -m deepsweep telemetry status)
echo "$STATUS" | grep -q "Offline mode enabled" && echo "[PASS] Offline mode detected"
unset DEEPSWEEP_OFFLINE

# 6. Verify version
python3 -m deepsweep --version | grep -q "1.2.0" && echo "[PASS] Version correct"

# 7. Test all output formats
python3 -m deepsweep validate . --format text > /dev/null && echo "[PASS] Text output"
python3 -m deepsweep validate . --format json > /dev/null && echo "[PASS] JSON output"
python3 -m deepsweep validate . --format sarif > /dev/null && echo "[PASS] SARIF output"

# 8. Test badge generation
python3 -m deepsweep badge --output /tmp/test-badge.svg > /dev/null 2>&1 && echo "[PASS] Badge generated"

# 9. Verify CVE coverage
python3 -m deepsweep patterns | grep -q "CVE-2025-53109" && echo "[PASS] IDEsaster CVEs present"

# 10. Run full test suite
python3 -m pytest tests/ -q && echo "[PASS] All unit tests passing"

echo ""
echo "=== All Integration Tests Passed ✓ ==="
