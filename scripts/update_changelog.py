#!/usr/bin/env python3
"""
Intelligently update CHANGELOG.md with new version information.
Analyzes git changes between the most recent tag and HEAD to generate meaningful entries.
Used by Makefile version bump commands.
"""

import argparse
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path


def run_git_command(cmd: list[str]) -> str:
    """Run a git command and return the output."""
    git_binary = shutil.which("git")
    if git_binary is None:
        return ""

    try:
        result = subprocess.run([git_binary, *cmd], capture_output=True, text=True, check=True)  # noqa: S603
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return ""


def get_latest_tag() -> str:
    """Get the most recent git tag."""
    tags = run_git_command(["tag", "--sort=-version:refname"])
    if tags:
        return tags.split("\n")[0]
    return ""


def get_commits_since_tag(tag: str) -> list[dict[str, str]]:
    """Get commit messages and metadata since the given tag."""
    if not tag:
        # If no tags, get all commits
        cmd = ["log", "--pretty=format:%H|%s|%b", "--no-merges"]
    else:
        cmd = ["log", f"{tag}..HEAD", "--pretty=format:%H|%s|%b", "--no-merges"]

    output = run_git_command(cmd)
    if not output:
        return []

    commits = []
    for line in output.split("\n"):
        if "|" in line:
            parts = line.split("|", 2)
            if len(parts) >= 2:  # noqa: PLR2004
                commits.append({"hash": parts[0], "subject": parts[1], "body": parts[2] if len(parts) > 2 else ""})  # noqa: PLR2004

    return commits


def get_changed_files(tag: str) -> set[str]:
    """Get list of files that changed since the tag."""
    if not tag:
        cmd = ["ls-files"]
    else:
        cmd = ["diff", "--name-only", f"{tag}..HEAD"]

    output = run_git_command(cmd)
    return set(output.split("\n")) if output else set()


def _get_commit_patterns() -> dict[str, list[str]]:
    """Return patterns for conventional commits."""
    return {
        "added": [r"^feat(\(.+\))?\s*:\s*(.+)", r"^add(\(.+\))?\s*:\s*(.+)", r"^\+\s*(.+)", r"^new\s*:\s*(.+)"],
        "fixed": [
            r"^fix(\(.+\))?\s*:\s*(.+)",
            r"^bug(\(.+\))?\s*:\s*(.+)",
            r"^patch(\(.+\))?\s*:\s*(.+)",
            r"^hotfix(\(.+\))?\s*:\s*(.+)",
        ],
        "changed": [
            r"^refactor(\(.+\))?\s*:\s*(.+)",
            r"^update(\(.+\))?\s*:\s*(.+)",
            r"^change(\(.+\))?\s*:\s*(.+)",
            r"^improve(\(.+\))?\s*:\s*(.+)",
            r"^enhance(\(.+\))?\s*:\s*(.+)",
        ],
    }


def _categorize_by_pattern(subject: str, patterns: dict[str, list[str]]) -> tuple[str | None, str | None]:
    """Categorize a commit subject using conventional commit patterns."""
    for category, category_patterns in patterns.items():
        for pattern in category_patterns:
            match = re.match(pattern, subject, re.IGNORECASE)
            if match:
                desc = match.groups()[-1].strip()
                return category, desc
    return None, None


def _categorize_by_keywords(subject: str) -> str:
    """Categorize a commit subject using keyword analysis."""
    subject_lower = subject.lower()
    if any(word in subject_lower for word in ["add", "new", "create", "implement", "introduce"]):
        return "added"
    if any(word in subject_lower for word in ["fix", "bug", "resolve", "correct", "patch"]):
        return "fixed"
    if any(word in subject_lower for word in ["update", "change", "modify", "refactor", "improve", "enhance"]):
        return "changed"
    return "changed"  # Default category


def _analyze_file_changes(changed_files: set[str]) -> list[str]:
    """Analyze file changes for additional context."""
    new_files = [f for f in changed_files if f and any(kw in f.lower() for kw in ["new", "add"])]
    if new_files:
        return [f"Added {len(new_files)} new file{'s' if len(new_files) > 1 else ''}"]
    return []


