# Contributing to DeepSweep

Thank you for your interest in contributing to DeepSweep!

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/deepsweep-ai/deepsweep.git
   cd deepsweep
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   ```

3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

4. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/deepsweep --cov-report=html

# Run specific test file
pytest tests/test_validator.py
```

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

All contributions must follow these standards:

- NO EMOJIS anywhere (code, docs, CLI, tests)
- Use ASCII symbols: [PASS] [FAIL] [WARN] [INFO]
- Optimistic messaging (see README)
- Type hints on all public functions
- Docstrings on all public functions

## Questions?

Open an issue or discussion on GitHub.
