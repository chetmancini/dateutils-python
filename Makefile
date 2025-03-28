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

.PHONY: init dev test coverage lint format build clean
