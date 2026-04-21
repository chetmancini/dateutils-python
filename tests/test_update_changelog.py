import importlib.util
from pathlib import Path
from typing import Any

import pytest


def _load_update_changelog_module() -> Any:
    script_path = Path(__file__).resolve().parent.parent / "scripts" / "update_changelog.py"
    spec = importlib.util.spec_from_file_location("update_changelog_script", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


update_changelog_script = _load_update_changelog_module()


def test_validate_changelog_content_rejects_duplicate_versions() -> None:
    with pytest.raises(ValueError, match="duplicate release sections: 0.1.0"):
        update_changelog_script.validate_changelog_content(
            """# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
-

### Changed
-

### Fixed
-

## [0.1.0] - 2025-01-01

### Added
-

### Changed
-

### Fixed
-

## [0.1.0] - 2025-01-02

### Added
-

### Changed
-

### Fixed
-
"""
        )


def test_validate_changelog_content_rejects_multiple_unreleased_sections() -> None:
    with pytest.raises(ValueError, match="exactly one Unreleased section, found 2"):
        update_changelog_script.validate_changelog_content(
            """# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
-

### Changed
-

### Fixed
-

## [0.1.0] - 2025-01-01

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
        )


def test_update_changelog_keeps_single_unreleased_and_single_release(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    changelog_path = tmp_path / "CHANGELOG.md"
    changelog_path.write_text(
        """# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
-

### Changed
-

### Fixed
-

## [0.6.0] - 2026-02-22

### Added
-

### Changed
-

### Fixed
-
""",
        encoding="utf-8",
    )

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(update_changelog_script, "get_latest_tag", lambda: "v0.6.0")
    monkeypatch.setattr(update_changelog_script, "get_commits_since_tag", lambda _tag: [])
    monkeypatch.setattr(update_changelog_script, "get_changed_files", lambda _tag: set())
    monkeypatch.setattr(update_changelog_script, "CHANGELOG_PATH", Path("CHANGELOG.md"))

    update_changelog_script.update_changelog("0.6.1", "2026-04-20")

    content = changelog_path.read_text(encoding="utf-8")
    assert content.count("## [Unreleased]") == 1
    assert content.count("## [0.6.1] - 2026-04-20") == 1

    section_names = update_changelog_script._extract_section_names(content)
    assert section_names[:3] == ["Unreleased", "0.6.1", "0.6.0"]


def test_update_changelog_inserts_unreleased_before_validating_legacy_file(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    changelog_path = tmp_path / "CHANGELOG.md"
    changelog_path.write_text(
        """# Changelog

All notable changes to this project will be documented in this file.

## [0.6.0] - 2026-02-22

### Added
-

### Changed
-

### Fixed
-
""",
        encoding="utf-8",
    )

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(update_changelog_script, "get_latest_tag", lambda: "v0.6.0")
    monkeypatch.setattr(update_changelog_script, "get_commits_since_tag", lambda _tag: [])
    monkeypatch.setattr(update_changelog_script, "get_changed_files", lambda _tag: set())
    monkeypatch.setattr(update_changelog_script, "CHANGELOG_PATH", Path("CHANGELOG.md"))

    update_changelog_script.update_changelog("0.6.1", "2026-04-20")

    content = changelog_path.read_text(encoding="utf-8")
    assert content.count("## [Unreleased]") == 1
    assert content.count("## [0.6.1] - 2026-04-20") == 1

    section_names = update_changelog_script._extract_section_names(content)
    assert section_names[:3] == ["Unreleased", "0.6.1", "0.6.0"]
