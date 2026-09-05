import importlib.util
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
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


def _valid_changelog_content() -> str:
    return """# Changelog

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
"""


def test_run_git_command_strips_output_and_uses_git_arguments(monkeypatch: pytest.MonkeyPatch) -> None:
    commands: list[list[str]] = []

    def fake_which(name: str) -> str:
        assert name == "git"
        return "/opt/bin/git"

    def fake_run(command: list[str], *, capture_output: bool, text: bool, check: bool) -> SimpleNamespace:
        assert capture_output is True
        assert text is True
        assert check is True
        commands.append(command)
        return SimpleNamespace(stdout="  status output \n")

    monkeypatch.setattr(update_changelog_script.shutil, "which", fake_which)
    monkeypatch.setattr(update_changelog_script.subprocess, "run", fake_run)

    assert update_changelog_script.run_git_command(["status", "--short"]) == "status output"
    assert commands == [["/opt/bin/git", "status", "--short"]]


def test_run_git_command_preserves_successful_empty_output(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(update_changelog_script.shutil, "which", lambda _name: "/opt/bin/git")
    monkeypatch.setattr(
        update_changelog_script.subprocess,
        "run",
        lambda *_args, **_kwargs: SimpleNamespace(stdout=" \n"),
    )

    assert update_changelog_script.run_git_command(["tag"]) == ""


def test_run_git_command_rejects_missing_git(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(update_changelog_script.shutil, "which", lambda _name: None)

    with pytest.raises(RuntimeError, match="^git executable not found$"):
        update_changelog_script.run_git_command(["status"])


def test_run_git_command_hides_command_failure_details(monkeypatch: pytest.MonkeyPatch) -> None:
    command_error = subprocess.CalledProcessError(
        returncode=1,
        cmd=["git", "status"],
        stderr="private git stderr",
    )

    monkeypatch.setattr(update_changelog_script.shutil, "which", lambda _name: "/opt/bin/git")
    monkeypatch.setattr(
        update_changelog_script.subprocess, "run", lambda *_args, **_kwargs: (_ for _ in ()).throw(command_error)
    )

    with pytest.raises(RuntimeError, match="^git command failed$") as raised:
        update_changelog_script.run_git_command(["status"])

    assert raised.value.__cause__ is command_error
    assert "private git stderr" not in str(raised.value)


def test_get_latest_tag_handles_empty_and_multiple_tags(monkeypatch: pytest.MonkeyPatch) -> None:
    commands: list[list[str]] = []
    outputs = iter(["", "v0.6.1\nv0.6.0"])

    def fake_run_git_command(command: list[str]) -> str:
        commands.append(command)
        return next(outputs)

    monkeypatch.setattr(update_changelog_script, "run_git_command", fake_run_git_command)

    assert update_changelog_script.get_latest_tag() == ""
    assert update_changelog_script.get_latest_tag() == "v0.6.1"
    assert commands == [["tag", "--sort=-version:refname"], ["tag", "--sort=-version:refname"]]


def test_get_commits_since_tag_builds_commands_and_parses_output(monkeypatch: pytest.MonkeyPatch) -> None:
    pretty_format = "%H%x1f%s%x1f%b"
    valid_line = "abc123\x1ffeat: add parser\x1fBody text"
    commands: list[list[str]] = []
    outputs = iter(["", f"{valid_line}\nmalformed"])

    def fake_run_git_command(command: list[str]) -> str:
        commands.append(command)
        return next(outputs)

    monkeypatch.setattr(update_changelog_script, "run_git_command", fake_run_git_command)

    assert update_changelog_script.get_commits_since_tag("") == []
    assert update_changelog_script.get_commits_since_tag("v0.6.0") == [
        update_changelog_script.Commit(hash="abc123", subject="feat: add parser", body="Body text")
    ]
    assert commands == [
        ["log", f"--pretty=format:{pretty_format}", "--no-merges"],
        ["log", "v0.6.0..HEAD", f"--pretty=format:{pretty_format}", "--no-merges"],
    ]


def test_get_changed_files_builds_commands_and_handles_empty_output(monkeypatch: pytest.MonkeyPatch) -> None:
    commands: list[list[str]] = []
    outputs = iter(["", "src/dateutils.py\nscripts/update_changelog.py"])

    def fake_run_git_command(command: list[str]) -> str:
        commands.append(command)
        return next(outputs)

    monkeypatch.setattr(update_changelog_script, "run_git_command", fake_run_git_command)

    assert update_changelog_script.get_changed_files("") == set()
    assert update_changelog_script.get_changed_files("v0.6.0") == {
        "src/dateutils.py",
        "scripts/update_changelog.py",
    }
    assert commands == [
        ["ls-files"],
        ["diff", "--name-only", "v0.6.0..HEAD"],
    ]


def test_parse_commit_line_returns_commit_metadata() -> None:
    commit = update_changelog_script._parse_commit_line("abc123\x1ffeat: add parser\x1fBody text")

    assert commit == update_changelog_script.Commit(
        hash="abc123",
        subject="feat: add parser",
        body="Body text",
    )


def test_parse_commit_line_allows_pipe_characters_in_subject_and_body() -> None:
    commit = update_changelog_script._parse_commit_line("abc123\x1ffix: keep a | b\x1fBody | details")

    assert commit == update_changelog_script.Commit(
        hash="abc123",
        subject="fix: keep a | b",
        body="Body | details",
    )


def test_parse_commit_line_rejects_malformed_lines() -> None:
    assert update_changelog_script._parse_commit_line("") is None
    assert update_changelog_script._parse_commit_line("abc123\x1fmissing body") is None
    assert update_changelog_script._parse_commit_line("\x1fmissing hash\x1fBody") is None
    assert update_changelog_script._parse_commit_line("abc123\x1f\x1fBody") is None


def test_categorize_by_pattern_covers_change_families_and_fallback() -> None:
    patterns = update_changelog_script._get_commit_patterns()

    assert update_changelog_script._categorize_by_pattern("feat: add parser", patterns) == ("added", "add parser")
    assert update_changelog_script._categorize_by_pattern("fix(parser): reject invalid input", patterns) == (
        "fixed",
        "reject invalid input",
    )
    assert update_changelog_script._categorize_by_pattern("refactor: simplify parser", patterns) == (
        "changed",
        "simplify parser",
    )
    assert update_changelog_script._categorize_by_pattern("document release behavior", patterns) == (None, None)


def test_categorize_by_keywords_covers_all_categories_and_default() -> None:
    assert update_changelog_script._categorize_by_keywords("introduce a parser") == "added"
    assert update_changelog_script._categorize_by_keywords("resolve a parsing bug") == "fixed"
    assert update_changelog_script._categorize_by_keywords("modify the parser") == "changed"
    assert update_changelog_script._categorize_by_keywords("document release behavior") == "changed"


def test_analyze_file_changes_covers_empty_nonmatching_and_matching_files() -> None:
    assert update_changelog_script._analyze_file_changes(set()) == []
    assert update_changelog_script._analyze_file_changes({"", "src/dateutils.py"}) == []
    assert update_changelog_script._analyze_file_changes({"new_parser.py"}) == ["Added 1 new file"]
    assert update_changelog_script._analyze_file_changes({"add_parser.py", "new_timezone.py"}) == ["Added 2 new files"]


def test_categorize_changes_handles_empty_inputs() -> None:
    assert update_changelog_script.categorize_changes([], set()) == {
        "added": [],
        "changed": [],
        "fixed": [],
    }


def test_categorize_changes_categorizes_commits_and_suppresses_duplicates() -> None:
    commits = [
        update_changelog_script.Commit("1", "feat: add parser", ""),
        update_changelog_script.Commit("2", "fix: reject invalid dates", ""),
        update_changelog_script.Commit("3", "refactor: simplify parser", ""),
        update_changelog_script.Commit("4", "introduce timezone support", ""),
        update_changelog_script.Commit("5", "resolve timezone bug", ""),
        update_changelog_script.Commit("6", "modify format output", ""),
        update_changelog_script.Commit("7", "ordinary note", ""),
        update_changelog_script.Commit("8", "ordinary note", ""),
        update_changelog_script.Commit("9", "feat: add parser", ""),
        update_changelog_script.Commit("10", "   ", ""),
    ]

    changes = update_changelog_script.categorize_changes(commits, {"new_parser.py", "src/dateutils.py"})

    assert changes == {
        "added": ["add parser", "introduce timezone support", "feat: add parser", "Added 1 new file"],
        "changed": ["simplify parser", "modify format output", "ordinary note"],
        "fixed": ["reject invalid dates", "resolve timezone bug"],
    }
    assert changes["changed"].count("ordinary note") == 1


def test_categorize_changes_suppresses_duplicate_file_insight() -> None:
    changes = update_changelog_script.categorize_changes(
        [update_changelog_script.Commit("1", "feat: Added 1 new file", "")],
        {"new_parser.py"},
    )

    assert changes["added"] == ["Added 1 new file"]


def test_format_changelog_entry_formats_populated_and_empty_sections() -> None:
    populated = update_changelog_script.format_changelog_entry(
        "0.6.1",
        "2026-04-20",
        {"added": ["add parser"], "changed": ["Already changed!"], "fixed": [""]},
    )

    assert "## [0.6.1] - 2026-04-20" in populated
    assert "- Add parser.\n" in populated
    assert "- Already changed!\n" in populated
    assert "### Fixed\n- \n" in populated

    empty = update_changelog_script.format_changelog_entry(
        "0.6.2",
        "2026-04-21",
        {"added": [], "changed": [], "fixed": []},
    )

    assert empty.count("\n-\n") == 3


def test_validate_changelog_content_rejects_missing_and_wrong_first_section() -> None:
    with pytest.raises(ValueError, match="must contain at least one section heading"):
        update_changelog_script.validate_changelog_content("# Changelog\n")

    with pytest.raises(ValueError, match="must begin with the Unreleased section"):
        update_changelog_script.validate_changelog_content("## [0.6.0] - 2026-02-22\n")


def test_validate_changelog_content_accepts_valid_content() -> None:
    update_changelog_script.validate_changelog_content(_valid_changelog_content())


def test_validate_changelog_file_handles_missing_and_valid_files(tmp_path: Path) -> None:
    missing_path = tmp_path / "missing-CHANGELOG.md"
    with pytest.raises(FileNotFoundError, match="missing-CHANGELOG.md not found"):
        update_changelog_script.validate_changelog_file(missing_path)

    changelog_path = tmp_path / "CHANGELOG.md"
    changelog_path.write_text(_valid_changelog_content(), encoding="utf-8")
    update_changelog_script.validate_changelog_file(changelog_path)


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


def test_update_changelog_creates_populated_entry_without_previous_tag(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    changelog_path = tmp_path / "CHANGELOG.md"
    changelog_path.write_text(_valid_changelog_content(), encoding="utf-8")

    class FixedDateTime:
        @classmethod
        def now(cls) -> "FixedDateTime":
            return cls()

        def strftime(self, format_string: str) -> str:
            assert format_string == "%Y-%m-%d"
            return "2026-04-20"

    monkeypatch.setattr(update_changelog_script, "datetime", FixedDateTime)
    monkeypatch.setattr(update_changelog_script, "CHANGELOG_PATH", changelog_path)
    monkeypatch.setattr(update_changelog_script, "get_latest_tag", lambda: "")
    monkeypatch.setattr(
        update_changelog_script,
        "get_commits_since_tag",
        lambda tag: [update_changelog_script.Commit("abc123", "feat: add parser", "")],
    )
    monkeypatch.setattr(update_changelog_script, "get_changed_files", lambda tag: {"new_parser.py"})

    update_changelog_script.update_changelog("0.6.1")

    content = changelog_path.read_text(encoding="utf-8")
    assert "## [0.6.1] - 2026-04-20" in content
    assert "- Add parser.\n" in content
    assert "- Added 1 new file.\n" in content
    assert content.count("## [Unreleased]") == 1
    assert update_changelog_script._extract_section_names(content)[:2] == ["Unreleased", "0.6.1"]


def test_update_changelog_rejects_missing_file(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    changelog_path = tmp_path / "missing-CHANGELOG.md"
    monkeypatch.setattr(update_changelog_script, "CHANGELOG_PATH", changelog_path)

    with pytest.raises(FileNotFoundError, match="missing-CHANGELOG.md not found"):
        update_changelog_script.update_changelog("0.6.1", "2026-04-20")


def test_update_changelog_prepends_to_file_without_recognized_header(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    changelog_path = tmp_path / "CHANGELOG.md"
    changelog_path.write_text("Legacy release notes\n", encoding="utf-8")

    monkeypatch.setattr(update_changelog_script, "CHANGELOG_PATH", changelog_path)
    monkeypatch.setattr(update_changelog_script, "get_latest_tag", lambda: "v0.6.0")
    monkeypatch.setattr(update_changelog_script, "get_commits_since_tag", lambda _tag: [])
    monkeypatch.setattr(update_changelog_script, "get_changed_files", lambda _tag: set())

    update_changelog_script.update_changelog("0.6.1", "2026-04-20")

    content = changelog_path.read_text(encoding="utf-8")
    assert content.startswith("# Changelog\n\nAll notable changes to this project will be documented in this file.\n")
    assert "## [0.6.1] - 2026-04-20" in content
    assert content.endswith("Legacy release notes\n")


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


def test_main_validates_changelog(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    changelog_path = tmp_path / "CHANGELOG.md"
    changelog_path.write_text(_valid_changelog_content(), encoding="utf-8")

    monkeypatch.setattr(update_changelog_script, "CHANGELOG_PATH", changelog_path)
    monkeypatch.setattr(sys, "argv", ["update_changelog.py", "--validate"])

    update_changelog_script.main()

    assert "CHANGELOG.md structure is valid" in capsys.readouterr().out


def test_main_rejects_missing_version(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(sys, "argv", ["update_changelog.py"])

    with pytest.raises(SystemExit) as raised:
        update_changelog_script.main()

    assert raised.value.code == 2
    assert "version is required unless --validate is used" in capsys.readouterr().err


def test_main_passes_supplied_version_and_date_to_updater(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[str, str | None]] = []

    def fake_update_changelog(version: str, date: str | None) -> None:
        calls.append((version, date))

    monkeypatch.setattr(update_changelog_script, "update_changelog", fake_update_changelog)
    monkeypatch.setattr(sys, "argv", ["update_changelog.py", "0.6.1", "--date", "2026-04-20"])

    update_changelog_script.main()

    assert calls == [("0.6.1", "2026-04-20")]
