#!/usr/bin/env python3
"""Validate public module doctests and executable README/API examples."""

import argparse
import doctest
import inspect
import io
import re
import traceback
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from types import ModuleType

import dateutils
from dateutils import dateutils as dateutils_module
from dateutils import parsing as parsing_module
from dateutils import timezones as timezones_module

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
README_PATH = REPOSITORY_ROOT / "README.md"
API_PATH = REPOSITORY_ROOT / "docs" / "API.md"
PUBLIC_MODULES: tuple[ModuleType, ...] = (dateutils_module, parsing_module, timezones_module)


def extract_python_blocks(markdown: str) -> list[str]:
    """Return blocks opened by a Markdown fence that is exactly ``python``."""
    blocks: list[str] = []
    block_lines: list[str] | None = None

    for line in markdown.splitlines(keepends=True):
        if block_lines is None:
            if line.rstrip("\r\n") == "```python":
                block_lines = []
            continue

        if line.rstrip("\r\n") == "```":
            blocks.append("".join(block_lines))
            block_lines = None
        else:
            block_lines.append(line)

    return blocks


def validate_markdown_blocks(markdown: str, document_name: str) -> list[str]:
    """Execute a Markdown document's Python blocks in isolation and return any failure reports."""
    failures: list[str] = []
    for index, block in enumerate(extract_python_blocks(markdown), start=1):
        output = io.StringIO()
        try:
            with redirect_stdout(output), redirect_stderr(output):
                exec(compile(block, f"{document_name} Python block {index}", "exec"), {})  # noqa: S102
        except Exception:
            captured_output = output.getvalue()
            report = f"{document_name} Python block {index} failed."
            if captured_output:
                report += f"\nCaptured output:\n{captured_output}"
            failures.append(f"{report}\n{traceback.format_exc()}")
    return failures


SIGNATURE_LINE_RE = re.compile(r"^### `([A-Za-z_][A-Za-z0-9_]*)`\n\n`([^`]+)`", flags=re.MULTILINE)


def _normalize_signature(signature: str) -> str:
    """Strip whitespace and ``collections.abc.`` prefixes for drift comparison.

    The documented signatures omit the ``collections.abc`` module path for
    brevity (``Iterable`` instead of ``collections.abc.Iterable``); this
    normalization makes both sides comparable.
    """
    return re.sub(r"\s+", "", signature).replace("collections.abc.", "")


def validate_api_signatures(markdown: str) -> list[str]:
    """Verify documented signatures under callable headings match the live package."""
    failures: list[str] = []
    for match in SIGNATURE_LINE_RE.finditer(markdown):
        name, documented = match.groups()
        obj = getattr(dateutils, name, None)
        if obj is None or not callable(obj):
            continue
        try:
            live = name + str(inspect.signature(obj))
        except (TypeError, ValueError):
            continue  # e.g. exception classes without a meaningful signature
        if _normalize_signature(documented) != _normalize_signature(live):
            failures.append(f"{name}: documented signature `{documented}` does not match `{live}`")
    return failures


def validate_module_doctests(*, verbose: bool = False) -> list[str]:
    """Run doctests through normal package imports and return failing modules."""
    failures: list[str] = []
    for module in PUBLIC_MODULES:
        result = doctest.testmod(module, verbose=verbose, optionflags=doctest.ELLIPSIS)
        if result.failed:
            failures.append(f"{module.__name__}: {result.failed} doctest failure(s)")
    return failures


def main(argv: list[str] | None = None) -> int:
    """Run selected documentation checks and return a process exit status."""
    parser = argparse.ArgumentParser(description=__doc__)
    checks = parser.add_mutually_exclusive_group()
    checks.add_argument("--readme-only", action="store_true", help="validate only README Python blocks")
    checks.add_argument("--doctest-only", action="store_true", help="validate only public module doctests")
    args = parser.parse_args(argv)

    failures: list[str] = []
    if not args.doctest_only:
        documents: tuple[Path, ...] = (README_PATH,) if args.readme_only else (README_PATH, API_PATH)
        for path in documents:
            failures.extend(validate_markdown_blocks(path.read_text(encoding="utf-8"), path.name))
        if not args.readme_only:
            failures.extend(validate_api_signatures(API_PATH.read_text(encoding="utf-8")))
    if not args.readme_only:
        failures.extend(validate_module_doctests(verbose=True))

    if failures:
        print("Documentation validation failed:\n" + "\n".join(failures))
        return 1

    print("Documentation validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
