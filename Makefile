# Colors for terminal output
GREEN := \033[0;32m
BLUE := \033[0;34m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

# Project configuration
PYTHON_VERSION := $(shell python --version 2>/dev/null || echo "Python not found")
UV_VERSION := $(shell uv --version 2>/dev/null || echo "uv not found")

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "${BLUE}DateUtils Python - Development Commands${NC}"
	@echo ""
	@echo "${GREEN}Available commands:${NC}"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  ${BLUE}make %-15s${NC} %s\n", $$1, $$2}'
	@echo ""
	@echo "${YELLOW}Environment Info:${NC}"
	@echo "  ${PYTHON_VERSION}"
	@echo "  ${UV_VERSION}"

# Setup and Installation
init: ## Install uv package manager if not present
	@command -v uv >/dev/null 2>&1 || { echo "${YELLOW}Installing uv...${NC}"; curl -LsSf https://astral.sh/uv/install.sh | sh; }
	@echo "${GREEN}✓ uv package manager ready${NC}"

deps: init ## Install development dependencies
	@echo "${BLUE}Installing dependencies...${NC}"
	@uv sync --group dev
	@echo "${GREEN}✓ Dependencies installed${NC}"

install: deps ## Install the package in development mode
	@echo "${BLUE}Installing package in development mode...${NC}"
	@uv pip install -e .
	@echo "${GREEN}✓ Package installed${NC}"

pre-commit: ## Install pre-commit hooks
	@echo "${BLUE}Installing pre-commit hooks...${NC}"
	@uv run pre-commit install
	@echo "${GREEN}✓ Pre-commit hooks installed${NC}"

pre-commit-run: ## Run all pre-commit hooks manually
	@echo "${BLUE}Running all pre-commit hooks...${NC}"
	@uv run pre-commit run --all-files
	@echo "${GREEN}✓ Pre-commit hooks completed${NC}"

# Code Quality
lint: ## Run linting checks
	@echo "${BLUE}Running linting checks...${NC}"
	@uv run ruff check .

lint-fix: ## Run linting checks and fix errors
	@echo "${BLUE}Running linting fixes...${NC}"
	@uv run ruff check --fix .
	@echo "${GREEN}✓ Linting fixes applied${NC}"

format: ## Format code using ruff
	@echo "${BLUE}Formatting code...${NC}"
	@uv run ruff format .
	@echo "${GREEN}✓ Code formatted${NC}"

format-check: ## Check if code is properly formatted
	@echo "${BLUE}Checking code formatting...${NC}"
	@uv run ruff format --check .

typecheck: ## Run static type checking with mypy
	@echo "${BLUE}Running type checks...${NC}"
	@uv run mypy dateutils tests

# Testing
test: ## Run tests
	@echo "${BLUE}Running tests...${NC}"
	@uv run pytest

test-fast: ## Run tests without coverage
	@echo "${BLUE}Running fast tests...${NC}"
	@uv run pytest --no-cov

coverage: ## Run tests with coverage report
	@echo "${BLUE}Running tests with coverage...${NC}"
	@uv run pytest --cov=dateutils
	@echo "${GREEN}✓ Coverage report generated${NC}"

coverage-html: ## Generate HTML coverage report
	@echo "${BLUE}Generating HTML coverage report...${NC}"
	@uv run pytest --cov=dateutils --cov-report=html
	@echo "${GREEN}✓ HTML coverage report generated in htmlcov/${NC}"

watch-test: ## Run tests in watch mode (requires entr)
	@command -v entr >/dev/null 2>&1 || { echo "${RED}Error: entr not found. Install with: brew install entr${NC}"; exit 1; }
	@echo "${BLUE}Watching for changes and running tests...${NC}"
	@find . -name "*.py" | entr -c uv run pytest

# Comprehensive Checks
check: ## Run all checks (lint, format-check, typecheck, test)
	@echo "${BLUE}Running comprehensive checks...${NC}"
	@$(MAKE) --no-print-directory lint
	@$(MAKE) --no-print-directory format-check
	@$(MAKE) --no-print-directory typecheck
	@$(MAKE) --no-print-directory test
	@echo "${GREEN}✓ All checks passed${NC}"


# Development Workflow
dev: deps ## Set up complete development environment
	@echo "${BLUE}Setting up development environment...${NC}"
	@$(MAKE) --no-print-directory install
	@$(MAKE) --no-print-directory pre-commit
	@echo "${GREEN}✓ Development environment ready${NC}"
	@echo "${YELLOW}Next steps:${NC}"
	@echo "  - Run 'make test' to verify setup"
	@echo "  - Pre-commit hooks will run automatically on commits"
	@echo "  - Run 'make check' before committing for manual verification"

fix: ## Fix common issues (format + lint-fix)
	@echo "${BLUE}Fixing common issues...${NC}"
	@$(MAKE) --no-print-directory format
	@$(MAKE) --no-print-directory lint-fix
	@echo "${GREEN}✓ Common issues fixed${NC}"

# Build and Distribution
build: ## Build the package for distribution
	@echo "${BLUE}Building package...${NC}"
	@uv run python -m build
	@echo "${GREEN}✓ Package built in dist/${NC}"

build-check: build ## Build and check the package
	@echo "${BLUE}Checking built package...${NC}"
	@uv run python -m twine check dist/*
	@echo "${GREEN}✓ Package check completed${NC}"

# Versioning and Release
version-patch: ## Bump patch version (e.g., 1.0.0 → 1.0.1)
	@echo "${BLUE}Bumping patch version...${NC}"
	@uv run bump2version patch
	@echo "${GREEN}✓ Patch version bumped${NC}"

version-minor: ## Bump minor version (e.g., 1.0.0 → 1.1.0)
	@echo "${BLUE}Bumping minor version...${NC}"
	@uv run bump2version minor
	@echo "${GREEN}✓ Minor version bumped${NC}"

version-major: ## Bump major version (e.g., 1.0.0 → 2.0.0)
	@echo "${BLUE}Bumping major version...${NC}"
	@uv run bump2version major
	@echo "${GREEN}✓ Major version bumped${NC}"

release-check: ## Check if ready for release (run all quality checks)
	@echo "${BLUE}Checking release readiness...${NC}"
	@$(MAKE) --no-print-directory clean
	@$(MAKE) --no-print-directory check
	@$(MAKE) --no-print-directory build-check
	@echo "${GREEN}✓ Ready for release${NC}"

release-patch: ## Create patch release (bump version, tag, and push)
	@echo "${BLUE}Creating patch release...${NC}"
	@$(MAKE) --no-print-directory release-check
	@$(MAKE) --no-print-directory version-patch
	@git push origin HEAD --follow-tags
	@echo "${GREEN}✓ Patch release created and pushed${NC}"

release-minor: ## Create minor release (bump version, tag, and push)
	@echo "${BLUE}Creating minor release...${NC}"
	@$(MAKE) --no-print-directory release-check
	@$(MAKE) --no-print-directory version-minor
	@git push origin HEAD --follow-tags
	@echo "${GREEN}✓ Minor release created and pushed${NC}"

release-major: ## Create major release (bump version, tag, and push)
	@echo "${BLUE}Creating major release...${NC}"
	@$(MAKE) --no-print-directory release-check
	@$(MAKE) --no-print-directory version-major
	@git push origin HEAD --follow-tags
	@echo "${GREEN}✓ Major release created and pushed${NC}"

publish-test: build-check ## Publish to TestPyPI
	@echo "${BLUE}Publishing to TestPyPI...${NC}"
	@uv publish --repository testpypi dist/*

publish: build-check ## Publish to PyPI (production)
	@echo "${RED}Publishing to PyPI (production)...${NC}"
	@read -p "Are you sure you want to publish to PyPI? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		uv publish dist/*; \
		echo "${GREEN}✓ Published to PyPI${NC}"; \
	else \
		echo "${YELLOW}Publication cancelled${NC}"; \
	fi

# Utilities
clean: ## Remove build artifacts and cache files
	@echo "${BLUE}Cleaning build artifacts...${NC}"
	@rm -rf build/
	@rm -rf dist/
	@rm -rf *.egg-info/
	@rm -rf htmlcov/
	@rm -rf .coverage
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "${GREEN}✓ Cleaned build artifacts${NC}"

requirements: ## Export current dependencies to requirements.txt
	@echo "${BLUE}Exporting dependencies...${NC}"
	@uv export --format requirements-txt --output-file requirements.txt
	@echo "${GREEN}✓ Dependencies exported to requirements.txt${NC}"

version: ## Show current version information
	@echo "${BLUE}Version Information:${NC}"
	@echo "Package version: $(shell grep '^version = ' pyproject.toml | cut -d'"' -f2)"
	@echo "Python version: $(PYTHON_VERSION)"
	@echo "UV version: $(UV_VERSION)"

# Safety check for dangerous operations
.PHONY: init deps install pre-commit pre-commit-run lint lint-fix format format-check typecheck test test-fast coverage coverage-html watch-test check dev fix build build-check version-patch version-minor version-major release-check release-patch release-minor release-major publish-test publish clean requirements version help
