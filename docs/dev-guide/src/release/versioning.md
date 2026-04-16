*This chapter is for contributors and maintainers.*

# Versioning

NeuralDrive follows a structured versioning scheme to ensure that users and developers can easily identify the age and feature set of a given image.

## Calendar Versioning (CalVer)

We use a variation of Calendar Versioning (CalVer) for our releases. This reflects the project's nature as a collection of upstream components (Debian, Ollama, WebUI) that change frequently.

The format is: `YYYY.MM.REVISION`
- **YYYY**: The four-digit year of release.
- **MM**: The two-digit month of release.
- **REVISION**: The total number of releases ever made. This number never resets — it always increments, even across year/month boundaries.

Examples: `2026.04.1`, `2026.05.2`, `2027.01.53`

The REVISION serves as a monotonically increasing release counter. Given any two NeuralDrive versions, the one with the higher REVISION is always newer, regardless of the date components.

## Version File

The primary source of truth for the system version is the file `/etc/neuraldrive/version`. This file is written during the build process (by `build.sh`) into `config/includes.chroot/etc/neuraldrive/version` and is used by the TUI, WebUI, and System API to display the version.

## Git Tags

Git tags are the source of truth for determining REVISION numbers. Tags follow the format `vYYYY.MM.REVISION` (e.g., `v2026.04.1`).

Use `scripts/tag-release.sh` to create the next release tag:

```bash
./scripts/tag-release.sh --dry-run   # preview
./scripts/tag-release.sh             # create tag
git push origin v2026.04.1           # push it
```

The script counts all existing `v*` tags and sets REVISION to count + 1.

## Development Builds

Commits on `main` that are not on an exact release tag produce dev versions labeled with the date and short git hash:

```
dev-2026.04.15-a1b2c3d
```

The build system resolves version automatically:
1. `NEURALDRIVE_VERSION` env var (if set explicitly)
2. Exact git tag on HEAD (stripped of `v` prefix)
3. Dev fallback: `dev-YYYY.MM.DD-SHORTHASH`

## Component Versioning

While the appliance has its own version, the individual components are also tracked:
- **Debian Base**: Debian 12 (Bookworm).
- **Ollama**: Tracked via the binary version (e.g., 0.1.32).
- **Open WebUI**: Tracked via the git tag or pip version.

The System API provides an endpoint (`GET /system/status`) that returns the version string.

> **Note**: Major architectural changes that break backward compatibility with older persistence partitions will be signaled by a "Breaking Change" notice in the release notes.
