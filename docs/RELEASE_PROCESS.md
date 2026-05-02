# Release Process

This document describes the release flow implemented by the current `Makefile`
and GitHub Actions workflows.

## Prerequisites

1. **Clean, reviewed working tree**: `make version-*` stages every changed file
   with `git add -A`, commits the version bump, creates a tag, and pushes both
   the branch and tag.
2. **Local quality gate**: run the full check before starting a release:
   ```bash
   make check
   ```
3. **Git remote access**: the version command pushes to `origin`, so make sure
   your branch can push to GitHub.

## Release Workflow

Choose the appropriate version bump based on the release contents:

```bash
# For bug fixes and patches
make version-patch  # 0.2.1 -> 0.2.2

# For new backward-compatible features
make version-minor  # 0.2.1 -> 0.3.0

# For breaking changes
make version-major  # 0.2.1 -> 1.0.0
```

The selected `version-*` target:

- Reads the current version from `pyproject.toml`
- Runs `bump2version --allow-dirty` for the selected bump type
- Updates `CHANGELOG.md` with `make update-changelog VERSION=<new-version>`
- Refreshes `uv.lock`
- Stages all changes with `git add -A`
- Commits the release changes with a `Bump version: <old> -> <new>` message
- Creates a local `v<new-version>` git tag
- Pushes the current branch to `origin`
- Pushes the new tag to `origin`

Pushing the tag starts `.github/workflows/release.yml`, which runs `make check`,
builds and verifies the distribution with `make build-check`, uploads the
artifacts, and creates a **draft** GitHub release containing the built files.

After the draft release exists, review the release notes and artifacts in
GitHub. Publishing that draft release starts `.github/workflows/publish.yml`,
which downloads the release assets and publishes them to PyPI.

## Important Behavior

- There are no `make gh-status`, `make release-draft`, `make release`,
  `make release-patch`, `make release-minor`, or `make release-major` targets.
- `make version-*` is not a local-only preparation step. It commits, tags, and
  pushes.
- `make version-*` does not run `make check` before committing locally. Run
  `make check` yourself before invoking it; the release workflow also runs
  `make check` after the tag is pushed.
- Because `make version-*` uses `git add -A`, review unrelated local changes
  before starting a release.

## Example Workflow

```bash
# 1. Finish code and documentation changes.

# 2. Verify locally.
make check

# 3. Review the working tree so only intended files are present.
git status
git diff

# 4. Bump, commit, tag, and push.
make version-patch

# 5. Wait for the GitHub release workflow to create the draft release.

# 6. Review the draft release on GitHub, then publish it to trigger PyPI.
```

## Manual Operations

### Update Changelog Only

```bash
make update-changelog VERSION=x.y.z
```

### Build and Check Distribution Locally

```bash
make build-check
```

### Show Current Version

```bash
make version
```

## Troubleshooting

### Release Workflow Fails

Fix the issue on the release branch, then decide whether to move the release tag
or create a new version. Do not rerun `make version-*` blindly; it will create
another version bump commit and tag.

### Draft Release Already Exists

If GitHub Actions cannot create the draft release because a release already
exists for the tag, inspect the existing release in GitHub. Delete or update it
only after confirming the tag and uploaded artifacts are the intended release.

### Tag Push Fails

If the tag push fails, inspect local and remote tags before retrying:

```bash
git tag --list 'v*'
git ls-remote --tags origin
```

Only push or recreate a tag after confirming which version should be released.
