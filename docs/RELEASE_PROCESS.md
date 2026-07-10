# Release Process

This document describes the release flow implemented by the current `Makefile`
and GitHub Actions workflows.

## Prerequisites

1. **Clean, reviewed working tree**: `make version-*` refuses to start when
   tracked or untracked changes are present.
2. **Local quality gate**: the target runs the full check before committing;
   you can also run it before starting a release:
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
- Runs `bump2version` for the selected bump type
- Updates `CHANGELOG.md` with `make update-changelog VERSION=<new-version>`
- Refreshes `uv.lock`
- Validates that `v<new-version>` matches the version in `pyproject.toml`
- Runs `make check` before creating the release commit
- Stages only `.bumpversion.cfg`, `pyproject.toml`, `CHANGELOG.md`, and `uv.lock`
- Commits the release changes with a `Bump version: <old> -> <new>` message
- Creates a local `v<new-version>` git tag
- Atomically pushes the current branch and new tag to `origin`

Pushing the tag starts `.github/workflows/release.yml`, which runs `make check`,
revalidates the tag, builds and verifies the distribution with
`make build-check`, installs the wheel in an isolated environment, smoke-tests
its public API and typing marker, uploads the artifacts, and creates a **draft**
GitHub release containing the built files.

After the draft release exists, review the release notes and artifacts in
GitHub. Publishing that draft release starts `.github/workflows/publish.yml`,
which downloads the release assets and publishes them to PyPI.

## Important Behavior

- There are no `make gh-status`, `make release-draft`, `make release`,
  `make release-patch`, `make release-minor`, or `make release-major` targets.
- `make version-*` is not a local-only preparation step. It commits, tags, and
  pushes.
- `make version-*` runs `make check` before committing locally, and the release
  workflow repeats it after the tag is pushed.
- The version command fails before changing files if the working tree is dirty.
- Branch and tag updates are sent with one atomic push, so GitHub accepts both
  refs or neither ref.

## Example Workflow

```bash
# 1. Finish code and documentation changes.

# 2. Verify locally (the release target repeats this gate).
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
