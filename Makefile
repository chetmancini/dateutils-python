# Default target
help:
	@echo "DateUtils Python - Development Commands"
	@echo ""
	@echo "Available commands:"
	@echo "  make init      - Install uv package manager if not present"
	@echo "  make deps      - Install development dependencies"
	@echo "  make test      - Run tests"
	@echo "  make coverage  - Run tests with coverage report"
	@echo "  make lint      - Run linting checks"
	@echo "  make format    - Format code using ruff"
	@echo "  make typecheck - Run static type checking with mypy"
	@echo "  make build     - Build the package for distribution"
	@echo "  make clean     - Remove build artifacts and cache files"
	@echo "  make help      - Show this help message"
	@echo ""

init:
	@command -v uv >/dev/null 2>&1 || { echo "Installing uv..."; curl -LsSf https://astral.sh/uv/install.sh | sh; }

deps:
	uv sync --group dev

# Run tests
test:
	uv run pytest

# Run tests with coverage
coverage:
	uv run pytest --cov=dateutils

# Run linting
lint:
	uv run ruff check .

# Format code
format:
	uv run ruff format .

# Run static type checking
typecheck:
	uv run mypy dateutils tests

# Build the package
build:
	uv pip install --upgrade build
	uv run python -m build

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

.PHONY: init dev test coverage lint format typecheck build clean help
