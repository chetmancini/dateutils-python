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
	@echo ""
	@echo "${YELLOW}Release Process:${NC}"
	@echo "  1. Bump version with 'make version-patch/minor/major' (auto-pushes tag)"
	@echo "  2. Create release from GitHub UI for the pushed tag"
	@echo "  3. GitHub Actions will automatically build, test, and publish to PyPI"

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

# Versioning
update-changelog: ## Update CHANGELOG.md with new version info
	@if [ -z "$(VERSION)" ]; then echo "${RED}Error: VERSION parameter required. Usage: make update-changelog VERSION=x.y.z${NC}"; exit 1; fi
	@echo "${BLUE}Updating CHANGELOG.md for version $(VERSION)...${NC}"
	@uv run python scripts/update_changelog.py $(VERSION)
	@echo "${GREEN}✓ CHANGELOG.md updated${NC}"

version-patch: ## Bump patch version and push tag (e.g., 1.0.0 → 1.0.1)
	@echo "${BLUE}Bumping patch version...${NC}"
	@OLD_VERSION=$$(grep '^current_version' .bumpversion.cfg | cut -d' ' -f3); \
	uv run bump2version --allow-dirty patch; \
	NEW_VERSION=$$(grep '^current_version' .bumpversion.cfg | cut -d' ' -f3); \
	$(MAKE) --no-print-directory update-changelog VERSION=$$NEW_VERSION; \
	uv lock; \
	echo "${BLUE}Staging all changes...${NC}"; \
	git add -A; \
	git commit --no-verify -m "Bump version: $$OLD_VERSION → $$NEW_VERSION"; \
	git tag "v$$NEW_VERSION"; \
	echo "${BLUE}Pushing tag to GitHub...${NC}"; \
	git push origin HEAD --follow-tags
	@echo "${GREEN}✓ Patch version bumped and pushed${NC}"
	@NEW_VERSION=$$(grep '^current_version' .bumpversion.cfg | cut -d' ' -f3); \
	echo "${YELLOW}Next steps:${NC}"; \
	echo "  - Go to GitHub and create a release for tag v$$NEW_VERSION"; \
	echo "  - GitHub Actions will automatically build and publish to PyPI"

version-minor: ## Bump minor version and push tag (e.g., 1.0.0 → 1.1.0)
	@echo "${BLUE}Bumping minor version...${NC}"
	@OLD_VERSION=$$(grep '^current_version' .bumpversion.cfg | cut -d' ' -f3); \
	uv run bump2version --allow-dirty minor; \
	NEW_VERSION=$$(grep '^current_version' .bumpversion.cfg | cut -d' ' -f3); \
	$(MAKE) --no-print-directory update-changelog VERSION=$$NEW_VERSION; \
	uv lock; \
	echo "${BLUE}Staging all changes...${NC}"; \
	git add -A; \
	git commit --no-verify -m "Bump version: $$OLD_VERSION → $$NEW_VERSION"; \
	git tag "v$$NEW_VERSION"; \
	echo "${BLUE}Pushing tag to GitHub...${NC}"; \
	git push origin HEAD --follow-tags
	@echo "${GREEN}✓ Minor version bumped and pushed${NC}"
	@NEW_VERSION=$$(grep '^current_version' .bumpversion.cfg | cut -d' ' -f3); \
	echo "${YELLOW}Next steps:${NC}"; \
	echo "  - Go to GitHub and create a release for tag v$$NEW_VERSION"; \
	echo "  - GitHub Actions will automatically build and publish to PyPI"

version-major: ## Bump major version and push tag (e.g., 1.0.0 → 2.0.0)
	@echo "${BLUE}Bumping major version...${NC}"
	@OLD_VERSION=$$(grep '^current_version' .bumpversion.cfg | cut -d' ' -f3); \
	uv run bump2version --allow-dirty major; \
	NEW_VERSION=$$(grep '^current_version' .bumpversion.cfg | cut -d' ' -f3); \
	$(MAKE) --no-print-directory update-changelog VERSION=$$NEW_VERSION; \
	uv lock; \
	echo "${BLUE}Staging all changes...${NC}"; \
	git add -A; \
	git commit --no-verify -m "Bump version: $$OLD_VERSION → $$NEW_VERSION"; \
	git tag "v$$NEW_VERSION"; \
	echo "${BLUE}Pushing tag to GitHub...${NC}"; \
	git push origin HEAD --follow-tags
	@echo "${GREEN}✓ Major version bumped and pushed${NC}"
	@NEW_VERSION=$$(grep '^current_version' .bumpversion.cfg | cut -d' ' -f3); \
	echo "${YELLOW}Next steps:${NC}"; \
	echo "  - Go to GitHub and create a release for tag v$$NEW_VERSION"; \
	echo "  - GitHub Actions will automatically build and publish to PyPI"

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
.PHONY: init deps install pre-commit pre-commit-run lint lint-fix format format-check typecheck test test-fast coverage coverage-html watch-test check dev fix build build-check update-changelog version-patch version-minor version-major clean requirements version help
