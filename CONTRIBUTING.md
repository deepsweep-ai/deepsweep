# Contributing to DeepSweep

Thank you for your interest in contributing to DeepSweep!

We welcome contributions of all kinds: bug reports, feature requests, documentation improvements, and code contributions.

---

## Development Setup

### Prerequisites

- Python 3.10 or higher
- Git
- Basic understanding of AI coding assistants and security

### Initial Setup

1. **Fork and clone:**
   ```bash
   git clone https://github.com/YOUR-USERNAME/deepsweep.git
   cd deepsweep
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # or
   venv\Scripts\activate  # Windows
   ```

3. **Install development dependencies:**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Install pre-commit hooks:**
   ```bash
   pre-commit install
   ```

5. **Verify setup:**
   ```bash
   pytest
   deepsweep validate .
   ```

---

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/deepsweep --cov-report=html

# Run specific test file
pytest tests/test_validator.py

# Run integration tests
bash test-integration.sh

# Test telemetry system
bash verify-telemetry.sh

# Test API endpoint
bash test-api-endpoint.sh

# Test PostHog integration
python test-posthog.py
```

For comprehensive testing documentation, see [docs/TESTING.md](docs/TESTING.md).

## Code Style

We use `ruff` for linting and formatting:

```bash
# Check
ruff check .

# Fix
ruff check . --fix

# Format
ruff format .
```

## Adding a Detection Pattern

1. Add the pattern to `src/deepsweep/patterns.py`
2. Add test cases to `tests/test_patterns.py`
3. Add test fixtures if needed
4. Update documentation

Pattern template:

```python
Pattern(
    id="CATEGORY-TYPE-NNN",
    name="Human Readable Name",
    severity=Severity.HIGH,
    description="What this pattern detects",
    regex=r"your regex here",
    file_types=(".cursorrules",),
    remediation="How to address this finding",
    cve="CVE-YYYY-NNNNN",  # If applicable
    owasp="ASI01",  # If applicable
)
```

## Pull Request Process

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Run tests: `pytest`
5. Run linting: `ruff check .`
6. Commit with clear message
7. Push and create Pull Request

## Design Standards

**MANDATORY - All contributions must follow these standards:**

### NO EMOJIS Policy

- **ZERO TOLERANCE**: No emojis anywhere in code, docs, CLI output, tests, or comments
- Use ASCII symbols only: `[PASS]` `[FAIL]` `[WARN]` `[INFO]` `*` `-` `>`
- This is a blocking requirement - PRs with emojis will not be merged

### Code Quality

- **Type hints** on all public functions and methods
- **Docstrings** on all public functions (Google style)
- **Test coverage** >80% for new code
- **Performance**: Validation must complete in <100ms for typical repos
- **No breaking changes** without major version bump

### Messaging Style

- **Optimistic tone**: "items to review" not "vulnerabilities detected"
- **Actionable guidance**: "How to address" not "Fix immediately"
- **Professional**: No hype, no marketing speak, no exaggeration
- See README for examples

### Terminology

- Use **"validate"** not "scan"
- Use **"findings"** or "items to review" not "vulnerabilities"
- Use **"How to address"** not "Fix" or "Remediation"

---

## Code Review Expectations

Your PR will be reviewed for:

1. **Correctness**: Does it work? Are there edge cases?
2. **Tests**: Are there tests? Do they cover edge cases?
3. **Performance**: Does it maintain <100ms validation time?
4. **Design standards**: NO EMOJIS, ASCII symbols, optimistic messaging
5. **Documentation**: Is it clear how to use the new feature?
6. **Backwards compatibility**: Does it break existing usage?

---

## Release Process

1. Version bump in `pyproject.toml`, `__init__.py`, `constants.py`
2. Update `CHANGELOG.md` with changes
3. Run full test suite: `pytest`
4. Run design verification: `./verify-design-standards.sh`
5. Tag release: `git tag v1.x.x`
6. Build and publish to PyPI (maintainers only)

---

## Performance Requirements

- Validation: <100ms for repos with <100 files
- Cold start: <500ms including pattern loading
- Memory: <50MB for typical usage
- Telemetry: Non-blocking, 2s timeout, fire-and-forget

---

## Questions?

- **Bug reports**: https://github.com/deepsweep-ai/deepsweep/issues
- **Feature requests**: https://github.com/deepsweep-ai/deepsweep/discussions
- **Security issues**: security@deepsweep.ai
- **General questions**: hello@deepsweep.ai

---

**Thank you for contributing to DeepSweep!**
