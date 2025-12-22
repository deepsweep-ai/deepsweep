#!/bin/bash
set -e

echo "============================================================"
echo "DeepSweep v1.2.0 Quality Verification"
echo "Elite OSS Standards Compliance Check"
echo "============================================================"
echo ""

FAILED=0

# Color output (respects NO_COLOR)
if [ -z "$NO_COLOR" ]; then
    GREEN='\033[0;32m'
    RED='\033[0;31m'
    YELLOW='\033[1;33m'
    NC='\033[0m'
else
    GREEN=''
    RED=''
    YELLOW=''
    NC=''
fi

run_check() {
    local name="$1"
    local command="$2"

    echo -e "${YELLOW}[RUN]${NC} $name"
    if eval "$command" > /tmp/check_output 2>&1; then
        echo -e "${GREEN}[PASS]${NC} $name"
        return 0
    else
        echo -e "${RED}[FAIL]${NC} $name"
        cat /tmp/check_output
        FAILED=$((FAILED + 1))
        return 1
    fi
}

# 1. Unit tests
echo "=== Unit Tests ==="
run_check "All unit tests" "python -m pytest tests/ -q --tb=short"
echo ""

# 2. Code coverage
echo "=== Code Coverage ==="
run_check "Coverage >80%" "python -m pytest tests/ --cov=src/deepsweep --cov-report=term --cov-fail-under=80 -q"
echo ""

# 3. Linting
echo "=== Code Quality ==="
run_check "Ruff linting" "ruff check . --quiet"
run_check "Ruff formatting" "ruff format --check . --quiet"
echo ""

# 4. Type checking
echo "=== Type Safety ==="
run_check "MyPy type checking" "mypy src/deepsweep --no-error-summary"
echo ""

# 5. Design standards
echo "=== Design Standards ==="
run_check "NO EMOJIS policy" "! grep -rP '[\\x{1F300}-\\x{1F9FF}]' src/ tests/ README.md CHANGELOG.md 2>/dev/null"
run_check "ASCII symbols defined" "grep -q '\\[PASS\\]' src/deepsweep/constants.py && grep -q '\\[FAIL\\]' src/deepsweep/constants.py"
run_check "Optimistic messaging" "grep -q 'items to review' src/deepsweep/output.py && ! grep -q 'vulnerabilities detected' src/deepsweep/output.py"
run_check "Correct terminology" "! grep -rn '\\.scan(' src/ && ! grep -rn 'class Scanner' src/"
echo ""

# 6. Documentation
echo "=== Documentation ==="
run_check "Version consistency" "grep -q '1.2.0' pyproject.toml && grep -q '1.2.0' src/deepsweep/__init__.py && grep -q '1.2.0' README.md"
run_check "README completeness" "grep -q 'Quick Start' README.md && grep -q 'Installation' README.md && grep -q 'Privacy & Telemetry' README.md"
run_check "SECURITY.md exists" "test -f SECURITY.md && grep -q 'Reporting Vulnerabilities' SECURITY.md"
run_check "CONTRIBUTING.md exists" "test -f CONTRIBUTING.md && grep -q 'NO EMOJIS' CONTRIBUTING.md"
echo ""

# 7. Build configuration
echo "=== Build Configuration ==="
run_check "py.typed marker" "test -f src/deepsweep/py.typed"
run_check "pyproject.toml valid" "python -c 'import tomllib; tomllib.load(open(\"pyproject.toml\", \"rb\"))' 2>/dev/null || python -c 'import tomli; tomli.load(open(\"pyproject.toml\", \"rb\"))'"
echo ""

# 8. Dependencies
echo "=== Dependencies ==="
run_check "Dependencies installed" "python -c 'import click; import rich; import yaml; import pydantic; import posthog'"
echo ""

# 9. Self-validation
echo "=== Self-Validation ==="
run_check "DeepSweep self-check" "python -m deepsweep validate . --format text > /dev/null"
echo ""

# 10. Integration tests
echo "=== Integration Tests ==="
if [ -f "test-integration.sh" ]; then
    run_check "Integration tests" "bash test-integration.sh"
else
    echo -e "${YELLOW}[SKIP]${NC} Integration tests (test-integration.sh not found)"
fi
echo ""

# Summary
echo "============================================================"
echo "QUALITY CHECK SUMMARY"
echo "============================================================"
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}[PASS]${NC} All checks passed - SHIP READY"
    echo ""
    echo "Elite OSS standards met:"
    echo "  - NO EMOJIS policy enforced"
    echo "  - Code coverage >80%"
    echo "  - Type safety verified"
    echo "  - Design standards compliant"
    echo "  - Documentation complete"
    echo "  - Self-validation passed"
    echo ""
    echo "Ready for production release."
    exit 0
else
    echo -e "${RED}[FAIL]${NC} $FAILED check(s) failed"
    echo ""
    echo "Please address the failures above before release."
    exit 1
fi
