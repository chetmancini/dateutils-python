# Changelog

## [0.3.0] - 2026-01-19

### Added
-

### Changed
- Repository improvements: exports, type hints, and CI enhancements (#2).
- None instead of Optional[X]).
- Update dependencies and Python version support (#1).
- Claude.

### Fixed
- Fix version bumping.

## [0.4.0] - 2026-01-19

### Added
- Fix datetime_end_of_day microseconds and add MONTHS_IN_QUARTER constant.

### Changed
- Achieve 100% test coverage (#9).
- Migrate from mypy to ty for type checking (#8).
- Tooling improvements: dependabot, mypy alignment, and doctest.

### Fixed
- Fix documentation issues and end_of_* microseconds consistency.
- Fix datetime handling bugs: httpdate, datetime_to_utc, pretty_date.
- Upgrade urllib3 to 2.6.3 to fix security vulnerabilities (#3).

## [0.4.1] - 2026-01-19

### Added
-

### Changed
- Make GitHub release a draft for manual review (#10).
- Ci: bump actions/download-artifact from 4 to 7 (#4).
- Ci: bump actions/upload-artifact from 4 to 6 (#6).
- Ci: bump actions/checkout from 4 to 6 (#7).
- Ci: bump astral-sh/setup-uv from 5 to 7 (#5).

### Fixed
-

## [0.5.0] - 2026-01-23

### Added
- Docs: add coverage badge to README (#17).
- Add Claude Code GitHub Workflow (#11).

### Changed
- Generate now goes forward or back.
- Chore: update all transitive dependencies (#16).
- Bump requests from 2.32.3 to 2.32.4 (#13).
- Bump filelock from 3.18.0 to 3.20.3 (#14).
- Ci: bump actions/checkout from 4 to 6 (#12).
- Improve README with badges and comparison section.
- Split release workflow to publish PyPI only on release publish.

### Fixed
- Fix httpdate localization.
- Fix validation on until_q in generate-quarters.
- CM: fix mutable results of federal holidays, each caller gets unique data.
- Fix release instructions to link directly to draft release.

## [0.5.1] - 2026-01-23

### Added
- Add Python 3.14 support to CI and package classifiers (#18).

### Changed
- Format.

### Fixed
- Fix generate_weeks.

## [0.5.2] - 2026-01-25

### Added
- Improve code quality: accept Iterable for holidays, add edge case tests, fix import path (#21).

### Changed
-

### Fixed
- Fix age_in_years leap year birthday edge case (#20).
- Improve code quality: simplify is_leap_year, refactor parse_iso8601 regex, and fix exception handling (#19).

## [0.5.3] - 2026-01-25

### Added
-

### Changed
- Improve code quality: optimize workdays_between, unify holidays parameter, expand exports, and enhance docs (#22).

### Fixed
-

## [Unreleased]

### Added
-

### Changed
-

### Fixed
-

## [0.2.4] - 2025-06-05

### Added
- New release process.

### Changed
- Changelog.

### Fixed
-

All notable changes to this project will be documented in this file.

## [0.2.3] - 2025-05-31

## [0.3.0] - 2026-01-19

### Added
-

### Changed
- Repository improvements: exports, type hints, and CI enhancements (#2).
- None instead of Optional[X]).
- Update dependencies and Python version support (#1).
- Claude.

### Fixed
- Fix version bumping.

## [0.4.0] - 2026-01-19

### Added
- Fix datetime_end_of_day microseconds and add MONTHS_IN_QUARTER constant.

### Changed
- Achieve 100% test coverage (#9).
- Migrate from mypy to ty for type checking (#8).
- Tooling improvements: dependabot, mypy alignment, and doctest.

### Fixed
- Fix documentation issues and end_of_* microseconds consistency.
- Fix datetime handling bugs: httpdate, datetime_to_utc, pretty_date.
- Upgrade urllib3 to 2.6.3 to fix security vulnerabilities (#3).

## [0.4.1] - 2026-01-19

### Added
-

### Changed
- Make GitHub release a draft for manual review (#10).
- Ci: bump actions/download-artifact from 4 to 7 (#4).
- Ci: bump actions/upload-artifact from 4 to 6 (#6).
- Ci: bump actions/checkout from 4 to 6 (#7).
- Ci: bump astral-sh/setup-uv from 5 to 7 (#5).

### Fixed
-

## [0.5.0] - 2026-01-23

### Added
- Docs: add coverage badge to README (#17).
- Add Claude Code GitHub Workflow (#11).

### Changed
- Generate now goes forward or back.
- Chore: update all transitive dependencies (#16).
- Bump requests from 2.32.3 to 2.32.4 (#13).
- Bump filelock from 3.18.0 to 3.20.3 (#14).
- Ci: bump actions/checkout from 4 to 6 (#12).
- Improve README with badges and comparison section.
- Split release workflow to publish PyPI only on release publish.

### Fixed
- Fix httpdate localization.
- Fix validation on until_q in generate-quarters.
- CM: fix mutable results of federal holidays, each caller gets unique data.
- Fix release instructions to link directly to draft release.

## [0.5.1] - 2026-01-23

### Added
- Add Python 3.14 support to CI and package classifiers (#18).

### Changed
- Format.

### Fixed
- Fix generate_weeks.

## [0.5.2] - 2026-01-25

### Added
- Improve code quality: accept Iterable for holidays, add edge case tests, fix import path (#21).

### Changed
-

### Fixed
- Fix age_in_years leap year birthday edge case (#20).
- Improve code quality: simplify is_leap_year, refactor parse_iso8601 regex, and fix exception handling (#19).

## [0.5.3] - 2026-01-25

### Added
-

### Changed
- Improve code quality: optimize workdays_between, unify holidays parameter, expand exports, and enhance docs (#22).

### Fixed
-

## [Unreleased]

### Added
-

### Changed
-

### Fixed
-

## [0.2.4] - 2025-06-05

### Added
- New release process.

### Changed
- Changelog.

### Fixed
-

- Testing release process

## [0.2.1] - 2025-05-31

## [0.3.0] - 2026-01-19

### Added
-

### Changed
- Repository improvements: exports, type hints, and CI enhancements (#2).
- None instead of Optional[X]).
- Update dependencies and Python version support (#1).
- Claude.

### Fixed
- Fix version bumping.

## [0.4.0] - 2026-01-19

### Added
- Fix datetime_end_of_day microseconds and add MONTHS_IN_QUARTER constant.

### Changed
- Achieve 100% test coverage (#9).
- Migrate from mypy to ty for type checking (#8).
- Tooling improvements: dependabot, mypy alignment, and doctest.

### Fixed
- Fix documentation issues and end_of_* microseconds consistency.
- Fix datetime handling bugs: httpdate, datetime_to_utc, pretty_date.
- Upgrade urllib3 to 2.6.3 to fix security vulnerabilities (#3).

## [0.4.1] - 2026-01-19

### Added
-

### Changed
- Make GitHub release a draft for manual review (#10).
- Ci: bump actions/download-artifact from 4 to 7 (#4).
- Ci: bump actions/upload-artifact from 4 to 6 (#6).
- Ci: bump actions/checkout from 4 to 6 (#7).
- Ci: bump astral-sh/setup-uv from 5 to 7 (#5).

### Fixed
-

## [0.5.0] - 2026-01-23

### Added
- Docs: add coverage badge to README (#17).
- Add Claude Code GitHub Workflow (#11).

### Changed
- Generate now goes forward or back.
- Chore: update all transitive dependencies (#16).
- Bump requests from 2.32.3 to 2.32.4 (#13).
- Bump filelock from 3.18.0 to 3.20.3 (#14).
- Ci: bump actions/checkout from 4 to 6 (#12).
- Improve README with badges and comparison section.
- Split release workflow to publish PyPI only on release publish.

### Fixed
- Fix httpdate localization.
- Fix validation on until_q in generate-quarters.
- CM: fix mutable results of federal holidays, each caller gets unique data.
- Fix release instructions to link directly to draft release.

## [0.5.1] - 2026-01-23

### Added
- Add Python 3.14 support to CI and package classifiers (#18).

### Changed
- Format.

### Fixed
- Fix generate_weeks.

## [0.5.2] - 2026-01-25

### Added
- Improve code quality: accept Iterable for holidays, add edge case tests, fix import path (#21).

### Changed
-

### Fixed
- Fix age_in_years leap year birthday edge case (#20).
- Improve code quality: simplify is_leap_year, refactor parse_iso8601 regex, and fix exception handling (#19).

## [0.5.3] - 2026-01-25

### Added
-

### Changed
- Improve code quality: optimize workdays_between, unify holidays parameter, expand exports, and enhance docs (#22).

### Fixed
-

## [Unreleased]

### Added
-

### Changed
-

### Fixed
-

## [0.2.4] - 2025-06-05

### Added
- New release process.

### Changed
- Changelog.

### Fixed
-

### Added
## [0.3.0] - 2026-01-19

### Added
-

### Changed
- Repository improvements: exports, type hints, and CI enhancements (#2).
- None instead of Optional[X]).
- Update dependencies and Python version support (#1).
- Claude.

### Fixed
- Fix version bumping.

## [0.4.0] - 2026-01-19

### Added
- Fix datetime_end_of_day microseconds and add MONTHS_IN_QUARTER constant.

### Changed
- Achieve 100% test coverage (#9).
- Migrate from mypy to ty for type checking (#8).
- Tooling improvements: dependabot, mypy alignment, and doctest.

### Fixed
- Fix documentation issues and end_of_* microseconds consistency.
- Fix datetime handling bugs: httpdate, datetime_to_utc, pretty_date.
- Upgrade urllib3 to 2.6.3 to fix security vulnerabilities (#3).

## [0.4.1] - 2026-01-19

### Added
-

### Changed
- Make GitHub release a draft for manual review (#10).
- Ci: bump actions/download-artifact from 4 to 7 (#4).
- Ci: bump actions/upload-artifact from 4 to 6 (#6).
- Ci: bump actions/checkout from 4 to 6 (#7).
- Ci: bump astral-sh/setup-uv from 5 to 7 (#5).

### Fixed
-

## [0.5.0] - 2026-01-23

### Added
- Docs: add coverage badge to README (#17).
- Add Claude Code GitHub Workflow (#11).

### Changed
- Generate now goes forward or back.
- Chore: update all transitive dependencies (#16).
- Bump requests from 2.32.3 to 2.32.4 (#13).
- Bump filelock from 3.18.0 to 3.20.3 (#14).
- Ci: bump actions/checkout from 4 to 6 (#12).
- Improve README with badges and comparison section.
- Split release workflow to publish PyPI only on release publish.

### Fixed
- Fix httpdate localization.
- Fix validation on until_q in generate-quarters.
- CM: fix mutable results of federal holidays, each caller gets unique data.
- Fix release instructions to link directly to draft release.

## [0.5.1] - 2026-01-23

### Added
- Add Python 3.14 support to CI and package classifiers (#18).

### Changed
- Format.

### Fixed
- Fix generate_weeks.

## [0.5.2] - 2026-01-25

### Added
- Improve code quality: accept Iterable for holidays, add edge case tests, fix import path (#21).

### Changed
-

### Fixed
- Fix age_in_years leap year birthday edge case (#20).
- Improve code quality: simplify is_leap_year, refactor parse_iso8601 regex, and fix exception handling (#19).

## [0.5.3] - 2026-01-25

### Added
-

### Changed
- Improve code quality: optimize workdays_between, unify holidays parameter, expand exports, and enhance docs (#22).

### Fixed
-

## [Unreleased]

### Added
-

### Changed
-

### Fixed
-

## [0.2.4] - 2025-06-05

### Added
- New release process.

### Changed
- Changelog.

### Fixed
-

- Initial release of `dateutils-python`.
- Core date/time utilities (UTC, parsing, formatting, timezone, business days, quarter/month/week/day operations).
- Comprehensive test suite.
- Project setup with `pyproject.toml`, `Makefile`, and development tools.

### Changed
## [0.3.0] - 2026-01-19

### Added
-

### Changed
- Repository improvements: exports, type hints, and CI enhancements (#2).
- None instead of Optional[X]).
- Update dependencies and Python version support (#1).
- Claude.

### Fixed
- Fix version bumping.

## [0.4.0] - 2026-01-19

### Added
- Fix datetime_end_of_day microseconds and add MONTHS_IN_QUARTER constant.

### Changed
- Achieve 100% test coverage (#9).
- Migrate from mypy to ty for type checking (#8).
- Tooling improvements: dependabot, mypy alignment, and doctest.

### Fixed
- Fix documentation issues and end_of_* microseconds consistency.
- Fix datetime handling bugs: httpdate, datetime_to_utc, pretty_date.
- Upgrade urllib3 to 2.6.3 to fix security vulnerabilities (#3).

## [0.4.1] - 2026-01-19

### Added
-

### Changed
- Make GitHub release a draft for manual review (#10).
- Ci: bump actions/download-artifact from 4 to 7 (#4).
- Ci: bump actions/upload-artifact from 4 to 6 (#6).
- Ci: bump actions/checkout from 4 to 6 (#7).
- Ci: bump astral-sh/setup-uv from 5 to 7 (#5).

### Fixed
-

## [0.5.0] - 2026-01-23

### Added
- Docs: add coverage badge to README (#17).
- Add Claude Code GitHub Workflow (#11).

### Changed
- Generate now goes forward or back.
- Chore: update all transitive dependencies (#16).
- Bump requests from 2.32.3 to 2.32.4 (#13).
- Bump filelock from 3.18.0 to 3.20.3 (#14).
- Ci: bump actions/checkout from 4 to 6 (#12).
- Improve README with badges and comparison section.
- Split release workflow to publish PyPI only on release publish.

### Fixed
- Fix httpdate localization.
- Fix validation on until_q in generate-quarters.
- CM: fix mutable results of federal holidays, each caller gets unique data.
- Fix release instructions to link directly to draft release.

## [0.5.1] - 2026-01-23

### Added
- Add Python 3.14 support to CI and package classifiers (#18).

### Changed
- Format.

### Fixed
- Fix generate_weeks.

## [0.5.2] - 2026-01-25

### Added
- Improve code quality: accept Iterable for holidays, add edge case tests, fix import path (#21).

### Changed
-

### Fixed
- Fix age_in_years leap year birthday edge case (#20).
- Improve code quality: simplify is_leap_year, refactor parse_iso8601 regex, and fix exception handling (#19).

## [0.5.3] - 2026-01-25

### Added
-

### Changed
- Improve code quality: optimize workdays_between, unify holidays parameter, expand exports, and enhance docs (#22).

### Fixed
-

## [Unreleased]

### Added
-

### Changed
-

### Fixed
-

## [0.2.4] - 2025-06-05

### Added
- New release process.

### Changed
- Changelog.

### Fixed
-

-

### Fixed
## [0.3.0] - 2026-01-19

### Added
-

### Changed
- Repository improvements: exports, type hints, and CI enhancements (#2).
- None instead of Optional[X]).
- Update dependencies and Python version support (#1).
- Claude.

### Fixed
- Fix version bumping.

## [0.4.0] - 2026-01-19

### Added
- Fix datetime_end_of_day microseconds and add MONTHS_IN_QUARTER constant.

### Changed
- Achieve 100% test coverage (#9).
- Migrate from mypy to ty for type checking (#8).
- Tooling improvements: dependabot, mypy alignment, and doctest.

### Fixed
- Fix documentation issues and end_of_* microseconds consistency.
- Fix datetime handling bugs: httpdate, datetime_to_utc, pretty_date.
- Upgrade urllib3 to 2.6.3 to fix security vulnerabilities (#3).

## [0.4.1] - 2026-01-19

### Added
-

### Changed
- Make GitHub release a draft for manual review (#10).
- Ci: bump actions/download-artifact from 4 to 7 (#4).
- Ci: bump actions/upload-artifact from 4 to 6 (#6).
- Ci: bump actions/checkout from 4 to 6 (#7).
- Ci: bump astral-sh/setup-uv from 5 to 7 (#5).

### Fixed
-

## [0.5.0] - 2026-01-23

### Added
- Docs: add coverage badge to README (#17).
- Add Claude Code GitHub Workflow (#11).

### Changed
- Generate now goes forward or back.
- Chore: update all transitive dependencies (#16).
- Bump requests from 2.32.3 to 2.32.4 (#13).
- Bump filelock from 3.18.0 to 3.20.3 (#14).
- Ci: bump actions/checkout from 4 to 6 (#12).
- Improve README with badges and comparison section.
- Split release workflow to publish PyPI only on release publish.

### Fixed
- Fix httpdate localization.
- Fix validation on until_q in generate-quarters.
- CM: fix mutable results of federal holidays, each caller gets unique data.
- Fix release instructions to link directly to draft release.

## [0.5.1] - 2026-01-23

### Added
- Add Python 3.14 support to CI and package classifiers (#18).

### Changed
- Format.

### Fixed
- Fix generate_weeks.

## [0.5.2] - 2026-01-25

### Added
- Improve code quality: accept Iterable for holidays, add edge case tests, fix import path (#21).

### Changed
-

### Fixed
- Fix age_in_years leap year birthday edge case (#20).
- Improve code quality: simplify is_leap_year, refactor parse_iso8601 regex, and fix exception handling (#19).

## [0.5.3] - 2026-01-25

### Added
-

### Changed
- Improve code quality: optimize workdays_between, unify holidays parameter, expand exports, and enhance docs (#22).

### Fixed
-

## [Unreleased]

### Added
-

### Changed
-

### Fixed
-

## [0.2.4] - 2025-06-05

### Added
- New release process.

### Changed
- Changelog.

### Fixed
-

-
