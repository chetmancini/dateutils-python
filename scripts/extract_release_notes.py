#!/usr/bin/env python3
"""
Extract release notes from CHANGELOG.md for a specific version.
Used by the Makefile for GitHub releases.
"""

import argparse
import re
import sys
from pathlib import Path


def extract_release_notes(version: str) -> str:
    """Extract release notes for a specific version from CHANGELOG.md."""
    changelog_path = Path("CHANGELOG.md")

    if not changelog_path.exists():
        print("CHANGELOG.md not found!", file=sys.stderr)
        return ""

    content = changelog_path.read_text()

    # Pattern to match version section
    version_pattern = rf"^## \[{re.escape(version)}\] - (\d{{4}}-\d{{2}}-\d{{2}}).*?(?=^## \[|\Z)"

    match = re.search(version_pattern, content, re.MULTILINE | re.DOTALL)

    if not match:
        print(f"Version {version} not found in CHANGELOG.md", file=sys.stderr)
        return ""

    # Extract the content and clean it up
    section_content = match.group(0)

    # Remove the version header line
    lines = section_content.split("\n")[1:]

    # Remove empty lines at the end
    while lines and not lines[-1].strip():
        lines.pop()

    # Join back and clean up
    notes = "\n".join(lines).strip()

    # If the notes are just empty section headers, provide a default message
    if not notes or all(line.strip() in ["### Added", "### Changed", "### Fixed", "-", ""] for line in lines):
        return f"Release {version} - See changelog for details."

    return notes


def main():
    parser = argparse.ArgumentParser(description="Extract release notes from CHANGELOG.md")
    parser.add_argument("version", help="Version number (e.g., 0.2.0)")
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")

    args = parser.parse_args()

    notes = extract_release_notes(args.version)

    if args.output:
        Path(args.output).write_text(notes)
        print(f"Release notes for {args.version} written to {args.output}", file=sys.stderr)
    else:
        print(notes)


if __name__ == "__main__":
    main()
