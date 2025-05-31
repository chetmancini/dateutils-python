#!/usr/bin/env python3
"""
Simple script to update CHANGELOG.md with new version information.
"""

import argparse
import re
from datetime import datetime
from pathlib import Path


def update_changelog(version: str, date: str | None = None) -> None:
    """Update CHANGELOG.md with new version entry."""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    changelog_path = Path("CHANGELOG.md")

    if not changelog_path.exists():
        print("CHANGELOG.md not found!")
        return

    content = changelog_path.read_text()

    # Find the placeholder or create new entry
    unreleased_pattern = r"## \[Unreleased\]"
    version_pattern = r"## \[0\.1\.0\] - YYYY-MM-DD"

    new_entry = f"""## [{version}] - {date}

### Added
-

### Changed
-

### Fixed
-

## [Unreleased]

### Added
-

### Changed
-

### Fixed
-

"""

    if re.search(unreleased_pattern, content):
        # Replace unreleased section
        content = re.sub(unreleased_pattern + r".*?(?=## \[|\Z)", new_entry, content, flags=re.DOTALL)
    elif re.search(version_pattern, content):
        # Replace the placeholder version
        content = re.sub(version_pattern, f"## [{version}] - {date}", content)
        # Add unreleased section after the new version
        content = re.sub(
            f"(## \\[{re.escape(version)}\\] - {date}.*?)(?=## \\[|\\Z)", f"\\1\n{new_entry}", content, flags=re.DOTALL
        )
    else:
        print("Could not find appropriate location to update changelog")
        return

    changelog_path.write_text(content)
    print(f"Updated CHANGELOG.md with version {version}")


def main():
    parser = argparse.ArgumentParser(description="Update CHANGELOG.md")
    parser.add_argument("version", help="Version number (e.g., 0.2.0)")
    parser.add_argument("--date", help="Release date (YYYY-MM-DD)", default=None)

    args = parser.parse_args()
    update_changelog(args.version, args.date)


if __name__ == "__main__":
    main()
