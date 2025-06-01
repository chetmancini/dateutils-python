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
update-changelog: ## Update CHANGELOG.md with new version info
	@if [ -z "$(VERSION)" ]; then echo "${RED}Error: VERSION parameter required. Usage: make update-changelog VERSION=x.y.z${NC}"; exit 1; fi
	@echo "${BLUE}Updating CHANGELOG.md for version $(VERSION)...${NC}"
	@uv run python scripts/update_changelog.py $(VERSION)
	@echo "${GREEN}✓ CHANGELOG.md updated${NC}"

version-patch: ## Bump patch version (e.g., 1.0.0 → 1.0.1)
	@echo "${BLUE}Bumping patch version...${NC}"
	@OLD_VERSION=$$(grep '^current_version' .bumpversion.cfg | cut -d' ' -f3); \
	uv run bump2version --allow-dirty patch; \
	NEW_VERSION=$$(grep '^current_version' .bumpversion.cfg | cut -d' ' -f3); \
	$(MAKE) --no-print-directory update-changelog VERSION=$$NEW_VERSION; \
	echo "${BLUE}Updating uv.lock file...${NC}"; \
	uv lock; \
	git add uv.lock; \
	git add .; \
	git commit --no-verify -m "Bump version: $$OLD_VERSION → $$NEW_VERSION"; \
	git tag "v$$NEW_VERSION"
	@echo "${GREEN}✓ Patch version bumped${NC}"
	@echo "${YELLOW}Next steps:${NC}"
	@echo "  - Review CHANGELOG.md and edit as needed"
	@echo "  - Run 'make release-draft' to create a draft release for review"
	@echo "  - Run 'make release' to publish the release"

version-minor: ## Bump minor version (e.g., 1.0.0 → 1.1.0)
	@echo "${BLUE}Bumping minor version...${NC}"
	@OLD_VERSION=$$(grep '^current_version' .bumpversion.cfg | cut -d' ' -f3); \
	uv run bump2version --allow-dirty minor; \
	NEW_VERSION=$$(grep '^current_version' .bumpversion.cfg | cut -d' ' -f3); \
	$(MAKE) --no-print-directory update-changelog VERSION=$$NEW_VERSION; \
	echo "${BLUE}Updating uv.lock file...${NC}"; \
	uv lock; \
	git add uv.lock; \
	git add .; \
	git commit --no-verify -m "Bump version: $$OLD_VERSION → $$NEW_VERSION"; \
	git tag "v$$NEW_VERSION"
	@echo "${GREEN}✓ Minor version bumped${NC}"
	@echo "${YELLOW}Next steps:${NC}"
	@echo "  - Review CHANGELOG.md and edit as needed"
	@echo "  - Run 'make release-draft' to create a draft release for review"
	@echo "  - Run 'make release' to publish the release"

version-major: ## Bump major version (e.g., 1.0.0 → 2.0.0)
	@echo "${BLUE}Bumping major version...${NC}"
	@OLD_VERSION=$$(grep '^current_version' .bumpversion.cfg | cut -d' ' -f3); \
	uv run bump2version --allow-dirty major; \
	NEW_VERSION=$$(grep '^current_version' .bumpversion.cfg | cut -d' ' -f3); \
	$(MAKE) --no-print-directory update-changelog VERSION=$$NEW_VERSION; \
	echo "${BLUE}Updating uv.lock file...${NC}"; \
	uv lock; \
	git add uv.lock; \
	git add .; \
	git commit --no-verify -m "Bump version: $$OLD_VERSION → $$NEW_VERSION"; \
	git tag "v$$NEW_VERSION"
	@echo "${GREEN}✓ Major version bumped${NC}"
	@echo "${YELLOW}Next steps:${NC}"
	@echo "  - Review CHANGELOG.md and edit as needed"
	@echo "  - Run 'make release-draft' to create a draft release for review"
	@echo "  - Run 'make release' to publish the release"

