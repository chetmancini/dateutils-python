
# Run tests
test:
	uv run pytest tests

lint:
	uv run ruff check .

format:
	uv run ruff format .

.PHONY: test lint format