# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
-

### Changed
-

### Fixed
-

## [0.8.2] - 2026-07-15

### Added
-

### Changed
- Normalize datetime awareness checks (#76).
- Enforce documentation and coverage checks (#75).

### Fixed
- Fix date range boundary handling (#74).

## [0.8.1] - 2026-07-15

### Added
-

### Changed
- Bound federal holiday rules historically (#73).
- Pin GitHub Actions to immutable commits (#72).
- Ci: consolidate quality and version matrix (#71).
- Upgrade development tooling (#70).

### Fixed
-

## [0.8.0] - 2026-07-11

### Added
- Add explicit naive datetime localization (#69).

### Changed
- Expose next occurrence datetime API (#68).
- Improve ambiguous numeric date parsing (#67).
- Ci: bump actions/checkout from 6 to 7 (#64).

### Fixed
-

## [0.7.1] - 2026-07-10

### Added
-

### Changed
-

### Fixed
- Fix PyPI publish artifact dependency (#66).

## [0.7.0] - 2026-07-10

### Added
-

### Changed
- Harden date handling and releases (#65).
- Update dependencies and constrain urllib3 (#63).
- Update development dependencies (#62).
- Make US federal holidays data-driven (#61).
- Extract month and quarter index helpers (#60).
- Tighten README and changelog flow (#59).
- Simplify date boundary helpers (#58).

### Fixed
-

## [0.6.1] - 2026-05-01

### Added
- Add time support to next occurence (#55).
- Add changelog validation to CI (#50).

### Changed
- Preserve datetime calendar parse errors (#57).
- Use top-level dateutils imports (#54).
- Extract DST occurrence normalization (#53).
- Extract inclusive walk helper (#52).
- Normalize changelog and validate headings (#48).
- Handle DST in daily occurrence helper (#47).
- Ci: bump actions/download-artifact from 7 to 8 (#43).
- Ci: bump actions/upload-artifact from 6 to 7 (#44).
- Update locked test dependency: pytest-cov 7.1.0 (#45).
- Bump versions (#42).
- Split parsing/timezone code and tests into modules (#41).

### Fixed
- Fix release process docs (#56).
- Fix historical Juneteenth holiday handling (#51).
- Fix DST fold and changelog fallback (#49).

## [0.6.0] - 2026-02-22

### Added
- Add observed US holidays and improve parse_date errors (#39).

### Changed
- Refactor parsers to raise ParseError (#38).
- Refactor pretty_date and parse_datetime defaults (#37).

### Fixed
-

## [0.5.7] - 2026-02-13

### Added
- Fix doctests, versions, and add better iso support (#36).
- Enable Ruff S/PT/RET/PERF and address findings (#35).

### Changed
- Update dev dependencies and refresh uv.lock (#34).

### Fixed
- Fix pretty_date grammar and validation edge cases (#33).
- Fix dateutils edge-case handling regressions (#32).

## [0.5.6] - 2026-02-09

### Added
- Add doctest CI and parser/coverage fixes (#30).
- Clean up code quality issues: fix comments, simplify logic, add test coverage (#29).

### Changed
- Update dev dependencies to latest versions (#27).

### Fixed
- Fix timezone error behavior and docs (#31).
- Fix date_range limit to account for leap days (#28).

## [0.5.5] - 2026-02-05

### Added
-

### Changed
-

### Fixed
- Fix ISO8601 validation and start defaults (#26).

## [0.5.4] - 2026-02-02

### Added
- Improve edge case handling, add tests, and enhance documentation (#24).
- Improve holiday handling, add locale support to parse_date, achieve 100% coverage (#23).

### Changed
- Sort holidays and speed business days (#25).

### Fixed
-

## [0.5.3] - 2026-01-25

### Added
-

### Changed
- Improve code quality: optimize workdays_between, unify holidays parameter, expand exports, and enhance docs (#22).

### Fixed
-

## [0.5.2] - 2026-01-25

### Added
- Improve code quality: accept Iterable for holidays, add edge case tests, fix import path (#21).

### Changed
-

### Fixed
- Fix age_in_years leap year birthday edge case (#20).
- Improve code quality: simplify is_leap_year, refactor parse_iso8601 regex, and fix exception handling (#19).

## [0.5.1] - 2026-01-23

### Added
- Add Python 3.14 support to CI and package classifiers (#18).

### Changed
- Format.

### Fixed
- Fix generate_weeks.

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

## [0.2.4] - 2025-06-05

### Added
- New release process.

### Changed
- Changelog.

### Fixed
-

## [0.2.3] - 2025-05-31

### Added
-

### Changed
- Testing release process.

### Fixed
-

## [0.2.2] - 2025-05-31

### Added
-

### Changed
-

### Fixed
-

## [0.2.1] - 2025-05-31

### Added
- Initial release of `dateutils-python`.
- Core date/time utilities (UTC, parsing, formatting, timezone, business days, quarter/month/week/day operations).
- Comprehensive test suite.
- Project setup with `pyproject.toml`, `Makefile`, and development tools.

### Changed
-

### Fixed
-
