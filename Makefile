.PHONY: install dev test lint format clean build publish

# Install production dependencies
install:
	pip install -e .

# Install development dependencies
dev:
	pip install -e ".[dev]"
	pre-commit install

# Run tests
test:
	pytest -v

# Run tests with coverage
coverage:
	pytest --cov=src/deepsweep --cov-report=html --cov-report=term

# Lint code
lint:
	ruff check .
	mypy src/deepsweep

# Format code
format:
	ruff format .
	ruff check . --fix

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +

# Build package
build: clean
	python -m build

# Publish to PyPI
publish: build
	twine upload dist/*

# Run the CLI
run:
	python -m deepsweep validate .
