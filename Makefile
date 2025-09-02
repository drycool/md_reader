# Makefile for md_reader development

.PHONY: help install install-dev test test-unit test-integration test-performance
.PHONY: test-security test-slow coverage lint format type-check security-check
.PHONY: pre-commit-install pre-commit-run clean build docs

# Default target
help:
	@echo "Available targets:"
	@echo "  install          Install the package"
	@echo "  install-dev      Install with development dependencies"
	@echo "  test             Run all tests"
	@echo "  test-unit        Run unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  test-performance Run performance tests"
	@echo "  test-security    Run security tests"
	@echo "  test-slow        Run slow tests"
	@echo "  coverage         Run tests with coverage report"
	@echo "  lint             Run linting (flake8)"
	@echo "  format           Format code (black + isort)"
	@echo "  type-check       Run type checking (mypy)"
	@echo "  security-check   Run security checks (bandit)"
	@echo "  pre-commit-install Install pre-commit hooks"
	@echo "  pre-commit-run   Run pre-commit on all files"
	@echo "  clean            Clean build artifacts"
	@echo "  build            Build package"
	@echo "  docs             Generate documentation"

# Installation
install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

# Testing
test:
	pytest

test-unit:
	pytest -m unit

test-integration:
	pytest -m integration

test-performance:
	pytest -m performance

test-security:
	pytest -m security

test-slow:
	pytest -m slow

coverage:
	pytest --cov=md_reader --cov-report=html --cov-report=term

# Code quality
lint:
	flake8 md_reader tests

format:
	black md_reader tests
	isort md_reader tests

type-check:
	mypy md_reader

security-check:
	bandit -r md_reader -f json -o bandit-report.json
	bandit -r md_reader

# Pre-commit
pre-commit-install:
	pre-commit install

pre-commit-run:
	pre-commit run --all-files

# Quality gate (run all checks)
quality-check: lint type-check security-check test

# Build and cleanup
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -f coverage.xml
	rm -f bandit-report.json
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +

build: clean
	python -m build

# Development workflow
dev-setup: install-dev pre-commit-install
	@echo "Development environment setup complete!"

dev-check: format lint type-check security-check test
	@echo "All development checks passed!"

# CI simulation
ci: lint type-check security-check coverage
	@echo "CI checks completed!"

# Documentation (placeholder for future implementation)
docs:
	@echo "Documentation generation not yet implemented"

# Performance benchmarking
benchmark:
	pytest -m performance --benchmark-only --benchmark-sort=mean

# Test specific modules
test-validators:
	pytest tests/test_validators.py -v

test-cache:
	pytest tests/test_cache.py -v

test-security-improvements:
	pytest test_security_improvements.py -v

# Profile performance
profile:
	python -m cProfile -o profile_output.prof -m pytest tests/test_cache.py::TestCachePerformance
	@echo "Profile saved to profile_output.prof"

# Check for outdated dependencies
deps-check:
	pip list --outdated

# Generate requirements.txt from current environment
freeze:
	pip freeze > requirements-frozen.txt