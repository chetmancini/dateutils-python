# Colors for terminal output
GREEN := \033[0;32m
BLUE := \033[0;34m
NC := \033[0m # No Color

# Default target
help:
	@echo "${BLUE}DateUtils Python - Development Commands${NC}"
	@echo ""
	@echo "${GREEN}Available commands:${NC}"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  ${BLUE}make %-10s${NC} %s\n", $$1, $$2}'

init: ## Install uv package manager if not present
	@command -v uv >/dev/null 2>&1 || { echo "Installing uv..."; curl -LsSf https://astral.sh/uv/install.sh | sh; }

deps: ## Install development dependencies
	@uv sync --group dev

test: ## Run tests
	@uv run pytest

coverage: ## Run tests with coverage report
	@uv run pytest --cov=dateutils

lint: ## Run linting checks
	@uv run ruff check .

format: ## Format code using ruff
	@uv run ruff format .

typecheck: ## Run static type checking with mypy
	@uv run mypy dateutils tests

build: ## Build the package for distribution
	@uv pip install --upgrade build
	@uv run python -m build

clean: ## Remove build artifacts and cache files
	@rm -rf build/
	@rm -rf dist/
	@rm -rf *.egg-info/
	@find . -type d -name __pycache__ -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete

.PHONY: init dev test coverage lint format typecheck build clean help
