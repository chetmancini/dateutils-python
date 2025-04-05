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

## Setting up the Development Environment

1.  **Fork the repository:** Click the "Fork" button on the [GitHub repository page](https://github.com/chetmancini/dateutils-python).
2.  **Clone your fork:**
    ```bash
    git clone https://github.com/YOUR_USERNAME/dateutils-python.git
    cd dateutils-python
    ```
3.  **Install dependencies:** We use `uv` for dependency management and task running. The `Makefile` provides convenient commands:
    ```bash
    make init # Ensure uv is installed
    make deps # Install dependencies
    ```

## Pull Request Process

1.  **Create a feature branch:**
    ```bash
    git checkout -b your-feature-name
    ```
2.  **Make your changes:** Implement your feature or bug fix.
3.  **Add tests:** Ensure your changes are covered by new or existing tests.
4.  **Run checks:** Before submitting, make sure all checks pass:
    ```bash
    make lint
    make format
    make typecheck
    make test
    ```
5.  **Commit your changes:** Use clear and concise commit messages.
    ```bash
    git commit -am "Add some feature"
    ```
6.  **Push to your fork:**
    ```bash
    git push origin your-feature-name
    ```
7.  **Open a Pull Request:** Go to the original `dateutils-python` repository on GitHub and open a pull request from your feature branch.
8.  **Describe your changes:** Provide a clear description of the changes in your pull request.

We will review your pull request as soon as possible. Thank you for contributing!
