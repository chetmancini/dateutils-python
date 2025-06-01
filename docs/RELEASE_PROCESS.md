# Release Process

This document describes the improved release process that separates versioning from releasing for better control and review.

## Prerequisites

1. **GitHub CLI**: Install and authenticate with GitHub CLI
   ```bash
   brew install gh
   gh auth login
   ```

2. **Verify Setup**: Check that everything is configured correctly
   ```bash
   make gh-status
   ```

## New Two-Step Workflow

The release process is now separated into two distinct steps for better control:

### Step 1: Version Bump
Choose the appropriate version bump based on your changes:

```bash
# For bug fixes and patches
make version-patch  # 0.2.1 → 0.2.2

# For new features (backward compatible)
make version-minor  # 0.2.1 → 0.3.0

# For breaking changes
make version-major  # 0.2.1 → 1.0.0
```

This will:
- Update version numbers in code
- Update `CHANGELOG.md` with new version entry
- Create git commit and tag locally
- Give you next steps

### Step 2: Review and Release

After version bumping, you have options:

**Option A: Create Draft Release (Recommended)**
```bash
make release-draft
```
This creates a draft release on GitHub that you can review and edit before publishing.

**Option B: Direct Release**
```bash
make release
```
This immediately creates and publishes the release.

**Option C: Manual Review**
1. Edit `CHANGELOG.md` to add proper release notes
2. Review the changes
3. Then run `make release` when ready

## What Each Step Does

### Version Commands (`make version-*`)
- Runs quality checks
- Updates version in `pyproject.toml` and `dateutils/__init__.py`
- Updates `CHANGELOG.md` with new version entry (with placeholders)
- Creates git commit with version bump message
- Creates git tag locally
- **Does NOT push or release anything**

### Release Command (`make release`)
- Verifies you've run a version command first
- Checks that the version isn't already released on GitHub
- Runs comprehensive quality checks
- Builds distribution packages
- Pushes commits and tags to GitHub
- Creates GitHub release with release notes
- Uploads distribution files

### Draft Release Command (`make release-draft`)
- Same as release but creates a draft
- Allows you to review before publishing
- Can be updated/recreated if needed

## Safety Features

- **Prevents double releases**: `make release` will fail gracefully if the version is already released
- **Requires versioning first**: `make release` will fail if no version tag exists locally
- **Quality gates**: All commands run comprehensive checks before proceeding
- **Rollback friendly**: Version bumps are local until you run release commands

## Example Workflow

```bash
# 1. Make your code changes
# ... edit code, add tests, etc ...

# 2. Run quality checks
make check

# 3. Bump version and prepare release
make version-patch

# 4. Review and edit the changelog
# Edit CHANGELOG.md - add proper descriptions under the new version section

# 5. Create draft release for review (optional)
make release-draft

# 6. Review the draft on GitHub, then either:
#    - Edit the draft on GitHub and publish manually, OR
#    - Run the final release command:
make release
```

## Backward Compatibility

The old combined commands still work but are deprecated:

```bash
make release-patch  # Still works, but shows deprecation warning
make release-minor  # Still works, but shows deprecation warning
make release-major  # Still works, but shows deprecation warning
```

These run `version-*` followed by `release` in sequence.

## Release Notes

Release notes are automatically generated from:

1. **Release Template** (`.github/RELEASE_TEMPLATE.md`): Used as base if present
2. **Changelog Extraction**: Relevant sections from `CHANGELOG.md` are automatically included
3. **Fallback**: Auto-generated notes with links to changelog

### Testing Release Notes

```bash
make test-release-notes
```

## Manual Operations

### Check if Version Already Released
```bash
make check-release-exists
```

### Create Release for Existing Tag
```bash
make create-github-release VERSION=x.y.z
```

### Update Changelog Only
```bash
make update-changelog VERSION=x.y.z
```

## Troubleshooting

### "Release already exists" Error
```bash
# Delete the existing release if you need to recreate it
gh release delete vX.Y.Z
make release
```

### "Tag not found" Error
This means you haven't run a version command first:
```bash
make version-patch  # or version-minor/major
make release
```

### Failed Release
Since version bumping and releasing are separate, you can retry releases:
```bash
# Fix any issues, then retry
make release
```

### GitHub CLI Issues
```bash
# Check authentication
make gh-status

# Re-authenticate if needed
gh auth login
```

## GitHub Actions Integration

The repository includes GitHub Actions that automatically:
- Run tests when tags are pushed
- Publish to PyPI after successful release

The Makefile integrates with this by ensuring proper tags and releases are created.

## Migration from Old Workflow

If you were using the old workflow, simply switch to:

**Old:**
```bash
make release-patch
```

**New:**
```bash
make version-patch
# Review CHANGELOG.md
make release
```

The new workflow gives you more control and the ability to review changes before publishing.
