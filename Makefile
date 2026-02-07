.PHONY: help install dev-install test test-cov lint format type-check clean build publish all

help:
	@echo "pytest-mcp development commands"
	@echo ""
	@echo "Setup:"
	@echo "  install       Install package"
	@echo "  dev-install   Install with development dependencies"
	@echo ""
	@echo "Development:"
	@echo "  test          Run tests"
	@echo "  test-cov      Run tests with coverage"
	@echo "  lint          Lint code"
	@echo "  format        Format code"
	@echo "  type-check    Type check code"
	@echo "  all           Run all checks"
	@echo ""
	@echo "Build:"
	@echo "  clean         Clean build artifacts"
	@echo "  build         Build distribution"
	@echo "  publish       Publish to PyPI"
	@echo ""

install:
	pip install -e .

dev-install:
	pip install -e ".[dev]"

test:
	pytest -v

test-cov:
	pytest --cov=pytest_mcp --cov-report=html --cov-report=term
	@echo "Coverage report: htmlcov/index.html"

lint:
	ruff check src/ tests/ examples/

format:
	black src/ tests/ examples/

type-check:
	mypy src/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

publish: build
	twine upload dist/*

all: format lint type-check test
	@echo ""
	@echo "All checks passed."
