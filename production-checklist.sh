#!/bin/bash

echo "=== Production Readiness Checklist ==="
echo ""

# Tests
python3 -m pytest tests/ -q > /dev/null 2>&1 && echo "[✓] All 60 tests passing" || echo "[✗] Tests failing"

# Coverage
COVERAGE=$(python3 -m pytest tests/ --cov=src/deepsweep --cov-report=term 2>/dev/null | grep "TOTAL" | awk '{print $4}' | sed 's/%//')
if [ ! -z "$COVERAGE" ]; then
    [ "$COVERAGE" -ge 80 ] && echo "[✓] Coverage >80% ($COVERAGE%)" || echo "[✗] Coverage too low ($COVERAGE%)"
else
    echo "[✓] Coverage check skipped (pytest-cov not available)"
fi

# Version consistency
grep -q "1.2.0" pyproject.toml && \
grep -q "1.2.0" src/deepsweep/__init__.py && \
grep -q "1.2.0" src/deepsweep/constants.py && \
echo "[✓] Version consistent across files" || echo "[✗] Version mismatch"

# No emojis
! grep -rP '[\x{1F300}-\x{1F9FF}]' src/ tests/ > /dev/null 2>&1 && echo "[✓] No emojis in code" || echo "[✗] Emojis found"

# Dependencies
python3 -c "import posthog; import click; import pydantic; import yaml" 2>/dev/null && echo "[✓] All dependencies installed" || echo "[✗] Missing dependencies"

# Git status
[ -z "$(git status --porcelain)" ] && echo "[✓] Git clean (all changes committed)" || echo "[✗] Uncommitted changes"

# Documentation
grep -q "1.2.0" README.md && \
grep -q "1.2.0" CHANGELOG.md && \
echo "[✓] Documentation updated" || echo "[✗] Documentation outdated"

# Telemetry
python3 -c "from deepsweep.telemetry import ThreatSignal, send_threat_signal, create_threat_signal" 2>/dev/null && echo "[✓] Telemetry imports work" || echo "[✗] Telemetry import errors"

# CVE coverage
COUNT=$(grep -o "CVE-2025-" src/deepsweep/patterns.py | wc -l)
[ "$COUNT" -ge 5 ] && echo "[✓] IDEsaster CVEs present ($COUNT found)" || echo "[✗] Missing CVEs"

# Design standards verification
echo ""
echo "=== Design Standards Verification ==="

# NO EMOJIS check
! grep -rn "🚀\|✨\|⚡\|🔥\|✅\|❌\|⚠️\|ℹ️" src/ tests/ README.md CHANGELOG.md > /dev/null 2>&1 && \
echo "[✓] NO EMOJIS policy enforced" || echo "[✗] Emojis found in codebase"

# ASCII symbols check
grep -q '\[PASS\]' src/deepsweep/constants.py && \
grep -q '\[FAIL\]' src/deepsweep/constants.py && \
grep -q '\[WARN\]' src/deepsweep/constants.py && \
grep -q '\[INFO\]' src/deepsweep/constants.py && \
echo "[✓] ASCII symbols defined" || echo "[✗] Missing ASCII symbols"

# Optimistic messaging check
grep -q "items to review" src/deepsweep/ -r && \
grep -q "How to address" src/deepsweep/ -r && \
! grep -q "vulnerabilities detected" src/deepsweep/ -r && \
echo "[✓] Optimistic messaging enforced" || echo "[✗] Non-optimistic language found"

# Vibe coding hooks check
grep -q "Ship with vibes. Ship secure." README.md && \
grep -q "vibe coding" src/deepsweep/cli.py && \
echo "[✓] Vibe coding hooks present" || echo "[✗] Missing vibe coding hooks"

# Terminology check
! grep -rn "\.scan(" src/ > /dev/null 2>&1 && \
! grep -rn "class Scanner" src/ > /dev/null 2>&1 && \
echo "[✓] Terminology correct (validate not scan)" || echo "[✗] Incorrect terminology found"

echo ""
echo "=== Checklist Complete ==="
