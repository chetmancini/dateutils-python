#!/usr/bin/env python3
"""Validate that a release tag matches the project version."""

import argparse
import re
from pathlib import Path

DEFAULT_PYPROJECT_PATH = Path(__file__).resolve().parent.parent / "pyproject.toml"


def read_project_version(pyproject_path: Path = DEFAULT_PYPROJECT_PATH) -> str:
    """Read and validate the project version from pyproject.toml."""
    content = pyproject_path.read_text(encoding="utf-8")
    project_section = re.search(r"^\[project\]\s*$\n(?P<body>.*?)(?=^\[|\Z)", content, flags=re.MULTILINE | re.DOTALL)
    version_match = (
        re.search(r'^version\s*=\s*"([^"]+)"\s*$', project_section.group("body"), flags=re.MULTILINE)
        if project_section is not None
        else None
    )
    if version_match is None:
        raise ValueError(f"{pyproject_path} does not define a non-empty project.version")
    return version_match.group(1)


def validate_release_tag(tag: str, pyproject_path: Path = DEFAULT_PYPROJECT_PATH) -> str:
    """Return the project version when its expected v-prefixed tag matches."""
    version = read_project_version(pyproject_path)
    expected_tag = f"v{version}"
    if tag != expected_tag:
        raise ValueError(f"Release tag {tag!r} does not match project version {version!r}; expected {expected_tag!r}")
    return version


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tag", help="Release tag to validate, for example v1.2.3")
    parser.add_argument("--pyproject", type=Path, default=DEFAULT_PYPROJECT_PATH)
    args = parser.parse_args()

    version = validate_release_tag(args.tag, args.pyproject)
    print(f"Release tag v{version} matches project version {version}")


if __name__ == "__main__":
    main()