def categorize_changes(commits: list[dict[str, str]], changed_files: set[str]) -> dict[str, list[str]]:
    """Categorize changes into Added/Changed/Fixed based on commits and files."""
    changes = {"added": [], "changed": [], "fixed": []}
    patterns = _get_commit_patterns()

    # Process commits
    for commit in commits:
        subject = commit["subject"].strip()
        category, desc = _categorize_by_pattern(subject, patterns)

        if category and desc and desc not in changes[category]:
            changes[category].append(desc)
        else:
            category = _categorize_by_keywords(subject)
            if subject not in changes[category]:
                changes[category].append(subject)

    # Add file-based insights
    file_changes = _analyze_file_changes(changed_files)
    for change in file_changes:
        if change not in changes["added"]:
            changes["added"].append(change)

    # Remove duplicates and clean up
    for category, items in changes.items():
        changes[category] = list(dict.fromkeys(items))  # Remove duplicates while preserving order
        changes[category] = [item for item in changes[category] if item.strip()]  # Remove empty items

    return changes


def format_changelog_entry(version: str, date: str, changes: dict[str, list[str]]) -> str:
    """Format the changelog entry."""
    entry = f"## [{version}] - {date}\n\n"

    # Add sections with content
    for section, items in [("Added", changes["added"]), ("Changed", changes["changed"]), ("Fixed", changes["fixed"])]:
        entry += f"### {section}\n"
        if items:
            for item in items:
                # Ensure item starts with capital letter and ends with period if it doesn't already
                formatted_item = item[0].upper() + item[1:] if item else ""
                if formatted_item and not formatted_item.endswith((".", "!", "?")):
                    formatted_item += "."
                entry += f"- {formatted_item}\n"
        else:
            entry += "-\n"
        entry += "\n"

    return entry


def update_changelog(version: str, date: str | None = None) -> None:
    """Update CHANGELOG.md with intelligent analysis of changes."""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    changelog_path = Path("CHANGELOG.md")

    if not changelog_path.exists():
        print(f"Error: {changelog_path} not found!")
        return

    print("🔍 Analyzing changes since last tag...")

    # Get the latest tag and analyze changes
    latest_tag = get_latest_tag()
    if latest_tag:
        print(f"📍 Found latest tag: {latest_tag}")
    else:
        print("📍 No previous tags found, analyzing all commits")

    commits = get_commits_since_tag(latest_tag)
    changed_files = get_changed_files(latest_tag)

    print(f"📝 Found {len(commits)} commits and {len(changed_files)} changed files")

    # Categorize changes
    changes = categorize_changes(commits, changed_files)

    # Show summary of what was found
    total_changes = sum(len(items) for items in changes.values())
    if total_changes > 0:
        print(f"✨ Generated {total_changes} changelog entries:")
        for category, items in changes.items():
            if items:
                print(f"   {category.title()}: {len(items)} items")
    else:
        print("⚠️  No significant changes detected, creating template entry")
        changes = {"added": [], "changed": [], "fixed": []}

    # Read current changelog
    content = changelog_path.read_text()

    # Create the new version entry
    new_version_entry = format_changelog_entry(version, date, changes)

    # Look for the Unreleased section and replace it with the new version
    unreleased_pattern = r"## \[Unreleased\].*?(?=^## \[|\Z)"

    if re.search(r"## \[Unreleased\]", content, re.MULTILINE):
        # Replace the unreleased section with the new version, then add a new unreleased section
        content = re.sub(
            unreleased_pattern,
            new_version_entry + "## [Unreleased]\n\n### Added\n-\n\n### Changed\n-\n\n### Fixed\n-\n\n",
            content,
            flags=re.MULTILINE | re.DOTALL,
        )
    else:
        # If no Unreleased section, add the new version at the top after the main header
        header_pattern = r"(# [^\n]+\n+)"
        if re.search(header_pattern, content):
            content = re.sub(
                header_pattern,
                f"\\1## [Unreleased]\n\n### Added\n-\n\n### Changed\n-\n\n### Fixed\n-\n\n{new_version_entry}",
                content,
            )
        else:
            # Fallback: just prepend to the file
            content = (
                f"# Changelog\n\n## [Unreleased]\n\n### Added\n-\n\n### Changed\n-\n\n### Fixed\n-\n\n{new_version_entry}"
                + content
            )

    changelog_path.write_text(content)
    print(f"✅ Updated {changelog_path} with version {version}")


def main():
    parser = argparse.ArgumentParser(description="Intelligently update CHANGELOG.md with git analysis")
    parser.add_argument("version", help="Version number (e.g., 1.0.0)")
    parser.add_argument("--date", help="Release date (YYYY-MM-DD, defaults to today)")

    args = parser.parse_args()
    update_changelog(args.version, args.date)


if __name__ == "__main__":
    main()