check-release-exists: ## Check if current version already has a GitHub release
	@command -v gh >/dev/null 2>&1 || { echo "${RED}Error: GitHub CLI (gh) not found. Install with: brew install gh${NC}"; exit 1; }
	@gh auth status >/dev/null 2>&1 || { echo "${RED}Error: GitHub CLI not authenticated. Run: gh auth login${NC}"; exit 1; }
	@CURRENT_VERSION=$$(grep '^current_version' .bumpversion.cfg | cut -d' ' -f3); \
	echo "${BLUE}Checking if v$$CURRENT_VERSION already exists on GitHub...${NC}"; \
	if gh release view "v$$CURRENT_VERSION" >/dev/null 2>&1; then \
		echo "${RED}Error: Release v$$CURRENT_VERSION already exists on GitHub${NC}"; \
		echo "${YELLOW}If you need to update it, delete the existing release first:${NC}"; \
		echo "  gh release delete v$$CURRENT_VERSION"; \
		exit 1; \
	else \
		echo "${GREEN}✓ Version v$$CURRENT_VERSION not yet released${NC}"; \
	fi

create-github-release: ## Create GitHub release with release notes
	@command -v gh >/dev/null 2>&1 || { echo "${RED}Error: GitHub CLI (gh) not found. Install with: brew install gh${NC}"; exit 1; }
	@gh auth status >/dev/null 2>&1 || { echo "${RED}Error: GitHub CLI not authenticated. Run: gh auth login${NC}"; exit 1; }
	@if [ -z "$(VERSION)" ]; then echo "${RED}Error: VERSION parameter required. Usage: make create-github-release VERSION=x.y.z${NC}"; exit 1; fi
	@echo "${BLUE}Creating GitHub release for v$(VERSION)...${NC}"
	@RELEASE_NOTES_FILE=".release-notes-$(VERSION).md"; \
	RELEASE_TEMPLATE=".github/RELEASE_TEMPLATE.md"; \
	if [ -f "$$RELEASE_TEMPLATE" ]; then \
		echo "${BLUE}Using release template...${NC}"; \
		sed "s/{version}/$(VERSION)/g; s/{current_tag}/v$(VERSION)/g" $$RELEASE_TEMPLATE > $$RELEASE_NOTES_FILE; \
		CHANGELOG_NOTES=$$(uv run python scripts/extract_release_notes.py $(VERSION) 2>/dev/null || true); \
		if [ -n "$$CHANGELOG_NOTES" ] && [ "$$CHANGELOG_NOTES" != "Release $(VERSION) - See changelog for details." ]; then \
			echo "" >> $$RELEASE_NOTES_FILE; \
			echo "## What's New in v$(VERSION)" >> $$RELEASE_NOTES_FILE; \
			echo "" >> $$RELEASE_NOTES_FILE; \
			echo "$$CHANGELOG_NOTES" >> $$RELEASE_NOTES_FILE; \
		fi; \
	else \
		echo "${BLUE}No release template found, using changelog...${NC}"; \
		CHANGELOG_NOTES=$$(uv run python scripts/extract_release_notes.py $(VERSION) 2>/dev/null || true); \
		if [ -n "$$CHANGELOG_NOTES" ]; then \
			echo "# Release v$(VERSION)" > $$RELEASE_NOTES_FILE; \
			echo "" >> $$RELEASE_NOTES_FILE; \
			echo "$$CHANGELOG_NOTES" >> $$RELEASE_NOTES_FILE; \
		else \
			echo "# Release v$(VERSION)" > $$RELEASE_NOTES_FILE; \
			echo "" >> $$RELEASE_NOTES_FILE; \
			echo "Auto-generated release notes for version $(VERSION)." >> $$RELEASE_NOTES_FILE; \
			echo "" >> $$RELEASE_NOTES_FILE; \
			echo "See the [full changelog](https://github.com/chetmancini/dateutils-python/blob/main/CHANGELOG.md) for details." >> $$RELEASE_NOTES_FILE; \
		fi; \
	fi; \
	echo "${BLUE}Building package for release...${NC}"; \
	$(MAKE) --no-print-directory build >/dev/null 2>&1; \
	echo "${BLUE}Creating GitHub release...${NC}"; \
	gh release create "v$(VERSION)" \
		--title "Release v$(VERSION)" \
		--notes-file $$RELEASE_NOTES_FILE \
		--verify-tag \
		--latest \
		dist/* || { echo "${RED}Failed to create GitHub release${NC}"; rm -f $$RELEASE_NOTES_FILE; exit 1; }; \
	rm -f $$RELEASE_NOTES_FILE
	@echo "${GREEN}✓ GitHub release v$(VERSION) created with release notes${NC}"

release-check: ## Check if ready for release (run all quality checks)
	@echo "${BLUE}Checking release readiness...${NC}"
	@$(MAKE) --no-print-directory clean
	@$(MAKE) --no-print-directory check
	@$(MAKE) --no-print-directory build-check
	@command -v gh >/dev/null 2>&1 || { echo "${RED}Error: GitHub CLI (gh) not found. Install with: brew install gh${NC}"; exit 1; }
	@gh auth status >/dev/null 2>&1 || { echo "${RED}Error: GitHub CLI not authenticated. Run: gh auth login${NC}"; exit 1; }
	@echo "${GREEN}✓ Ready for release${NC}"

release: release-check check-release-exists ## Release the current version (must be versioned first)
	@CURRENT_VERSION=$$(grep '^current_version' .bumpversion.cfg | cut -d' ' -f3); \
	echo "${BLUE}Releasing v$$CURRENT_VERSION...${NC}"; \
	if ! git tag -l | grep -q "^v$$CURRENT_VERSION$$"; then \
		echo "${RED}Error: Tag v$$CURRENT_VERSION not found locally${NC}"; \
		echo "${YELLOW}Make sure you've run 'make version-patch/minor/major' first${NC}"; \
		exit 1; \
	fi; \
	echo "${BLUE}Pushing commits and tags to GitHub...${NC}"; \
	git push origin HEAD --follow-tags; \
	$(MAKE) --no-print-directory create-github-release VERSION=$$CURRENT_VERSION
	@echo "${GREEN}✓ Release completed successfully${NC}"
	@echo "${YELLOW}GitHub Actions will now handle PyPI publication${NC}"

release-draft: release-check ## Create a draft release for the current version
	@CURRENT_VERSION=$$(grep '^current_version' .bumpversion.cfg | cut -d' ' -f3); \
	echo "${BLUE}Creating draft release for v$$CURRENT_VERSION...${NC}"; \
	if ! git tag -l | grep -q "^v$$CURRENT_VERSION$$"; then \
		echo "${RED}Error: Tag v$$CURRENT_VERSION not found locally${NC}"; \
		echo "${YELLOW}Make sure you've run 'make version-patch/minor/major' first${NC}"; \
		exit 1; \
	fi; \
	if gh release view "v$$CURRENT_VERSION" >/dev/null 2>&1; then \
		echo "${YELLOW}Draft release v$$CURRENT_VERSION already exists, updating...${NC}"; \
		gh release delete "v$$CURRENT_VERSION" --yes; \
	fi; \
	git push origin HEAD --follow-tags; \
	RELEASE_NOTES_FILE=".draft-release-notes.md"; \
	RELEASE_TEMPLATE=".github/RELEASE_TEMPLATE.md"; \
	if [ -f "$$RELEASE_TEMPLATE" ]; then \
		sed "s/{version}/$$CURRENT_VERSION/g; s/{current_tag}/v$$CURRENT_VERSION/g" $$RELEASE_TEMPLATE > $$RELEASE_NOTES_FILE; \
		CHANGELOG_NOTES=$$(uv run python scripts/extract_release_notes.py $$CURRENT_VERSION 2>/dev/null || true); \
		if [ -n "$$CHANGELOG_NOTES" ] && [ "$$CHANGELOG_NOTES" != "Release $$CURRENT_VERSION - See changelog for details." ]; then \
			echo "" >> $$RELEASE_NOTES_FILE; \
			echo "## What's New in v$$CURRENT_VERSION" >> $$RELEASE_NOTES_FILE; \
			echo "" >> $$RELEASE_NOTES_FILE; \
			echo "$$CHANGELOG_NOTES" >> $$RELEASE_NOTES_FILE; \
		fi; \
	else \
		echo "# Draft Release v$$CURRENT_VERSION" > $$RELEASE_NOTES_FILE; \
		echo "" >> $$RELEASE_NOTES_FILE; \
		CHANGELOG_NOTES=$$(uv run python scripts/extract_release_notes.py $$CURRENT_VERSION 2>/dev/null || true); \
		if [ -n "$$CHANGELOG_NOTES" ]; then \
			echo "$$CHANGELOG_NOTES" >> $$RELEASE_NOTES_FILE; \
		else \
			echo "Draft release notes for version $$CURRENT_VERSION." >> $$RELEASE_NOTES_FILE; \
		fi; \
	fi; \
	$(MAKE) --no-print-directory build >/dev/null 2>&1; \
	gh release create "v$$CURRENT_VERSION" \
		--title "Release v$$CURRENT_VERSION" \
		--notes-file $$RELEASE_NOTES_FILE \
		--draft \
		dist/*; \
	rm -f $$RELEASE_NOTES_FILE
	@echo "${GREEN}✓ Draft release created. Review and publish when ready with:${NC}"
	@CURRENT_VERSION=$$(grep '^current_version' .bumpversion.cfg | cut -d' ' -f3); \
	echo "${BLUE}  gh release edit v$$CURRENT_VERSION --draft=false${NC}"
	@echo "${BLUE}  OR: make release${NC}"

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

test-release-notes: ## Test release notes extraction for current version
	@CURRENT_VERSION=$$(grep '^current_version' .bumpversion.cfg | cut -d' ' -f3); \
	echo "${BLUE}Testing release notes extraction for v$$CURRENT_VERSION...${NC}"; \
	if [ -f "CHANGELOG.md" ]; then \
		echo "${YELLOW}Changelog sections found:${NC}"; \
		grep "^## \[" CHANGELOG.md | head -5; \
		echo ""; \
		echo "${YELLOW}Release notes for v$$CURRENT_VERSION:${NC}"; \
		uv run python scripts/extract_release_notes.py $$CURRENT_VERSION || echo "${RED}No release notes found for v$$CURRENT_VERSION${NC}"; \
	else \
		echo "${RED}CHANGELOG.md not found${NC}"; \
	fi

gh-status: ## Show GitHub CLI authentication status
	@command -v gh >/dev/null 2>&1 || { echo "${RED}Error: GitHub CLI (gh) not found. Install with: brew install gh${NC}"; exit 1; }
	@echo "${BLUE}GitHub CLI Status:${NC}"
	@gh auth status
	@echo ""
	@echo "${BLUE}Current repository:${NC}"
	@gh repo view --json name,owner,defaultBranchRef | uv run python -c "import sys, json; data=json.load(sys.stdin); print(f\"Repository: {data['owner']['login']}/{data['name']}\"); print(f\"Default branch: {data['defaultBranchRef']['name']}\")" || echo "${YELLOW}Could not retrieve repository information${NC}"

# Safety check for dangerous operations
.PHONY: init deps install pre-commit pre-commit-run lint lint-fix format format-check typecheck test test-fast coverage coverage-html watch-test check dev fix build build-check update-changelog version-patch version-minor version-major create-github-release check-release-exists release-check release release-draft clean requirements version help test-release-notes gh-status
