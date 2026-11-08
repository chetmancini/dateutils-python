#!/usr/bin/env python3
"""Validate that a release tag matches the project version."""

import argparse
import tomllib
from pathlib import Path

DEFAULT_PYPROJECT_PATH = Path(__file__).resolve().parent.parent / "pyproject.toml"


def read_project_version(pyproject_path: Path = DEFAULT_PYPROJECT_PATH) -> str:
    """Read and validate the project version from pyproject.toml."""
    content = pyproject_path.read_text(encoding="utf-8")
    try:
        pyproject = tomllib.loads(content)
    except tomllib.TOMLDecodeError as exc:
        raise ValueError(f"{pyproject_path} does not define a non-empty project.version") from exc
    project = pyproject.get("project")
    version = project.get("version") if isinstance(project, dict) else None
    if not isinstance(version, str) or not version:
        raise ValueError(f"{pyproject_path} does not define a non-empty project.version")
    return version


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
