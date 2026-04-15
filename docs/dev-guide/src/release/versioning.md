*This chapter is for contributors and maintainers.*

# Versioning

NeuralDrive follows a structured versioning scheme to ensure that users and developers can easily identify the age and feature set of a given image.

## Calendar Versioning (CalVer)

We use a variation of Calendar Versioning (CalVer) for our releases. This reflects the project's nature as a collection of upstream components (Debian, Ollama, WebUI) that change frequently.

The format is: `YYYY.MM.Patch`
- **YYYY**: The four-digit year of release.
- **MM**: The two-digit month of release.
- **Patch**: A sequential number for releases within the same month (starting at 0).

Example: `2026.04.1`

## Version File

The primary source of truth for the system version is the file `/etc/neuraldrive/version`. This file is generated during the build process and is used by the TUI, WebUI, and System API to display the version to the user.

## Tagging and Branching

### Development
The `main` branch always contains the latest stable development code. Commits to `main` are built as "Snapshot" releases and labeled with the date and short git hash (e.g., `dev-20260415-a1b2c3d`).

### Release Tags
When a stable release is ready:
1. A new tag is created following the `vYYYY.MM.Patch` format.
2. The GitHub CI pipeline automatically triggers a full production build.
3. The resulting artifacts are attached to a GitHub Release.

## Component Versioning

While the appliance has its own version, the individual components are also tracked:
- **Debian Base**: Debian 12 (Bookworm).
- **Ollama**: Tracked via the binary version (e.g., 0.1.32).
- **Open WebUI**: Tracked via the git tag or pip version.

The System API provides an endpoint (`GET /system/version`) that returns the version strings for all core components.

> **Note**: Major architectural changes that break backward compatibility with older persistence partitions will be signaled by a "Breaking Change" notice in the release notes and potentially a change to the versioning format.

