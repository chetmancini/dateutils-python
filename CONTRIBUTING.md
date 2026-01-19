# Contributing to dateutils-python

Thank you for your interest in contributing to `dateutils-python`! We welcome contributions from the community.

## Reporting Issues

If you encounter a bug or have a suggestion for improvement, please check the [issue tracker](https://github.com/chetmancini/dateutils-python/issues) to see if a similar issue already exists. If not, feel free to open a new issue.

When reporting bugs, please include:

*   Your operating system name and version.
*   Your Python version.
*   Steps to reproduce the bug.
*   The expected behavior.
*   The actual behavior.

## Suggesting Enhancements

If you have an idea for a new feature or an enhancement to an existing one, please open an issue first to discuss it. This allows us to coordinate efforts and ensure the proposed change fits the project's scope and direction.

## Development Setup

1.  **Fork and clone the repository:**
    ```bash
    git clone https://github.com/YOUR_USERNAME/dateutils-python.git
    cd dateutils-python
    ```

2.  **Set up the development environment:**
    ```bash
    make dev  # Complete setup: installs uv, dependencies, package, and pre-commit hooks
    ```

3.  **Verify setup:**
    ```bash
    make test  # Run tests to ensure everything works
    ```

## Development Workflow

### Key Commands

Run `make help` to see all available commands. The most important ones:

- **`make dev`** - Complete development environment setup
- **`make fix`** - Fix formatting and linting issues automatically
- **`make check`** - Run all quality checks (lint, format-check, typecheck, test)
- **`make pre-commit-run`** - Run all pre-commit hooks manually
- **`make test-fast`** - Quick tests without coverage
- **`make watch-test`** - Continuous testing (requires `brew install entr`)

### Recommended Workflow

```bash
# 1. Make your changes
# 2. Fix common issues and run checks
make fix && make check

# 3. For continuous development (optional)
make watch-test  # In a separate terminal
```

**Note:** Pre-commit hooks are automatically installed and will run on every commit, checking your code before it's committed.

## Pull Request Process

1.  **Create a feature branch:**
    ```bash
    git checkout -b your-feature-name
    ```

2.  **Make your changes and add tests** for any new functionality.

3.  **Ensure all checks pass:**
    ```bash
    make check
    ```

4.  **Commit and push:**
    ```bash
    git commit -am "Add some feature"
    git push origin your-feature-name
    ```

5.  **Open a Pull Request** on GitHub with a clear description of your changes.

## Code Standards

This project uses automated tooling with pre-commit hooks:

- **`ruff`** for formatting and linting
- **`ty`** for type checking
- **`pytest`** for testing

Pre-commit hooks automatically run these checks on every commit. The `make fix` command automatically resolves most style issues. Ensure `make check` passes before submitting your PR.

## Release Process

**Note:** This section is for maintainers who have push access to the repository.

We use automated semantic versioning and GitHub Actions for releases. The process is streamlined with Make targets:

### Quick Release Commands

```bash
# For bug fixes and patches
make release-patch  # 0.1.0 → 0.1.1

# For new features (backward compatible)
make release-minor  # 0.1.0 → 0.2.0

# For breaking changes
make release-major  # 0.1.0 → 1.0.0
```

### What Happens During Release

1. **Quality checks** - Runs full test suite and builds package
2. **Version bump** - Updates version in `pyproject.toml` and `dateutils/__init__.py`
3. **Git operations** - Creates commit, tags with version, and pushes
4. **GitHub Actions** - Automatically builds, tests, and publishes to PyPI
5. **GitHub Release** - Creates release with auto-generated notes

### Manual Steps (if needed)

```bash
# Check if ready for release
make release-check

# Bump version only (without pushing)
make version-patch   # or version-minor, version-major

# Test publish to TestPyPI first
make publish-test

# Manual publish to PyPI (if needed)
make publish
```

The automated workflow handles everything from testing to PyPI publication when you push a version tag.

## Getting Help

If you need help:
- Open an issue with the "question" label
- Check existing issues and discussions
- Review the codebase and tests for examples

We will review your pull request as soon as possible. Thank you for contributing!
